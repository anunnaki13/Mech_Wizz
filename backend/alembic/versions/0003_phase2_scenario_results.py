"""phase 2 scenario results

Revision ID: 0003_phase2_scenario_results
Revises: 0002_phase2_scenarios
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_phase2_scenario_results"
down_revision = "0002_phase2_scenarios"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scenario_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("total_co2_ton_per_year", sa.Float(), nullable=True),
        sa.Column("captured_co2_ton_per_year", sa.Float(), nullable=True),
        sa.Column("vented_co2_ton_per_year", sa.Float(), nullable=True),
        sa.Column("methanol_ton_per_year", sa.Float(), nullable=True),
        sa.Column("h2_required_ton_per_year", sa.Float(), nullable=True),
        sa.Column("electrolyzer_required_mw", sa.Float(), nullable=True),
        sa.Column("gross_revenue_usd_per_year", sa.Float(), nullable=True),
        sa.Column("lcom_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("npv_usd", sa.Float(), nullable=True),
        sa.Column("irr", sa.Float(), nullable=True),
        sa.Column("payback_years", sa.Float(), nullable=True),
        sa.Column("missing_inputs", sa.JSON(), nullable=False),
        sa.Column("assumption_snapshot", sa.JSON(), nullable=False),
        sa.Column("calculation_version", sa.String(length=80), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scenario_results_scenario_id"), "scenario_results", ["scenario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_scenario_results_scenario_id"), table_name="scenario_results")
    op.drop_table("scenario_results")
