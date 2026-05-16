"""phase 3 sensitivity results

Revision ID: 0005_phase3_sensitivity
Revises: 0004_phase3_scoring
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_phase3_sensitivity"
down_revision = "0004_phase3_scoring"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sensitivity_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_result_id", sa.String(length=36), nullable=True),
        sa.Column("variable_name", sa.String(length=80), nullable=False),
        sa.Column("low_input_value", sa.Float(), nullable=True),
        sa.Column("base_input_value", sa.Float(), nullable=True),
        sa.Column("high_input_value", sa.Float(), nullable=True),
        sa.Column("low_irr", sa.Float(), nullable=True),
        sa.Column("base_irr", sa.Float(), nullable=True),
        sa.Column("high_irr", sa.Float(), nullable=True),
        sa.Column("low_npv_usd", sa.Float(), nullable=True),
        sa.Column("base_npv_usd", sa.Float(), nullable=True),
        sa.Column("high_npv_usd", sa.Float(), nullable=True),
        sa.Column("low_lcom_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("base_lcom_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("high_lcom_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("impact_score", sa.Float(), nullable=False),
        sa.Column("missing_inputs", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("assumption_snapshot", sa.JSON(), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_result_id"], ["scenario_results.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sensitivity_results_run_id"), "sensitivity_results", ["run_id"], unique=False)
    op.create_index(op.f("ix_sensitivity_results_plant_id"), "sensitivity_results", ["plant_id"], unique=False)
    op.create_index(
        op.f("ix_sensitivity_results_scenario_id"),
        "sensitivity_results",
        ["scenario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sensitivity_results_scenario_result_id"),
        "sensitivity_results",
        ["scenario_result_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_sensitivity_results_scenario_result_id"), table_name="sensitivity_results")
    op.drop_index(op.f("ix_sensitivity_results_scenario_id"), table_name="sensitivity_results")
    op.drop_index(op.f("ix_sensitivity_results_plant_id"), table_name="sensitivity_results")
    op.drop_index(op.f("ix_sensitivity_results_run_id"), table_name="sensitivity_results")
    op.drop_table("sensitivity_results")
