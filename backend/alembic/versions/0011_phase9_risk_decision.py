"""phase 9 risk decision dashboard

Revision ID: 0011_phase9_risk_decision
Revises: 0010_phase8_offtake_mrv
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0011_phase9_risk_decision"
down_revision = "0010_phase8_offtake_mrv"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_feed_risks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("risk_statement", sa.Text(), nullable=False),
        sa.Column("likelihood", sa.Integer(), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("mitigation", sa.Text(), nullable=True),
        sa.Column("owner_name", sa.String(length=160), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pre_feed_risks_package_id"), "pre_feed_risks", ["package_id"], unique=False)
    op.create_index(op.f("ix_pre_feed_risks_category"), "pre_feed_risks", ["category"], unique=False)
    op.create_index(op.f("ix_pre_feed_risks_status"), "pre_feed_risks", ["status"], unique=False)

    op.create_table(
        "pre_feed_decision_gates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("gate_title", sa.String(length=160), nullable=False),
        sa.Column("evidence_reference", sa.Text(), nullable=True),
        sa.Column("owner_name", sa.String(length=160), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pre_feed_decision_gates_package_id"),
        "pre_feed_decision_gates",
        ["package_id"],
        unique=False,
    )
    op.create_index(op.f("ix_pre_feed_decision_gates_category"), "pre_feed_decision_gates", ["category"], unique=False)
    op.create_index(op.f("ix_pre_feed_decision_gates_status"), "pre_feed_decision_gates", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pre_feed_decision_gates_status"), table_name="pre_feed_decision_gates")
    op.drop_index(op.f("ix_pre_feed_decision_gates_category"), table_name="pre_feed_decision_gates")
    op.drop_index(op.f("ix_pre_feed_decision_gates_package_id"), table_name="pre_feed_decision_gates")
    op.drop_table("pre_feed_decision_gates")
    op.drop_index(op.f("ix_pre_feed_risks_status"), table_name="pre_feed_risks")
    op.drop_index(op.f("ix_pre_feed_risks_category"), table_name="pre_feed_risks")
    op.drop_index(op.f("ix_pre_feed_risks_package_id"), table_name="pre_feed_risks")
    op.drop_table("pre_feed_risks")
