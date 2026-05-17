from io import BytesIO
from typing import Any

from sqlalchemy.orm import Session

from app.services.shortlist import build_shortlist_decision_matrix


def _fmt_number(value: float | int | None, digits: int = 0) -> str:
    if value is None:
        return "-"
    return f"{float(value):,.{digits}f}"


def _fmt_money(value: float | int | None) -> str:
    if value is None:
        return "-"
    value_float = float(value)
    if abs(value_float) >= 1_000_000_000:
        return f"USD {value_float / 1_000_000_000:,.2f}B"
    if abs(value_float) >= 1_000_000:
        return f"USD {value_float / 1_000_000:,.1f}M"
    return f"USD {value_float:,.0f}"


def _status_for_confidence(label: str, data_gap_count: int) -> str:
    if data_gap_count >= 3 or label.lower() in {"low", "unknown"}:
        return "critical_gap"
    if data_gap_count > 0 or label.lower() == "medium":
        return "needs_validation"
    return "available"


def _candidate_validation_items(candidate: dict[str, Any]) -> list[dict[str, str]]:
    data_status = _status_for_confidence(candidate["data_confidence_label"], int(candidate["data_gap_count"]))
    port_status = "needs_validation" if candidate["nearest_port_name"] else "critical_gap"
    capex_status = "needs_validation" if candidate["estimated_lcom_usd_ton"] is not None else "critical_gap"
    return [
        {
            "category": "Technical",
            "item": "Site, unit, capacity, stack, and operating profile",
            "current_basis": f"{candidate['capacity_mw'] or 0:g} MW public/benchmark site aggregate",
            "required_evidence": "PLN unit register, CEMS/stack data, operating hours, capacity factor, and stack configuration.",
            "status": data_status,
            "priority": "high",
        },
        {
            "category": "Economics",
            "item": "CAPEX/OPEX and LCOM calibration",
            "current_basis": f"Screening LCOM {_fmt_number(candidate['estimated_lcom_usd_ton'], 0)} USD/t",
            "required_evidence": "Vendor quotation or Pre-FEED cost estimate for capture, electrolyzer, methanol plant, storage, grid, and logistics.",
            "status": capex_status,
            "priority": "high",
        },
        {
            "category": "Logistics",
            "item": "Port and export handling route",
            "current_basis": f"{candidate['nearest_port_name'] or 'Unconfirmed port'} at {_fmt_number(candidate['nearest_port_distance_km'], 1)} km straight-line proxy",
            "required_evidence": "Terminal operator confirmation, route distance, methanol handling/storage capability, export permits, and route cost.",
            "status": port_status,
            "priority": "high",
        },
        {
            "category": "Power and H2",
            "item": "Electrolyzer and electricity supply readiness",
            "current_basis": f"{_fmt_number(candidate['electrolyzer_required_mw'], 1)} MW electrolyzer screening scale",
            "required_evidence": "Grid connection study, renewable electricity source, water supply, electrolyzer layout, and H2 storage assumptions.",
            "status": "needs_validation",
            "priority": "high",
        },
        {
            "category": "Commercial and MRV",
            "item": "Offtake, MRV, and carbon accounting",
            "current_basis": f"{_fmt_number(candidate['methanol_tpy'], 0)} t/y e-methanol screening output",
            "required_evidence": "Offtake term sheet, MRV methodology, carbon intensity basis, certification path, and credit eligibility review.",
            "status": "needs_validation",
            "priority": "medium",
        },
    ]


def _pack_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    breakdown = candidate["score_breakdown"]
    return {
        "validation_rank": candidate["shortlist_rank"],
        "site_name": candidate["site_name"],
        "plant_id": candidate["plant_id"],
        "scenario_id": candidate["scenario_id"],
        "province": candidate["province"],
        "city": candidate["city"],
        "capacity_mw": candidate["capacity_mw"],
        "final_score": breakdown["final_score"],
        "economics_score": breakdown["economics_score"],
        "logistics_score": breakdown["logistics_score"],
        "confidence_score": breakdown["confidence_score"],
        "captured_co2_tpy": candidate["captured_co2_tpy"],
        "methanol_tpy": candidate["methanol_tpy"],
        "h2_required_tpy": candidate["h2_required_tpy"],
        "electrolyzer_required_mw": candidate["electrolyzer_required_mw"],
        "gross_revenue_usd_per_year": candidate["gross_revenue_usd_per_year"],
        "estimated_lcom_usd_ton": candidate["estimated_lcom_usd_ton"],
        "nearest_port_name": candidate["nearest_port_name"],
        "nearest_port_distance_km": candidate["nearest_port_distance_km"],
        "data_confidence_label": candidate["data_confidence_label"],
        "data_gap_count": candidate["data_gap_count"],
        "key_bottleneck": candidate["key_bottleneck"],
        "recommendation": candidate["recommendation"],
        "why_shortlisted": candidate["decision_rationale"],
        "validation_items": _candidate_validation_items(candidate),
        "next_actions": candidate["next_actions"],
    }


def _leader(candidates: list[dict[str, Any]], key: str, *, lower_is_better: bool = False) -> str | None:
    values = [candidate for candidate in candidates if candidate.get(key) is not None]
    if not values:
        return None
    selected = min(values, key=lambda item: float(item[key])) if lower_is_better else max(values, key=lambda item: float(item[key]))
    return str(selected["site_name"])


def _comparison_axes(candidates: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    return [
        {
            "axis": "Scale / CO2 capture",
            "leader": _leader(candidates, "captured_co2_tpy"),
            "notes": "Largest captured CO2 volume gives the strongest scale signal for pilot-to-scale screening.",
        },
        {
            "axis": "E-methanol output",
            "leader": _leader(candidates, "methanol_tpy"),
            "notes": "Higher output improves offtake relevance but increases hydrogen, power, water, and logistics requirements.",
        },
        {
            "axis": "Indicative LCOM",
            "leader": _leader(candidates, "estimated_lcom_usd_ton", lower_is_better=True),
            "notes": "Current values are benchmark-based and must be recalibrated with vendor CAPEX/OPEX.",
        },
        {
            "axis": "Port logistics",
            "leader": max(candidates, key=lambda item: float(item["logistics_score"]))["site_name"] if candidates else None,
            "notes": "Combines nearest commercial port readiness and straight-line distance proxy.",
        },
        {
            "axis": "Data confidence",
            "leader": max(candidates, key=lambda item: float(item["confidence_score"]))["site_name"] if candidates else None,
            "notes": "Confidence reflects current source quality and data-gap penalties.",
        },
    ]


def _committee_memo(candidates: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    lead = candidates[0]["site_name"] if candidates else None
    top3_lines = [
        (
            f"#{candidate['validation_rank']} {candidate['site_name']}: score {candidate['final_score']:.3f}, "
            f"{_fmt_number(candidate['methanol_tpy'], 0)} t/y e-methanol, nearest port {candidate['nearest_port_name'] or '-'}."
        )
        for candidate in candidates
    ]
    return {
        "title": "MECH WIZ Top 3 Validation Committee Memo",
        "recommendation": f"Advance {lead or 'the Top 3 shortlist'} into PLN/site/port/vendor validation before selecting a single pilot.",
        "executive_summary": (
            "The Top 3 shortlist is suitable for validation discussion, but not yet for final investment approval. "
            "The current ranking is based on deterministic screening outputs, benchmark economics, port proximity/readiness, "
            "and data-confidence penalties."
        ),
        "decision_ask": (
            "Approve a focused validation sprint covering site data, stack/CEMS, CAPEX/OPEX quotations, port handling, "
            "offtake, power/H2 supply, MRV, and decision blockers for the Top 3 candidates."
        ),
        "top3_summary": top3_lines,
        "decision_questions": [
            "Which candidate has PLN-confirmed site and stack data strong enough for Pre-FEED?",
            "Can the nearest feasible port handle methanol storage, safety, and export requirements?",
            "Which candidate remains attractive after vendor CAPEX/OPEX replaces benchmark assumptions?",
            "Which offtake or Singapore export route is commercially credible for the expected methanol volume?",
            "Which site has the fewest land, grid, water, permit, and MRV blockers?",
        ],
        "no_go_triggers": [
            "PLN/site data materially contradicts public capacity, coordinate, or operating assumptions.",
            "Port or route validation shows methanol handling/export is impractical or uneconomic.",
            "Vendor CAPEX/OPEX increases LCOM beyond committee threshold.",
            "Power, water, land, permit, or MRV constraints cannot be resolved within the target timeline.",
        ],
        "caveats": [
            "All figures remain screening/pre-validation outputs.",
            "Port distance is a straight-line proxy, not a confirmed transport route.",
            "Vendor quotation and PLN-confirmed data should replace public/benchmark assumptions before investment decision.",
            f"Top 3 portfolio screening revenue is {_fmt_money(summary['total_gross_revenue_usd_per_year'])}, not contracted revenue.",
        ],
    }


def build_top3_validation_pack(db: Session, scheme: str = "align", limit: int = 3) -> dict[str, Any]:
    matrix = build_shortlist_decision_matrix(db, scheme=scheme, top_n=max(limit, 5))
    shortlisted = matrix["candidates"][:limit]
    packed_candidates = [_pack_candidate(candidate) for candidate in shortlisted]
    lcom_values = [
        float(candidate["estimated_lcom_usd_ton"])
        for candidate in packed_candidates
        if candidate["estimated_lcom_usd_ton"] is not None
    ]
    high_priority_evidence_count = sum(
        1
        for candidate in packed_candidates
        for item in candidate["validation_items"]
        if item["priority"] == "high" and item["status"] != "available"
    )
    summary = {
        "candidate_count": len(packed_candidates),
        "lead_candidate": packed_candidates[0]["site_name"] if packed_candidates else None,
        "total_captured_co2_tpy": round(sum(float(candidate["captured_co2_tpy"] or 0) for candidate in packed_candidates), 2),
        "total_methanol_tpy": round(sum(float(candidate["methanol_tpy"] or 0) for candidate in packed_candidates), 2),
        "total_gross_revenue_usd_per_year": round(
            sum(float(candidate["gross_revenue_usd_per_year"] or 0) for candidate in packed_candidates),
            2,
        ),
        "average_lcom_usd_ton": round(sum(lcom_values) / len(lcom_values), 2) if lcom_values else None,
        "high_priority_evidence_count": high_priority_evidence_count,
    }
    warnings = [
        "This validation pack is a decision-support artifact, not an approval or bankable feasibility study.",
        "All candidate evidence items must be replaced by PLN, site, vendor, terminal, offtake, and MRV confirmations.",
        "The committee memo is generated deterministically from stored backend outputs and does not use LLM calculations.",
    ]
    return {
        "scheme": scheme,
        "limit": limit,
        "summary": summary,
        "candidates": packed_candidates,
        "comparison_axes": _comparison_axes(packed_candidates),
        "committee_memo": _committee_memo(packed_candidates, summary),
        "warnings": warnings,
    }


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _render_minimal_pdf(pack: dict[str, Any]) -> bytes:
    memo = pack["committee_memo"]
    summary = pack["summary"]
    lines = [
        memo["title"],
        memo["recommendation"],
        f"Lead candidate: {summary['lead_candidate'] or '-'}",
        f"Top 3 methanol: {_fmt_number(summary['total_methanol_tpy'], 0)} t/y",
        f"Top 3 captured CO2: {_fmt_number(summary['total_captured_co2_tpy'], 0)} t/y",
        f"Revenue benchmark: {_fmt_money(summary['total_gross_revenue_usd_per_year'])}",
        "Top 3 candidates:",
        *[
            f"#{candidate['validation_rank']} {candidate['site_name']} - score {candidate['final_score']:.3f}, port {candidate['nearest_port_name'] or '-'}"
            for candidate in pack["candidates"]
        ],
        "Decision questions:",
        *memo["decision_questions"],
        "No-go triggers:",
        *memo["no_go_triggers"],
        "Caveats:",
        *memo["caveats"],
    ]
    text_ops = ["BT", "/F1 9 Tf", "42 800 Td", "12 TL"]
    for line in lines[:52]:
        text_ops.append(f"({_pdf_escape(line[:115])}) Tj")
        text_ops.append("T*")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _render_reportlab_pdf(pack: dict[str, Any]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="MECH WIZ Top 3 Validation Committee Memo",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MemoTitle", parent=styles["Title"], fontSize=17, leading=21, spaceAfter=8))
    styles.add(ParagraphStyle(name="MemoHeading", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=8))
    styles.add(ParagraphStyle(name="MemoBody", parent=styles["BodyText"], fontSize=8.6, leading=11))

    story: list[Any] = []
    memo = pack["committee_memo"]
    summary = pack["summary"]
    story.append(Paragraph(memo["title"], styles["MemoTitle"]))
    story.append(Paragraph(memo["recommendation"], styles["MemoBody"]))
    story.append(Spacer(1, 6))

    kpi_table = Table(
        [
            ["Lead", summary["lead_candidate"] or "-", "Top 3 methanol", f"{_fmt_number(summary['total_methanol_tpy'], 0)} t/y"],
            ["Captured CO2", f"{_fmt_number(summary['total_captured_co2_tpy'], 0)} t/y", "Revenue benchmark", _fmt_money(summary["total_gross_revenue_usd_per_year"])],
            ["Avg LCOM", f"{_fmt_number(summary['average_lcom_usd_ton'], 0)} USD/t", "High-priority evidence gaps", str(summary["high_priority_evidence_count"])],
        ],
        colWidths=[33 * mm, 50 * mm, 38 * mm, 52 * mm],
    )
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dff6f2")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9aa9b8")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
            ]
        )
    )
    story.append(kpi_table)

    story.append(Paragraph("Executive Summary", styles["MemoHeading"]))
    story.append(Paragraph(memo["executive_summary"], styles["MemoBody"]))
    story.append(Paragraph("Decision Ask", styles["MemoHeading"]))
    story.append(Paragraph(memo["decision_ask"], styles["MemoBody"]))

    story.append(Paragraph("Top 3 Candidates", styles["MemoHeading"]))
    top3_rows = [["Rank", "Candidate", "Score", "Methanol", "Port", "LCOM"]]
    for candidate in pack["candidates"]:
        top3_rows.append(
            [
                f"#{candidate['validation_rank']}",
                candidate["site_name"],
                f"{candidate['final_score']:.3f}",
                f"{_fmt_number(candidate['methanol_tpy'], 0)} t/y",
                f"{candidate['nearest_port_name'] or '-'} ({_fmt_number(candidate['nearest_port_distance_km'], 1)} km)",
                f"{_fmt_number(candidate['estimated_lcom_usd_ton'], 0)} USD/t",
            ]
        )
    top3_table = Table(top3_rows, colWidths=[13 * mm, 38 * mm, 18 * mm, 34 * mm, 49 * mm, 27 * mm])
    top3_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f1f33")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9aa9b8")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(top3_table)

    story.append(Paragraph("Decision Questions", styles["MemoHeading"]))
    for question in memo["decision_questions"]:
        story.append(Paragraph(f"- {question}", styles["MemoBody"]))

    story.append(Paragraph("No-Go Triggers", styles["MemoHeading"]))
    for trigger in memo["no_go_triggers"]:
        story.append(Paragraph(f"- {trigger}", styles["MemoBody"]))

    story.append(Paragraph("Caveats", styles["MemoHeading"]))
    for caveat in memo["caveats"]:
        story.append(Paragraph(f"- {caveat}", styles["MemoBody"]))

    doc.build(story)
    return buffer.getvalue()


def render_validation_pack_pdf(pack: dict[str, Any]) -> bytes:
    try:
        return _render_reportlab_pdf(pack)
    except ModuleNotFoundError:
        return _render_minimal_pdf(pack)
