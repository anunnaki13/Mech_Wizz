import json
from typing import Any, Protocol

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import BusinessScenario, Document, LlmInsight, Plant, ScenarioResult, SensitivityResult
from app.services.data_quality import build_data_quality_summary
from app.services.investor_case import build_investor_case
from app.services.prefeed import get_package_or_raise
from app.services.prefeed_decision import build_prefeed_decision_dashboard


INSIGHT_TYPES = {
    "executive_summary",
    "data_gap_explanation",
    "investor_memo",
    "sensitivity_explanation",
    "document_qa",
    "prefeed_committee_brief",
}

CALCULATION_AUTHORITY_RULES = """Rules:
- Use only the supplied context.
- Do not invent numbers.
- Do not recalculate IRR, NPV, LCOM, payback, scoring, sensitivity, CO2, H2, or methanol outputs.
- Clearly separate actual data, assumptions, confidence, and data gaps.
- If a required number is missing or null, say it is not calculated from current data.
- Write concise professional Indonesian for PLN NP management, partners, and investors.
"""


class LlmInputError(ValueError):
    pass


class LlmProviderError(RuntimeError):
    def __init__(self, message: str, insight: LlmInsight, status_code: int = 503):
        super().__init__(message)
        self.insight = insight
        self.status_code = status_code


class OpenRouterTransport(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> httpx.Response:
        pass


def _json_dumps(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, default=str)


def _truncate_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}\n\n[Context truncated to {max_chars} characters for model safety.]"


def _latest_scenario_result(db: Session, scenario_id: str) -> ScenarioResult | None:
    return db.scalar(
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.created_at.desc(), ScenarioResult.id.desc())
    )


def _latest_sensitivity(db: Session, scenario_id: str) -> list[dict[str, Any]]:
    records = list(
        db.scalars(
            select(SensitivityResult)
            .where(SensitivityResult.scenario_id == scenario_id)
            .order_by(SensitivityResult.created_at.desc(), SensitivityResult.impact_score.desc())
        )
    )
    if not records:
        return []
    latest_run_id = records[0].run_id
    latest_records = [record for record in records if record.run_id == latest_run_id]
    return [
        {
            "variable_name": record.variable_name,
            "base_input_value": record.base_input_value,
            "low_input_value": record.low_input_value,
            "high_input_value": record.high_input_value,
            "base_irr": record.base_irr,
            "low_irr": record.low_irr,
            "high_irr": record.high_irr,
            "base_npv_usd": record.base_npv_usd,
            "low_npv_usd": record.low_npv_usd,
            "high_npv_usd": record.high_npv_usd,
            "base_lcom_usd_per_ton": record.base_lcom_usd_per_ton,
            "low_lcom_usd_per_ton": record.low_lcom_usd_per_ton,
            "high_lcom_usd_per_ton": record.high_lcom_usd_per_ton,
            "impact_score": record.impact_score,
            "confidence_level": record.confidence_level,
            "missing_inputs": record.missing_inputs,
            "warnings": record.warnings,
        }
        for record in latest_records
    ]


def _data_quality_payload(db: Session, plant_id: str, scenario_id: str | None) -> dict[str, Any]:
    summary = build_data_quality_summary(db, plant_id=plant_id, scenario_id=scenario_id)
    gaps = [
        {
            "source_module": gap.source_module,
            "missing_data_name": gap.missing_data_name,
            "impact_level": gap.impact_level,
            "priority_level": gap.priority_level,
            "recommendation": gap.recommendation,
            "status": gap.status,
        }
        for gap in summary["gaps"]
    ]
    return {
        "plant_id": summary["plant_id"],
        "scenario_id": summary["scenario_id"],
        "input_status": summary["input_status"],
        "output_confidence": summary["output_confidence"],
        "gaps": gaps,
    }


def _scenario_context(db: Session, scenario_id: str) -> tuple[Plant, BusinessScenario, dict[str, Any]]:
    scenario = db.get(BusinessScenario, scenario_id)
    if scenario is None:
        raise LlmInputError("Scenario not found")
    plant = db.get(Plant, scenario.plant_id)
    if plant is None:
        raise LlmInputError("Plant not found")
    result = _latest_scenario_result(db, scenario.id)
    investor_case = build_investor_case(db, plant_id=plant.id, scenario_id=scenario.id)
    data_quality = _data_quality_payload(db, plant.id, scenario.id)
    context = {
        "plant": investor_case["plant"],
        "scenario": investor_case["scenario"],
        "actual_data": {
            "plant": investor_case["plant"],
            "latest_scenario_result": {
                "id": result.id,
                "total_co2_ton_per_year": result.total_co2_ton_per_year,
                "captured_co2_ton_per_year": result.captured_co2_ton_per_year,
                "methanol_ton_per_year": result.methanol_ton_per_year,
                "h2_required_ton_per_year": result.h2_required_ton_per_year,
                "irr": result.irr,
                "npv_usd": result.npv_usd,
                "lcom_usd_per_ton": result.lcom_usd_per_ton,
                "payback_years": result.payback_years,
                "confidence_level": result.confidence_level,
                "missing_inputs": result.missing_inputs,
            }
            if result
            else None,
        },
        "assumptions": {
            "scenario": investor_case["scenario"],
            "capex_structure": investor_case["capex_structure"],
            "revenue_mix": investor_case["revenue_mix"],
        },
        "confidence": {
            "investor_case": investor_case["confidence_level"],
            "data_quality": data_quality["output_confidence"],
        },
        "data_gaps": data_quality["gaps"],
        "investor_case": investor_case,
    }
    return plant, scenario, context


def build_prompt(
    db: Session,
    insight_type: str,
    *,
    scenario_id: str | None = None,
    plant_id: str | None = None,
    package_id: str | None = None,
    document_id: str | None = None,
    question: str | None = None,
    max_context_chars: int | None = None,
) -> tuple[str, str | None, str | None, str | None]:
    if insight_type not in INSIGHT_TYPES:
        raise LlmInputError("Unsupported insight type")
    settings = get_settings()
    max_chars = max_context_chars or settings.llm_max_context_chars

    resolved_plant_id = plant_id
    resolved_scenario_id = scenario_id
    resolved_document_id = document_id

    if insight_type in {"executive_summary", "investor_memo", "sensitivity_explanation"}:
        if scenario_id is None:
            raise LlmInputError("scenario_id is required")
        plant, scenario, context = _scenario_context(db, scenario_id)
        resolved_plant_id = plant.id
        resolved_scenario_id = scenario.id
        if insight_type == "sensitivity_explanation":
            context["sensitivity_results"] = _latest_sensitivity(db, scenario.id)
    elif insight_type == "data_gap_explanation":
        if plant_id is None:
            raise LlmInputError("plant_id is required")
        plant = db.get(Plant, plant_id)
        if plant is None:
            raise LlmInputError("Plant not found")
        context = {
            "plant": {
                "id": plant.id,
                "plant_name": plant.plant_name,
                "unit_name": plant.unit_name,
                "data_status": plant.data_status,
                "confidence_level": plant.confidence_level,
            },
            "data_quality": _data_quality_payload(db, plant.id, scenario_id),
        }
        resolved_plant_id = plant.id
        resolved_scenario_id = scenario_id
    elif insight_type == "prefeed_committee_brief":
        if package_id is None:
            raise LlmInputError("package_id is required")
        try:
            package = get_package_or_raise(db, package_id)
        except ValueError as exc:
            raise LlmInputError(str(exc)) from exc
        plant = db.get(Plant, package.plant_id)
        if plant is None:
            raise LlmInputError("Plant not found")
        dashboard = jsonable_encoder(build_prefeed_decision_dashboard(db, package.id))
        context = {
            "plant": {
                "id": plant.id,
                "plant_name": plant.plant_name,
                "unit_name": plant.unit_name,
                "province": plant.province,
                "data_status": plant.data_status,
                "confidence_level": plant.confidence_level,
            },
            "pre_feed_package": {
                "id": package.id,
                "package_name": package.package_name,
                "package_status": package.package_status,
                "version_label": package.version_label,
                "data_status": package.data_status,
                "confidence_level": package.confidence_level,
            },
            "actual_data": {
                "decision_dashboard": dashboard,
            },
            "assumptions": {
                "scenario_ready_cost_assumptions": dashboard.get("cost_summary", {}).get("scenario_ready_assumptions"),
                "scenario_ready_market_assumptions": dashboard.get("offtake_summary", {}).get(
                    "scenario_ready_assumptions"
                ),
            },
            "confidence": {
                "package": package.confidence_level,
                "risk_summary": dashboard.get("risk_summary", {}),
                "decision_gate_summary": dashboard.get("decision_gate_summary", {}),
            },
            "data_gaps": {
                "package_gaps": dashboard.get("package_gaps", []),
                "offtake_gaps": dashboard.get("offtake_gaps", []),
                "mrv_gaps": dashboard.get("mrv_gaps", []),
                "blockers": dashboard.get("blockers", []),
                "next_actions": dashboard.get("next_actions", []),
                "warnings": dashboard.get("warnings", []),
            },
        }
        resolved_plant_id = plant.id
        resolved_scenario_id = package.scenario_id
    else:
        if document_id is None:
            raise LlmInputError("document_id is required")
        if not question:
            raise LlmInputError("question is required")
        document = db.get(Document, document_id)
        if document is None:
            raise LlmInputError("Document not found")
        if not document.extracted_text:
            raise LlmInputError("Document text must be extracted before Q&A")
        context = {
            "document": {
                "id": document.id,
                "filename": document.filename,
                "document_category": document.document_category,
                "extraction_status": document.extraction_status,
            },
            "question": question,
            "extracted_text": document.extracted_text,
        }
        resolved_plant_id = document.plant_id
        resolved_scenario_id = document.scenario_id
        resolved_document_id = document.id

    context_text = _truncate_text(_json_dumps(context), max_chars)
    prompt_by_type = {
        "executive_summary": "Write an executive summary for PLN NP management and potential investors.",
        "data_gap_explanation": "Explain the current data gaps, impact, priority, and recommended next actions.",
        "investor_memo": "Write a structured investor memo with thesis, selected site rationale, economics, scheme, risk, confidence, and next actions.",
        "sensitivity_explanation": "Explain which variables most affect IRR, NPV, and LCOM using only the sensitivity result values.",
        "document_qa": "Answer the user's document question using only the extracted document text and supplied context.",
        "prefeed_committee_brief": "Write a Pre-FEED investment committee brief in Indonesian with recommendation, readiness, economics, risks, blockers, and next actions.",
    }
    prompt = f"""{prompt_by_type[insight_type]}

{CALCULATION_AUTHORITY_RULES}

Context:
{context_text}
"""
    return prompt, resolved_plant_id, resolved_scenario_id, resolved_document_id


def _create_insight(
    db: Session,
    *,
    plant_id: str | None,
    scenario_id: str | None,
    document_id: str | None,
    insight_type: str,
    model_name: str,
    prompt: str,
) -> LlmInsight:
    record = LlmInsight(
        plant_id=plant_id,
        scenario_id=scenario_id,
        document_id=document_id,
        insight_type=insight_type,
        model_name=model_name,
        prompt=prompt,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _mark_failed(db: Session, record: LlmInsight, message: str) -> LlmInsight:
    record.status = "failed"
    record.error_message = message
    db.commit()
    db.refresh(record)
    return record


def _mark_completed(db: Session, record: LlmInsight, payload: dict[str, Any], requested_model: str) -> LlmInsight:
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not choices:
        raise ValueError("OpenRouter response did not include choices")
    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("OpenRouter response did not include response content")
    record.status = "completed"
    record.response_text = content.strip()
    record.error_message = None
    record.provider_response_id = payload.get("id")
    record.model_name = payload.get("model") or requested_model
    record.usage = payload.get("usage")
    db.commit()
    db.refresh(record)
    return record


def generate_insight(
    db: Session,
    insight_type: str,
    *,
    scenario_id: str | None = None,
    plant_id: str | None = None,
    package_id: str | None = None,
    document_id: str | None = None,
    question: str | None = None,
    model_name: str | None = None,
    api_key: str | None = None,
    transport: OpenRouterTransport | None = None,
) -> LlmInsight:
    settings = get_settings()
    resolved_model = model_name or settings.openrouter_model
    prompt, resolved_plant_id, resolved_scenario_id, resolved_document_id = build_prompt(
        db,
        insight_type,
        scenario_id=scenario_id,
        plant_id=plant_id,
        package_id=package_id,
        document_id=document_id,
        question=question,
        max_context_chars=settings.llm_max_context_chars,
    )
    record = _create_insight(
        db,
        plant_id=resolved_plant_id,
        scenario_id=resolved_scenario_id,
        document_id=resolved_document_id,
        insight_type=insight_type,
        model_name=resolved_model,
        prompt=prompt,
    )
    resolved_api_key = (api_key if api_key is not None else settings.openrouter_api_key) or ""
    if not resolved_api_key.strip():
        failed = _mark_failed(db, record, "OpenRouter API key is not configured")
        raise LlmProviderError("OpenRouter API key is not configured", failed, status_code=503)

    payload = {
        "model": resolved_model,
        "messages": [
            {
                "role": "system",
                "content": "You are MECH WIZ's narrative assistant. You explain backend-calculated facts and never create source-of-record numbers.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
        "metadata": {"app": "mech_wiz", "insight_type": insight_type},
    }
    headers = {
        "Authorization": f"Bearer {resolved_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-OpenRouter-Title": settings.openrouter_app_name,
    }
    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"

    try:
        if transport is None:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload, timeout=45.0)
        else:
            response = transport.post(url, headers=headers, json=payload, timeout=45.0)
        response_payload = response.json()
        if response.status_code >= 400:
            detail = response_payload.get("error", {}).get("message", response.text)
            failed = _mark_failed(db, record, f"OpenRouter request failed: {detail}")
            raise LlmProviderError(str(failed.error_message), failed, status_code=response.status_code)
        return _mark_completed(db, record, response_payload, requested_model=resolved_model)
    except LlmProviderError:
        raise
    except Exception as exc:
        failed = _mark_failed(db, record, f"OpenRouter generation failed: {exc}")
        raise LlmProviderError(str(failed.error_message), failed, status_code=502) from exc


def list_insights(
    db: Session,
    *,
    scenario_id: str | None = None,
    plant_id: str | None = None,
    document_id: str | None = None,
    insight_type: str | None = None,
) -> list[LlmInsight]:
    query = select(LlmInsight)
    if scenario_id:
        query = query.where(LlmInsight.scenario_id == scenario_id)
    if plant_id:
        query = query.where(LlmInsight.plant_id == plant_id)
    if document_id:
        query = query.where(LlmInsight.document_id == document_id)
    if insight_type:
        query = query.where(LlmInsight.insight_type == insight_type)
    return list(db.scalars(query.order_by(LlmInsight.created_at.desc(), LlmInsight.id.desc())))
