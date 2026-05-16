"""phase 2 scenario assumptions

Revision ID: 0002_phase2_scenarios
Revises: 0001_phase1_schema
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_phase2_scenarios"
down_revision = "0001_phase1_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_scenarios",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_name", sa.String(length=160), nullable=False),
        sa.Column("scheme", sa.String(length=32), nullable=False),
        sa.Column("pln_ownership_percent", sa.Float(), nullable=True),
        sa.Column("partner_capex_responsibility_percent", sa.Float(), nullable=True),
        sa.Column("pln_capex_responsibility_percent", sa.Float(), nullable=True),
        sa.Column("revenue_model", sa.String(length=160), nullable=True),
        sa.Column("capture_rate", sa.Float(), nullable=True),
        sa.Column("process_efficiency", sa.Float(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plant_id", "scenario_name", name="uq_business_scenarios_plant_name"),
    )
    op.create_index(op.f("ix_business_scenarios_plant_id"), "business_scenarios", ["plant_id"], unique=False)

    op.create_table(
        "financial_assumptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("methanol_price_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("grey_methanol_price_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("hydrogen_price_usd_per_kg", sa.Float(), nullable=True),
        sa.Column("electricity_price_usd_per_kwh", sa.Float(), nullable=True),
        sa.Column("carbon_credit_price_idr_per_ton", sa.Float(), nullable=True),
        sa.Column("exchange_rate_idr_usd", sa.Float(), nullable=True),
        sa.Column("discount_rate", sa.Float(), nullable=True),
        sa.Column("tax_rate", sa.Float(), nullable=True),
        sa.Column("capex_capture_usd", sa.Float(), nullable=True),
        sa.Column("capex_electrolyzer_usd", sa.Float(), nullable=True),
        sa.Column("capex_methanol_plant_usd", sa.Float(), nullable=True),
        sa.Column("capex_storage_port_usd", sa.Float(), nullable=True),
        sa.Column("opex_percent_capex", sa.Float(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scenario_id", name="uq_financial_assumptions_scenario"),
    )
    op.create_index(op.f("ix_financial_assumptions_scenario_id"), "financial_assumptions", ["scenario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_financial_assumptions_scenario_id"), table_name="financial_assumptions")
    op.drop_table("financial_assumptions")
    op.drop_index(op.f("ix_business_scenarios_plant_id"), table_name="business_scenarios")
    op.drop_table("business_scenarios")
