"""phase 7 cost vendor engine

Revision ID: 0009_phase7_cost_vendor
Revises: 0008_phase6_prefeed_packages
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_phase7_cost_vendor"
down_revision = "0008_phase6_prefeed_packages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_feed_vendor_proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("supporting_document_id", sa.String(length=36), nullable=True),
        sa.Column("vendor_name", sa.String(length=160), nullable=False),
        sa.Column("proposal_name", sa.String(length=160), nullable=False),
        sa.Column("scope_capture_package", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_electrolyzer", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_methanol_plant", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_storage_port", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_grid_power", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_land", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("scope_mrv", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("commercial_basis", sa.Text(), nullable=True),
        sa.Column("delivery_assumptions", sa.Text(), nullable=True),
        sa.Column("exclusions", sa.Text(), nullable=True),
        sa.Column("validity_date", sa.Date(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supporting_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pre_feed_vendor_proposals_package_id"),
        "pre_feed_vendor_proposals",
        ["package_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_vendor_proposals_supporting_document_id"),
        "pre_feed_vendor_proposals",
        ["supporting_document_id"],
        unique=False,
    )

    op.create_table(
        "pre_feed_cost_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("vendor_proposal_id", sa.String(length=36), nullable=True),
        sa.Column("cost_type", sa.String(length=32), nullable=False),
        sa.Column("cost_component", sa.String(length=80), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("unit_basis", sa.String(length=80), nullable=True),
        sa.Column("recurrence", sa.String(length=32), nullable=True),
        sa.Column("contingency_percent", sa.Float(), nullable=True),
        sa.Column("escalation_percent", sa.Float(), nullable=True),
        sa.Column("source_label", sa.String(length=160), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_proposal_id"], ["pre_feed_vendor_proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pre_feed_cost_items_package_id"), "pre_feed_cost_items", ["package_id"], unique=False)
    op.create_index(
        op.f("ix_pre_feed_cost_items_vendor_proposal_id"),
        "pre_feed_cost_items",
        ["vendor_proposal_id"],
        unique=False,
    )
    op.create_index(op.f("ix_pre_feed_cost_items_cost_type"), "pre_feed_cost_items", ["cost_type"], unique=False)

    op.create_table(
        "pre_feed_cost_basis_selections",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("vendor_proposal_id", sa.String(length=36), nullable=True),
        sa.Column("selection_type", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("snapshot_totals", sa.JSON(), nullable=True),
        sa.Column("scenario_ready_assumptions", sa.JSON(), nullable=True),
        sa.Column("selected_by", sa.String(length=160), nullable=True),
        sa.Column("selection_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_proposal_id"], ["pre_feed_vendor_proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pre_feed_cost_basis_selections_scenario_id"),
        "pre_feed_cost_basis_selections",
        ["scenario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_cost_basis_selections_package_id"),
        "pre_feed_cost_basis_selections",
        ["package_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_cost_basis_selections_vendor_proposal_id"),
        "pre_feed_cost_basis_selections",
        ["vendor_proposal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pre_feed_cost_basis_selections_vendor_proposal_id"), table_name="pre_feed_cost_basis_selections")
    op.drop_index(op.f("ix_pre_feed_cost_basis_selections_package_id"), table_name="pre_feed_cost_basis_selections")
    op.drop_index(op.f("ix_pre_feed_cost_basis_selections_scenario_id"), table_name="pre_feed_cost_basis_selections")
    op.drop_table("pre_feed_cost_basis_selections")
    op.drop_index(op.f("ix_pre_feed_cost_items_cost_type"), table_name="pre_feed_cost_items")
    op.drop_index(op.f("ix_pre_feed_cost_items_vendor_proposal_id"), table_name="pre_feed_cost_items")
    op.drop_index(op.f("ix_pre_feed_cost_items_package_id"), table_name="pre_feed_cost_items")
    op.drop_table("pre_feed_cost_items")
    op.drop_index(op.f("ix_pre_feed_vendor_proposals_supporting_document_id"), table_name="pre_feed_vendor_proposals")
    op.drop_index(op.f("ix_pre_feed_vendor_proposals_package_id"), table_name="pre_feed_vendor_proposals")
    op.drop_table("pre_feed_vendor_proposals")
