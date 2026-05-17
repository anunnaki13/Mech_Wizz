"""phase 12 validation evidence workspace

Revision ID: 0012_phase12_validation_evidence
Revises: 0011_phase9_risk_decision
Create Date: 2026-05-17
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_phase12_validation_evidence"
down_revision = "0011_phase9_risk_decision"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("evidence_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("required_evidence", sa.Text(), nullable=True),
        sa.Column("current_basis", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("owner_name", sa.String(length=160), nullable=True),
        sa.Column("source_organization", sa.String(length=160), nullable=True),
        sa.Column("reference_url", sa.String(length=500), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("verified_date", sa.Date(), nullable=True),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "plant_id",
            "scenario_id",
            "category",
            "evidence_key",
            name="uq_validation_evidence_candidate_key",
        ),
    )
    op.create_index(op.f("ix_validation_evidence_plant_id"), "validation_evidence", ["plant_id"], unique=False)
    op.create_index(op.f("ix_validation_evidence_scenario_id"), "validation_evidence", ["scenario_id"], unique=False)
    op.create_index(op.f("ix_validation_evidence_document_id"), "validation_evidence", ["document_id"], unique=False)
    op.create_index(op.f("ix_validation_evidence_category"), "validation_evidence", ["category"], unique=False)
    op.create_index(op.f("ix_validation_evidence_status"), "validation_evidence", ["status"], unique=False)
    op.create_index(op.f("ix_validation_evidence_priority"), "validation_evidence", ["priority"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_validation_evidence_priority"), table_name="validation_evidence")
    op.drop_index(op.f("ix_validation_evidence_status"), table_name="validation_evidence")
    op.drop_index(op.f("ix_validation_evidence_category"), table_name="validation_evidence")
    op.drop_index(op.f("ix_validation_evidence_document_id"), table_name="validation_evidence")
    op.drop_index(op.f("ix_validation_evidence_scenario_id"), table_name="validation_evidence")
    op.drop_index(op.f("ix_validation_evidence_plant_id"), table_name="validation_evidence")
    op.drop_table("validation_evidence")
