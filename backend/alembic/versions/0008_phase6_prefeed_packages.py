"""phase 6 prefeed packages

Revision ID: 0008_phase6_prefeed_packages
Revises: 0007_phase5_llm_documents
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_phase6_prefeed_packages"
down_revision = "0007_phase5_llm_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_feed_packages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("plant_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("package_name", sa.String(length=160), nullable=False),
        sa.Column("package_status", sa.String(length=50), nullable=False),
        sa.Column("owner_name", sa.String(length=160), nullable=True),
        sa.Column("source_organization", sa.String(length=160), nullable=True),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("version_label", sa.String(length=120), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pre_feed_packages_plant_id"), "pre_feed_packages", ["plant_id"], unique=False)
    op.create_index(op.f("ix_pre_feed_packages_scenario_id"), "pre_feed_packages", ["scenario_id"], unique=False)
    op.create_index(
        op.f("ix_pre_feed_packages_package_status"),
        "pre_feed_packages",
        ["package_status"],
        unique=False,
    )

    op.create_table(
        "pre_feed_package_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("document_role", sa.String(length=80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("package_id", "document_id", "document_role", name="uq_pre_feed_package_document_role"),
    )
    op.create_index(
        op.f("ix_pre_feed_package_documents_document_id"),
        "pre_feed_package_documents",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_package_documents_package_id"),
        "pre_feed_package_documents",
        ["package_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_package_documents_document_role"),
        "pre_feed_package_documents",
        ["document_role"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pre_feed_package_documents_document_role"), table_name="pre_feed_package_documents")
    op.drop_index(op.f("ix_pre_feed_package_documents_package_id"), table_name="pre_feed_package_documents")
    op.drop_index(op.f("ix_pre_feed_package_documents_document_id"), table_name="pre_feed_package_documents")
    op.drop_table("pre_feed_package_documents")
    op.drop_index(op.f("ix_pre_feed_packages_package_status"), table_name="pre_feed_packages")
    op.drop_index(op.f("ix_pre_feed_packages_scenario_id"), table_name="pre_feed_packages")
    op.drop_index(op.f("ix_pre_feed_packages_plant_id"), table_name="pre_feed_packages")
    op.drop_table("pre_feed_packages")
