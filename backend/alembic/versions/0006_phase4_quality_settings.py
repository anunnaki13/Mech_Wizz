"""phase 4 quality settings

Revision ID: 0006_phase4_quality_settings
Revises: 0005_phase3_sensitivity
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_phase4_quality_settings"
down_revision = "0005_phase3_sensitivity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_application_settings_key"),
    )
    op.create_index(op.f("ix_application_settings_key"), "application_settings", ["key"], unique=False)

    op.create_table(
        "data_gaps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("source_module", sa.String(length=100), nullable=False),
        sa.Column("missing_data_name", sa.String(length=255), nullable=False),
        sa.Column("impact_level", sa.String(length=50), nullable=False),
        sa.Column("priority_level", sa.String(length=50), nullable=False),
        sa.Column("recommendation", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_gaps_plant_id"), "data_gaps", ["plant_id"], unique=False)
    op.create_index(op.f("ix_data_gaps_scenario_id"), "data_gaps", ["scenario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_gaps_scenario_id"), table_name="data_gaps")
    op.drop_index(op.f("ix_data_gaps_plant_id"), table_name="data_gaps")
    op.drop_table("data_gaps")
    op.drop_index(op.f("ix_application_settings_key"), table_name="application_settings")
    op.drop_table("application_settings")
