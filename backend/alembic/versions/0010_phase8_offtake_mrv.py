"""phase 8 offtake mrv readiness

Revision ID: 0010_phase8_offtake_mrv
Revises: 0009_phase7_cost_vendor
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0010_phase8_offtake_mrv"
down_revision = "0009_phase7_cost_vendor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_feed_price_decks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("scenario_id", sa.String(length=36), nullable=True),
        sa.Column("deck_name", sa.String(length=160), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("methanol_price_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("carbon_credit_price_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("electricity_price_usd_per_kwh", sa.Float(), nullable=True),
        sa.Column("hydrogen_price_usd_per_kg", sa.Float(), nullable=True),
        sa.Column("exchange_rate_idr_usd", sa.Float(), nullable=True),
        sa.Column("escalation_percent", sa.Float(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scenario_id"], ["business_scenarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pre_feed_price_decks_package_id"), "pre_feed_price_decks", ["package_id"], unique=False)
    op.create_index(op.f("ix_pre_feed_price_decks_scenario_id"), "pre_feed_price_decks", ["scenario_id"], unique=False)
    op.create_index(op.f("ix_pre_feed_price_decks_is_active"), "pre_feed_price_decks", ["is_active"], unique=False)

    op.create_table(
        "pre_feed_offtake_prospects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("supporting_document_id", sa.String(length=36), nullable=True),
        sa.Column("counterparty_name", sa.String(length=160), nullable=False),
        sa.Column("product", sa.String(length=50), nullable=False),
        sa.Column("target_volume_tpy", sa.Float(), nullable=True),
        sa.Column("term_years", sa.Float(), nullable=True),
        sa.Column("pricing_basis", sa.String(length=160), nullable=True),
        sa.Column("price_usd_per_ton", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
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
        op.f("ix_pre_feed_offtake_prospects_package_id"),
        "pre_feed_offtake_prospects",
        ["package_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pre_feed_offtake_prospects_supporting_document_id"),
        "pre_feed_offtake_prospects",
        ["supporting_document_id"],
        unique=False,
    )
    op.create_index(op.f("ix_pre_feed_offtake_prospects_product"), "pre_feed_offtake_prospects", ["product"], unique=False)
    op.create_index(op.f("ix_pre_feed_offtake_prospects_status"), "pre_feed_offtake_prospects", ["status"], unique=False)

    op.create_table(
        "pre_feed_mrv_assumptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), nullable=False),
        sa.Column("supporting_document_id", sa.String(length=36), nullable=True),
        sa.Column("baseline_emissions_tco2e_per_year", sa.Float(), nullable=True),
        sa.Column("captured_co2_accounting_tpy", sa.Float(), nullable=True),
        sa.Column("product_carbon_intensity_tco2e_per_ton", sa.Float(), nullable=True),
        sa.Column("electricity_source", sa.String(length=160), nullable=True),
        sa.Column("electricity_emission_factor_tco2e_per_mwh", sa.Float(), nullable=True),
        sa.Column("methanol_pathway", sa.String(length=160), nullable=True),
        sa.Column("carbon_credit_methodology", sa.String(length=160), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=False),
        sa.Column("verifier_name", sa.String(length=160), nullable=True),
        sa.Column("carbon_credit_eligibility", sa.String(length=50), nullable=False),
        sa.Column("eligibility_basis", sa.Text(), nullable=True),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("confidence_level", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["pre_feed_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supporting_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pre_feed_mrv_assumptions_package_id"), "pre_feed_mrv_assumptions", ["package_id"], unique=False)
    op.create_index(
        op.f("ix_pre_feed_mrv_assumptions_supporting_document_id"),
        "pre_feed_mrv_assumptions",
        ["supporting_document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pre_feed_mrv_assumptions_supporting_document_id"), table_name="pre_feed_mrv_assumptions")
    op.drop_index(op.f("ix_pre_feed_mrv_assumptions_package_id"), table_name="pre_feed_mrv_assumptions")
    op.drop_table("pre_feed_mrv_assumptions")
    op.drop_index(op.f("ix_pre_feed_offtake_prospects_status"), table_name="pre_feed_offtake_prospects")
    op.drop_index(op.f("ix_pre_feed_offtake_prospects_product"), table_name="pre_feed_offtake_prospects")
    op.drop_index(op.f("ix_pre_feed_offtake_prospects_supporting_document_id"), table_name="pre_feed_offtake_prospects")
    op.drop_index(op.f("ix_pre_feed_offtake_prospects_package_id"), table_name="pre_feed_offtake_prospects")
    op.drop_table("pre_feed_offtake_prospects")
    op.drop_index(op.f("ix_pre_feed_price_decks_is_active"), table_name="pre_feed_price_decks")
    op.drop_index(op.f("ix_pre_feed_price_decks_scenario_id"), table_name="pre_feed_price_decks")
    op.drop_index(op.f("ix_pre_feed_price_decks_package_id"), table_name="pre_feed_price_decks")
    op.drop_table("pre_feed_price_decks")
