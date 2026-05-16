from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApplicationSetting


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
