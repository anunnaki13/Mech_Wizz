"""phase 3 unit scoring

Revision ID: 0004_phase3_scoring
Revises: 0003_phase2_scenario_results
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_phase3_scoring"
down_revision = "0003_phase2_scenario_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "unit_scoring_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_result_id", sa.String(length=36), nullable=False),
        sa.Column("scoring_run_id", sa.String(length=36), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=False),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("co2_availability_score", sa.Float(), nullable=False),
        sa.Column("methanol_potential_score", sa.Float(), nullable=False),
        sa.Column("h2_readiness_score", sa.Float(), nullable=False),
        sa.Column("economic_return_score", sa.Float(), nullable=False),
        sa.Column("infrastructure_score", sa.Float(), nullable=False),
        sa.Column("land_port_score", sa.Float(), nullable=False),
        sa.Column("market_access_score", sa.Float(), nullable=False),
        sa.Column("risk_permit_score", sa.Float(), nullable=False),
        sa.Column("data_completeness_score", sa.Float(), nullable=False),
        sa.Column("emission_data_quality_score", sa.Float(), nullable=False),
        sa.Column("land_readiness_score", sa.Float(), nullable=False),
        sa.Column("utility_readiness_score", sa.Float(), nullable=False),
        sa.Column("h2_strategy_clarity_score", sa.Float(), nullable=False),
        sa.Column("permit_logistic_readiness_score", sa.Float(), nullable=False),
        sa.Column("carbon_credit_potential_score", sa.Float(), nullable=False),
        sa.Column("strategic_value_score", sa.Float(), nullable=False),
        sa.Column("utility_advantage_score", sa.Float(), nullable=False),
        sa.Column("component_scores", sa.JSON(), nullable=False),
        sa.Column("data_gap_count", sa.Integer(), nullable=False),
        sa.Column("rank_position", sa.Integer(), nullable=True),
        sa.Column("recommended_scheme", sa.String(length=80), nullable=False),
        sa.Column("key_bottleneck", sa.String(length=240), nullable=False),
        sa.Column("scoring_version", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_result_id"], ["scenario_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_unit_scoring_results_plant_id"), "unit_scoring_results", ["plant_id"], unique=False)
    op.create_index(
        op.f("ix_unit_scoring_results_scenario_id"),
        "unit_scoring_results",
        ["scenario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unit_scoring_results_scenario_result_id"),
        "unit_scoring_results",
        ["scenario_result_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unit_scoring_results_scoring_run_id"),
        "unit_scoring_results",
        ["scoring_run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_unit_scoring_results_scoring_run_id"), table_name="unit_scoring_results")
    op.drop_index(op.f("ix_unit_scoring_results_scenario_result_id"), table_name="unit_scoring_results")
    op.drop_index(op.f("ix_unit_scoring_results_scenario_id"), table_name="unit_scoring_results")
    op.drop_index(op.f("ix_unit_scoring_results_plant_id"), table_name="unit_scoring_results")
    op.drop_table("unit_scoring_results")
