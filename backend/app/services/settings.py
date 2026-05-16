from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ApplicationSetting


OPENROUTER_SETTING_KEY = "openrouter_provider"

DEFAULT_SETTINGS: list[dict[str, Any]] = [
    {
        "key": "default_financial_assumptions",
        "category": "default_assumptions",
        "value": {
            "methanol_price_usd_per_ton": 1250,
            "hydrogen_price_usd_per_kg": 3.0,
            "electricity_price_usd_per_kwh": 0.06,
            "carbon_credit_price_idr_per_ton": 58800,
            "exchange_rate_idr_usd": 17500,
            "discount_rate": 0.10,
            "tax_rate": 0.22,
            "opex_percent_capex": 0.04,
        },
        "data_status": "benchmark",
        "confidence_level": "low",
    },
    {
        "key": "scoring_weights",
        "category": "scoring_weights",
        "value": {
            "composite": {"opportunity": 0.45, "readiness": 0.35, "confidence": 0.20},
            "heatmap": {"opportunity": 0.45, "readiness": 0.25, "economic_return": 0.20, "confidence": 0.10},
        },
        "data_status": "benchmark",
        "confidence_level": "medium",
    },
]


class SettingInputError(ValueError):
    pass


def _masked_secret(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return f"{value[:2]}***"
    return f"{value[:4]}...{value[-4:]}"


def _openrouter_defaults() -> dict[str, str | None]:
    settings = get_settings()
    return {
        "api_key": settings.openrouter_api_key,
        "base_url": settings.openrouter_base_url,
        "model": settings.openrouter_model,
        "site_url": settings.openrouter_site_url,
        "app_name": settings.openrouter_app_name,
    }


def _string_or_default(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def seed_default_settings(db: Session) -> list[ApplicationSetting]:
    records: list[ApplicationSetting] = []
    for row in DEFAULT_SETTINGS:
        setting = db.scalar(select(ApplicationSetting).where(ApplicationSetting.key == row["key"]))
        if setting is None:
            setting = ApplicationSetting(**row)
            db.add(setting)
        else:
            for field in ["category", "value", "data_status", "confidence_level"]:
                setattr(setting, field, row[field])
        records.append(setting)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def list_settings(db: Session, category: str | None = None) -> list[ApplicationSetting]:
    query = select(ApplicationSetting)
    if category:
        query = query.where(ApplicationSetting.category == category)
    query = query.where(ApplicationSetting.key != OPENROUTER_SETTING_KEY)
    return list(db.scalars(query.order_by(ApplicationSetting.category, ApplicationSetting.key)))


def get_setting(db: Session, key: str) -> ApplicationSetting | None:
    return db.scalar(select(ApplicationSetting).where(ApplicationSetting.key == key))


def validate_setting_value(key: str, value: dict[str, Any]) -> None:
    if key == "scoring_weights":
        composite = value.get("composite")
        heatmap = value.get("heatmap")
        if not isinstance(composite, dict) or not isinstance(heatmap, dict):
            raise SettingInputError("scoring_weights requires composite and heatmap objects")
        for group_name, group in [("composite", composite), ("heatmap", heatmap)]:
            if not group or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in group.values()):
                raise SettingInputError(f"{group_name} weights must be numeric")
            total = sum(float(item) for item in group.values())
            if abs(total - 1.0) > 0.001:
                raise SettingInputError(f"{group_name} weights must sum to 1.0")
    if key == "default_financial_assumptions":
        if not value:
            raise SettingInputError("default_financial_assumptions cannot be empty")
        for item in value.values():
            if not isinstance(item, (int, float)) or isinstance(item, bool) or item < 0:
                raise SettingInputError("default financial assumptions must be non-negative numbers")
    if key == OPENROUTER_SETTING_KEY:
        for field in ("api_key", "base_url", "model", "site_url", "app_name"):
            if field in value and value[field] is not None and not isinstance(value[field], str):
                raise SettingInputError(f"{field} must be a string")


def update_setting(
    db: Session,
    *,
    key: str,
    value: dict[str, Any],
    data_status: str,
    confidence_level: str,
) -> ApplicationSetting:
    validate_setting_value(key, value)
    setting = get_setting(db, key)
    if setting is None:
        raise SettingInputError("Setting not found")
    setting.value = value
    setting.data_status = data_status
    setting.confidence_level = confidence_level
    db.commit()
    db.refresh(setting)
    return setting


def openrouter_settings_read(db: Session) -> dict[str, str | bool | None]:
    defaults = _openrouter_defaults()
    record = get_setting(db, OPENROUTER_SETTING_KEY)
    stored_value = record.value if record is not None else {}
    stored_key = stored_value.get("api_key") if isinstance(stored_value.get("api_key"), str) else None
    env_key = defaults["api_key"]
    resolved_key = stored_key or env_key
    api_key_source = "stored" if stored_key else "environment" if env_key else "missing"
    return {
        "has_api_key": bool(resolved_key),
        "api_key_masked": _masked_secret(resolved_key),
        "api_key_source": api_key_source,
        "base_url": _string_or_default(stored_value.get("base_url"), str(defaults["base_url"])),
        "model": _string_or_default(stored_value.get("model"), str(defaults["model"])),
        "site_url": _string_or_default(stored_value.get("site_url"), str(defaults["site_url"])),
        "app_name": _string_or_default(stored_value.get("app_name"), str(defaults["app_name"])),
    }


def openrouter_runtime_settings(db: Session) -> dict[str, str | None]:
    defaults = _openrouter_defaults()
    record = get_setting(db, OPENROUTER_SETTING_KEY)
    stored_value = record.value if record is not None else {}
    stored_key = stored_value.get("api_key") if isinstance(stored_value.get("api_key"), str) else None
    return {
        "api_key": stored_key or defaults["api_key"],
        "base_url": _string_or_default(stored_value.get("base_url"), str(defaults["base_url"])),
        "model": _string_or_default(stored_value.get("model"), str(defaults["model"])),
        "site_url": _string_or_default(stored_value.get("site_url"), str(defaults["site_url"])),
        "app_name": _string_or_default(stored_value.get("app_name"), str(defaults["app_name"])),
    }


def update_openrouter_settings(
    db: Session,
    *,
    api_key: str | None = None,
    clear_api_key: bool = False,
    base_url: str | None = None,
    model: str | None = None,
    site_url: str | None = None,
    app_name: str | None = None,
) -> dict[str, str | bool | None]:
    defaults = _openrouter_defaults()
    record = get_setting(db, OPENROUTER_SETTING_KEY)
    current_value = dict(record.value) if record is not None else {}

    if clear_api_key:
        current_value.pop("api_key", None)
    elif api_key is not None and api_key.strip():
        current_value["api_key"] = api_key.strip()

    for field, value, default in (
        ("base_url", base_url, defaults["base_url"]),
        ("model", model, defaults["model"]),
        ("site_url", site_url, defaults["site_url"]),
        ("app_name", app_name, defaults["app_name"]),
    ):
        if value is not None:
            stripped = value.strip()
            current_value[field] = stripped or default

    validate_setting_value(OPENROUTER_SETTING_KEY, current_value)

    if record is None:
        record = ApplicationSetting(
            key=OPENROUTER_SETTING_KEY,
            category="llm_provider",
            value=current_value,
            data_status="user_assumption",
            confidence_level="medium",
        )
        db.add(record)
    else:
        record.value = current_value
        record.data_status = "user_assumption"
        record.confidence_level = "medium"

    db.commit()
    db.refresh(record)
    return openrouter_settings_read(db)
