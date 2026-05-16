"""phase 5 llm and documents

Revision ID: 0007_phase5_llm_documents
Revises: 0006_phase4_quality_settings
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_phase5_llm_documents"
down_revision = "0006_phase4_quality_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=True),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("document_category", sa.String(length=120), nullable=True),
        sa.Column("upload_status", sa.String(length=50), nullable=False),
        sa.Column("extraction_status", sa.String(length=50), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("extraction_error", sa.Text(), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_plant_id"), "documents", ["plant_id"], unique=False)
    op.create_index(op.f("ix_documents_scenario_id"), "documents", ["scenario_id"], unique=False)

    op.create_table(
        "llm_insights",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=True),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("insight_type", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("provider_response_id", sa.String(length=160), nullable=True),
        sa.Column("usage", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_llm_insights_document_id"), "llm_insights", ["document_id"], unique=False)
    op.create_index(op.f("ix_llm_insights_insight_type"), "llm_insights", ["insight_type"], unique=False)
    op.create_index(op.f("ix_llm_insights_plant_id"), "llm_insights", ["plant_id"], unique=False)
    op.create_index(op.f("ix_llm_insights_scenario_id"), "llm_insights", ["scenario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_llm_insights_scenario_id"), table_name="llm_insights")
    op.drop_index(op.f("ix_llm_insights_plant_id"), table_name="llm_insights")
    op.drop_index(op.f("ix_llm_insights_insight_type"), table_name="llm_insights")
    op.drop_index(op.f("ix_llm_insights_document_id"), table_name="llm_insights")
    op.drop_table("llm_insights")
    op.drop_index(op.f("ix_documents_scenario_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_plant_id"), table_name="documents")
    op.drop_table("documents")
