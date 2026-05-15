"""phase 1 input schema

Revision ID: 0001_phase1_schema
Revises:
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_phase1_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_name", sa.String(length=160), nullable=False),
        sa.Column("unit_name", sa.String(length=120), nullable=False),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("capacity_mw", sa.Float(), nullable=True),
        sa.Column("fuel_type", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("capacity_factor", sa.Float(), nullable=True),
        sa.Column("operating_days_per_year", sa.Integer(), nullable=True),
        sa.Column("owner", sa.String(length=160), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_name", "unit_name", name="uq_plants_name_unit"),
    )

    op.create_table(
        "emission_tests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("stack_id", sa.String(length=120), nullable=False),
        sa.Column("test_date", sa.Date(), nullable=True),
        sa.Column("lab_name", sa.String(length=160), nullable=True),
        sa.Column("stack_diameter_m", sa.Float(), nullable=True),
        sa.Column("gas_velocity_m_s", sa.Float(), nullable=True),
        sa.Column("flue_gas_temperature_c", sa.Float(), nullable=True),
        sa.Column("co2_percent_dry", sa.Float(), nullable=True),
        sa.Column("o2_percent", sa.Float(), nullable=True),
        sa.Column("moisture_percent", sa.Float(), nullable=True),
        sa.Column("so2_mg_nm3", sa.Float(), nullable=True),
        sa.Column("nox_mg_nm3", sa.Float(), nullable=True),
        sa.Column("particulate_mg_nm3", sa.Float(), nullable=True),
        sa.Column("hg_mg_nm3", sa.Float(), nullable=True),
        sa.Column("compliance_status", sa.String(length=80), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_id", "stack_id", name="uq_emission_tests_plant_stack"),
    )
    op.create_index(op.f("ix_emission_tests_plant_id"), "emission_tests", ["plant_id"], unique=False)

    op.create_table(
        "site_readiness",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("available_land_ha", sa.Float(), nullable=True),
        sa.Column("land_status", sa.String(length=120), nullable=True),
        sa.Column("distance_to_stack_km", sa.Float(), nullable=True),
        sa.Column("has_port_or_jetty", sa.Boolean(), nullable=True),
        sa.Column("distance_to_port_km", sa.Float(), nullable=True),
        sa.Column("port_capacity_dwt", sa.Float(), nullable=True),
        sa.Column("road_access", sa.String(length=160), nullable=True),
        sa.Column("water_availability", sa.String(length=160), nullable=True),
        sa.Column("power_availability", sa.String(length=160), nullable=True),
        sa.Column("utility_readiness", sa.String(length=160), nullable=True),
        sa.Column("permit_risk", sa.String(length=80), nullable=True),
        sa.Column("social_risk", sa.String(length=80), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_id"),
    )

    op.create_table(
        "hydrogen_strategies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("existing_h2_available", sa.Boolean(), nullable=True),
        sa.Column("h2_strategy", sa.String(length=180), nullable=True),
        sa.Column("h2_cost_case", sa.String(length=120), nullable=True),
        sa.Column("h2_cost_usd_per_kg", sa.Float(), nullable=True),
        sa.Column("h2_readiness_score", sa.Float(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_id"),
    )


def downgrade() -> None:
    op.drop_table("hydrogen_strategies")
    op.drop_table("site_readiness")
    op.drop_index(op.f("ix_emission_tests_plant_id"), table_name="emission_tests")
    op.drop_table("emission_tests")
    op.drop_table("plants")
