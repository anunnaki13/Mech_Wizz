from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.models import Plant


TENAYAN_PLANT = {
    "plant_name": "PLTU Tenayan",
    "unit_name": "Unit 1-2",
    "province": "Riau",
    "city": "Pekanbaru",
    "capacity_mw": 220,
    "fuel_type": "coal",
    "status": "active",
    "capacity_factor": 0.90,
    "operating_days_per_year": 330,
    "owner": "PLN NP",
    "data_status": "actual",
    "confidence_level": "medium",
}


def seed_tenayan(db: Session) -> Plant:
    plant = db.scalar(
        select(Plant).where(
            Plant.plant_name == TENAYAN_PLANT["plant_name"],
            Plant.unit_name == TENAYAN_PLANT["unit_name"],
        )
    )
    if plant is None:
        plant = Plant(**TENAYAN_PLANT)
        db.add(plant)
    else:
        for field, value in TENAYAN_PLANT.items():
            setattr(plant, field, value)

    db.commit()
    db.refresh(plant)
    return plant


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        plant = seed_tenayan(db)
        print(f"Seeded {plant.plant_name} {plant.unit_name}")


if __name__ == "__main__":
    main()
