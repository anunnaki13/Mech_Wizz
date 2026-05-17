"use client";

import { AlertTriangle, BadgeDollarSign, Leaf, Plus, RefreshCw, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  activatePreFeedPriceDeck,
  createPreFeedMrvAssumption,
  createPreFeedOfftakeProspect,
  createPreFeedPriceDeck,
  deletePreFeedMrvAssumption,
  deletePreFeedOfftakeProspect,
  deletePreFeedPriceDeck,
  getPreFeedMrvGaps,
  getPreFeedMrvSummary,
  getPreFeedOfftakeGaps,
  getPreFeedOfftakeSummary,
  listPreFeedMrvAssumptions,
  listPreFeedOfftakeProspects,
  listPreFeedPriceDecks,
} from "@/lib/api";
import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";
import type {
  PreFeedCarbonCreditEligibility,
  PreFeedGap,
  PreFeedMrvAssumption,
  PreFeedMrvSummary,
  PreFeedMrvVerificationStatus,
  PreFeedOfftakeProduct,
  PreFeedOfftakeProspect,
  PreFeedOfftakeStatus,
  PreFeedOfftakeSummary,
  PreFeedPriceDeck,
} from "@/types/prefeed-market";

const DATA_STATUS_OPTIONS: DataStatus[] = [
  "actual",
  "estimated",
  "benchmark",
  "user_assumption",
  "partner_supplied",
  "unknown",
];
const CONFIDENCE_OPTIONS: ConfidenceLevel[] = ["high", "medium", "low", "unknown"];
const PRODUCTS: PreFeedOfftakeProduct[] = ["e_methanol", "carbon_credit", "co2_supply", "hydrogen", "other"];
const OFFTAKE_STATUSES: PreFeedOfftakeStatus[] = [
  "lead",
  "discussion",
  "loi",
  "term_sheet",
  "contracted",
  "signed",
  "inactive",
];
const VERIFICATION_STATUSES: PreFeedMrvVerificationStatus[] = [
  "not_started",
  "method_selected",
  "data_collected",
  "third_party_review",
  "verified",
];
const ELIGIBILITY_OPTIONS: PreFeedCarbonCreditEligibility[] = [
  "unknown",
  "screening",
  "potentially_eligible",
  "eligible",
  "not_eligible",
];

type PriceDeckDraft = {
  deck_name: string;
  is_active: boolean;
  methanol_price_usd_per_ton: string;
  carbon_credit_price_usd_per_ton: string;
  electricity_price_usd_per_kwh: string;
  hydrogen_price_usd_per_kg: string;
  exchange_rate_idr_usd: string;
  escalation_percent: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

type OfftakeDraft = {
  supporting_document_id: string;
  counterparty_name: string;
  product: PreFeedOfftakeProduct;
  target_volume_tpy: string;
  term_years: string;
  pricing_basis: string;
  price_usd_per_ton: string;
  status: PreFeedOfftakeStatus;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

type MrvDraft = {
  supporting_document_id: string;
  baseline_emissions_tco2e_per_year: string;
  captured_co2_accounting_tpy: string;
  product_carbon_intensity_tco2e_per_ton: string;
  electricity_source: string;
  electricity_emission_factor_tco2e_per_mwh: string;
  methanol_pathway: string;
  carbon_credit_methodology: string;
  verification_status: PreFeedMrvVerificationStatus;
  verifier_name: string;
  carbon_credit_eligibility: PreFeedCarbonCreditEligibility;
  eligibility_basis: string;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string;
};

const EMPTY_PRICE_DECK: PriceDeckDraft = {
  deck_name: "",
  is_active: true,
  methanol_price_usd_per_ton: "",
  carbon_credit_price_usd_per_ton: "",
  electricity_price_usd_per_kwh: "",
  hydrogen_price_usd_per_kg: "",
  exchange_rate_idr_usd: "",
  escalation_percent: "",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

const EMPTY_OFFTAKE: OfftakeDraft = {
  supporting_document_id: "",
  counterparty_name: "",
  product: "e_methanol",
  target_volume_tpy: "",
  term_years: "",
  pricing_basis: "",
  price_usd_per_ton: "",
  status: "lead",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

const EMPTY_MRV: MrvDraft = {
  supporting_document_id: "",
  baseline_emissions_tco2e_per_year: "",
  captured_co2_accounting_tpy: "",
  product_carbon_intensity_tco2e_per_ton: "",
  electricity_source: "",
  electricity_emission_factor_tco2e_per_mwh: "",
  methanol_pathway: "",
  carbon_credit_methodology: "",
  verification_status: "not_started",
  verifier_name: "",
  carbon_credit_eligibility: "unknown",
  eligibility_basis: "",
  data_status: "unknown",
  confidence_level: "unknown",
  notes: "",
};

function labelFor(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function blankToNull(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function numberOrNull(value: string) {
  return value.trim() ? Number(value) : null;
}

function formatNumber(value: number | null | undefined, suffix = "", digits = 0) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: digits })}${suffix}`;
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${Math.round(value * 100)}%`;
}

export function OfftakeMrvWorkspace({
  packageId,
  scenarioId,
  documents,
}: {
  packageId: string | null;
  scenarioId: string | null;
  documents: ProjectDocument[];
}) {
  const [priceDecks, setPriceDecks] = useState<PreFeedPriceDeck[]>([]);
  const [prospects, setProspects] = useState<PreFeedOfftakeProspect[]>([]);
  const [offtakeSummary, setOfftakeSummary] = useState<PreFeedOfftakeSummary | null>(null);
  const [offtakeGaps, setOfftakeGaps] = useState<PreFeedGap[]>([]);
  const [mrvAssumptions, setMrvAssumptions] = useState<PreFeedMrvAssumption[]>([]);
  const [mrvSummary, setMrvSummary] = useState<PreFeedMrvSummary | null>(null);
  const [mrvGaps, setMrvGaps] = useState<PreFeedGap[]>([]);
  const [priceDraft, setPriceDraft] = useState<PriceDeckDraft>(EMPTY_PRICE_DECK);
  const [offtakeDraft, setOfftakeDraft] = useState<OfftakeDraft>(EMPTY_OFFTAKE);
  const [mrvDraft, setMrvDraft] = useState<MrvDraft>(EMPTY_MRV);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeDeck = useMemo(() => priceDecks.find((deck) => deck.is_active) ?? null, [priceDecks]);

  function updatePriceDraft<K extends keyof PriceDeckDraft>(key: K, value: PriceDeckDraft[K]) {
    setPriceDraft((current) => ({ ...current, [key]: value }));
  }

  function updateOfftakeDraft<K extends keyof OfftakeDraft>(key: K, value: OfftakeDraft[K]) {
    setOfftakeDraft((current) => ({ ...current, [key]: value }));
  }

  function updateMrvDraft<K extends keyof MrvDraft>(key: K, value: MrvDraft[K]) {
    setMrvDraft((current) => ({ ...current, [key]: value }));
  }

  async function loadAll() {
    if (!packageId) {
      setPriceDecks([]);
      setProspects([]);
      setOfftakeSummary(null);
      setOfftakeGaps([]);
      setMrvAssumptions([]);
      setMrvSummary(null);
      setMrvGaps([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [decks, offtakes, offtakeData, offtakeGapRows, mrvRows, mrvData, mrvGapRows] = await Promise.all([
        listPreFeedPriceDecks(packageId),
        listPreFeedOfftakeProspects(packageId),
        getPreFeedOfftakeSummary(packageId),
        getPreFeedOfftakeGaps(packageId),
        listPreFeedMrvAssumptions(packageId),
        getPreFeedMrvSummary(packageId),
        getPreFeedMrvGaps(packageId),
      ]);
      setPriceDecks(decks);
      setProspects(offtakes);
      setOfftakeSummary(offtakeData);
      setOfftakeGaps(offtakeGapRows);
      setMrvAssumptions(mrvRows);
      setMrvSummary(mrvData);
      setMrvGaps(mrvGapRows);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Offtake/MRV data could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSavePriceDeck() {
    if (!packageId || !priceDraft.deck_name.trim()) {
      setErrorMessage("Package and deck name are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedPriceDeck(packageId, {
        scenario_id: scenarioId,
        deck_name: priceDraft.deck_name.trim(),
        is_active: priceDraft.is_active,
        methanol_price_usd_per_ton: numberOrNull(priceDraft.methanol_price_usd_per_ton),
        carbon_credit_price_usd_per_ton: numberOrNull(priceDraft.carbon_credit_price_usd_per_ton),
        electricity_price_usd_per_kwh: numberOrNull(priceDraft.electricity_price_usd_per_kwh),
        hydrogen_price_usd_per_kg: numberOrNull(priceDraft.hydrogen_price_usd_per_kg),
        exchange_rate_idr_usd: numberOrNull(priceDraft.exchange_rate_idr_usd),
        escalation_percent: numberOrNull(priceDraft.escalation_percent),
        data_status: priceDraft.data_status,
        confidence_level: priceDraft.confidence_level,
        notes: blankToNull(priceDraft.notes),
      });
      setPriceDraft(EMPTY_PRICE_DECK);
      await loadAll();
      setStatusMessage("Price deck saved. Next: keep it active if it should drive revenue assumptions.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Price deck could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleActivateDeck(deckId: string) {
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await activatePreFeedPriceDeck(deckId);
      await loadAll();
      setStatusMessage("Price deck activated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Price deck could not be activated.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteDeck(deckId: string) {
    const confirmed = window.confirm("Delete this price deck? Revenue assumptions linked to this deck will no longer be available.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedPriceDeck(deckId);
      await loadAll();
      setStatusMessage("Price deck deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Price deck could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveOfftake() {
    if (!packageId || !offtakeDraft.counterparty_name.trim()) {
      setErrorMessage("Package and counterparty are required.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedOfftakeProspect(packageId, {
        supporting_document_id: blankToNull(offtakeDraft.supporting_document_id),
        counterparty_name: offtakeDraft.counterparty_name.trim(),
        product: offtakeDraft.product,
        target_volume_tpy: numberOrNull(offtakeDraft.target_volume_tpy),
        term_years: numberOrNull(offtakeDraft.term_years),
        pricing_basis: blankToNull(offtakeDraft.pricing_basis),
        price_usd_per_ton: numberOrNull(offtakeDraft.price_usd_per_ton),
        status: offtakeDraft.status,
        data_status: offtakeDraft.data_status,
        confidence_level: offtakeDraft.confidence_level,
        notes: blankToNull(offtakeDraft.notes),
      });
      setOfftakeDraft(EMPTY_OFFTAKE);
      await loadAll();
      setStatusMessage("Offtake prospect saved. Next: review offtake readiness and gaps.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Offtake prospect could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteOfftake(prospectId: string) {
    const confirmed = window.confirm("Delete this offtake prospect? This may reduce offtake readiness.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedOfftakeProspect(prospectId);
      await loadAll();
      setStatusMessage("Offtake prospect deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Offtake prospect could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveMrv() {
    if (!packageId) {
      setErrorMessage("Select a package before saving MRV assumptions.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createPreFeedMrvAssumption(packageId, {
        supporting_document_id: blankToNull(mrvDraft.supporting_document_id),
        baseline_emissions_tco2e_per_year: numberOrNull(mrvDraft.baseline_emissions_tco2e_per_year),
        captured_co2_accounting_tpy: numberOrNull(mrvDraft.captured_co2_accounting_tpy),
        product_carbon_intensity_tco2e_per_ton: numberOrNull(mrvDraft.product_carbon_intensity_tco2e_per_ton),
        electricity_source: blankToNull(mrvDraft.electricity_source),
        electricity_emission_factor_tco2e_per_mwh: numberOrNull(mrvDraft.electricity_emission_factor_tco2e_per_mwh),
        methanol_pathway: blankToNull(mrvDraft.methanol_pathway),
        carbon_credit_methodology: blankToNull(mrvDraft.carbon_credit_methodology),
        verification_status: mrvDraft.verification_status,
        verifier_name: blankToNull(mrvDraft.verifier_name),
        carbon_credit_eligibility: mrvDraft.carbon_credit_eligibility,
        eligibility_basis: blankToNull(mrvDraft.eligibility_basis),
        data_status: mrvDraft.data_status,
        confidence_level: mrvDraft.confidence_level,
        notes: blankToNull(mrvDraft.notes),
      });
      setMrvDraft(EMPTY_MRV);
      await loadAll();
      setStatusMessage("MRV assumptions saved. Next: review MRV readiness and carbon intensity.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "MRV assumptions could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteMrv(assumptionId: string) {
    const confirmed = window.confirm("Delete this MRV assumption? This may change MRV readiness and carbon indicators.");
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await deletePreFeedMrvAssumption(assumptionId);
      await loadAll();
      setStatusMessage("MRV assumptions deleted.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "MRV assumptions could not be deleted.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, [packageId, scenarioId]);

  if (!packageId) {
    return (
      <article className="card offtake-mrv-empty">
        <h3>Offtake & MRV</h3>
        <p className="muted">Save or select a Pre-FEED package before adding offtake and MRV records.</p>
      </article>
    );
  }

  return (
    <section className="offtake-mrv-workspace">
      <div className="setting-card-header">
        <div>
          <h3>Offtake & MRV</h3>
          <span>{loading ? "Loading" : `${prospects.length} prospects / ${mrvAssumptions.length} MRV records`}</span>
        </div>
        <button className="button secondary" type="button" onClick={() => void loadAll()} disabled={loading}>
          <RefreshCw size={16} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <div className="offtake-mrv-summary-grid">
        <div>
          <span>Revenue</span>
          <strong>{formatNumber(offtakeSummary?.gross_revenue_usd_per_year, " USD/y")}</strong>
        </div>
        <div>
          <span>Offtake readiness</span>
          <strong>{formatPercent(offtakeSummary?.readiness_score)}</strong>
        </div>
        <div>
          <span>Carbon intensity</span>
          <strong>{formatNumber(mrvSummary?.carbon_intensity_tco2e_per_ton_methanol, " tCO2e/t", 3)}</strong>
        </div>
        <div>
          <span>Abatement</span>
          <strong>{formatNumber(mrvSummary?.abatement_tco2e_per_year, " tCO2e/y")}</strong>
        </div>
        <div>
          <span>MRV readiness</span>
          <strong>{formatPercent(mrvSummary?.readiness_score)}</strong>
        </div>
      </div>

      <div className="offtake-mrv-grid">
        <article className="card market-panel">
          <div className="setting-card-header">
            <div>
              <h3>Price Deck</h3>
              <span>{activeDeck ? activeDeck.deck_name : "No active deck"}</span>
            </div>
            <BadgeDollarSign size={18} aria-hidden="true" />
          </div>
          <div className="market-form">
            <label className="field">
              <span>Deck name</span>
              <input value={priceDraft.deck_name} onChange={(event) => updatePriceDraft("deck_name", event.target.value)} />
            </label>
            <label className="field checkbox-field">
              <span>Active</span>
              <input
                type="checkbox"
                checked={priceDraft.is_active}
                onChange={(event) => updatePriceDraft("is_active", event.target.checked)}
              />
            </label>
            <label className="field">
              <span>Methanol USD/t</span>
              <input
                type="number"
                min="0"
                value={priceDraft.methanol_price_usd_per_ton}
                onChange={(event) => updatePriceDraft("methanol_price_usd_per_ton", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Carbon USD/t</span>
              <input
                type="number"
                min="0"
                value={priceDraft.carbon_credit_price_usd_per_ton}
                onChange={(event) => updatePriceDraft("carbon_credit_price_usd_per_ton", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Electricity USD/kWh</span>
              <input
                type="number"
                min="0"
                step="0.001"
                value={priceDraft.electricity_price_usd_per_kwh}
                onChange={(event) => updatePriceDraft("electricity_price_usd_per_kwh", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Hydrogen USD/kg</span>
              <input
                type="number"
                min="0"
                value={priceDraft.hydrogen_price_usd_per_kg}
                onChange={(event) => updatePriceDraft("hydrogen_price_usd_per_kg", event.target.value)}
              />
            </label>
            <label className="field">
              <span>IDR/USD</span>
              <input
                type="number"
                min="0"
                value={priceDraft.exchange_rate_idr_usd}
                onChange={(event) => updatePriceDraft("exchange_rate_idr_usd", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Escalation %</span>
              <input
                type="number"
                min="0"
                value={priceDraft.escalation_percent}
                onChange={(event) => updatePriceDraft("escalation_percent", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Data status</span>
              <select value={priceDraft.data_status} onChange={(event) => updatePriceDraft("data_status", event.target.value as DataStatus)}>
                {DATA_STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>{labelFor(status)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Confidence</span>
              <select
                value={priceDraft.confidence_level}
                onChange={(event) => updatePriceDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>{labelFor(level)}</option>
                ))}
              </select>
            </label>
            <label className="field market-form-wide">
              <span>Notes</span>
              <input value={priceDraft.notes} onChange={(event) => updatePriceDraft("notes", event.target.value)} />
            </label>
            <button className="button" type="button" onClick={() => void handleSavePriceDeck()} disabled={busy}>
              <Save size={16} aria-hidden="true" />
              Save Deck
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table market-table">
              <thead>
                <tr>
                  <th>Deck</th>
                  <th>Methanol</th>
                  <th>Carbon</th>
                  <th>Confidence</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {priceDecks.map((deck) => (
                  <tr className={deck.is_active ? "active" : ""} key={deck.id}>
                    <td>
                      <button className="table-link" type="button" onClick={() => void handleActivateDeck(deck.id)} disabled={deck.is_active || busy}>
                        {deck.deck_name}
                      </button>
                      <span className="table-subtext">{deck.is_active ? "Active" : "Inactive"}</span>
                    </td>
                    <td>{formatNumber(deck.methanol_price_usd_per_ton, " USD/t")}</td>
                    <td>{formatNumber(deck.carbon_credit_price_usd_per_ton, " USD/t")}</td>
                    <td>{labelFor(deck.confidence_level)}</td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete price deck"
                        title="Delete price deck"
                        onClick={() => void handleDeleteDeck(deck.id)}
                        disabled={busy}
                      >
                        <Trash2 size={16} aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="card market-panel">
          <div className="setting-card-header">
            <div>
              <h3>Offtake Prospects</h3>
              <span>{formatNumber(offtakeSummary?.methanol_volume_committed_tpy, " t/y")} committed</span>
            </div>
            <Plus size={18} aria-hidden="true" />
          </div>
          <div className="market-form">
            <label className="field">
              <span>Counterparty</span>
              <input value={offtakeDraft.counterparty_name} onChange={(event) => updateOfftakeDraft("counterparty_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Product</span>
              <select value={offtakeDraft.product} onChange={(event) => updateOfftakeDraft("product", event.target.value as PreFeedOfftakeProduct)}>
                {PRODUCTS.map((product) => (
                  <option key={product} value={product}>{labelFor(product)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Status</span>
              <select value={offtakeDraft.status} onChange={(event) => updateOfftakeDraft("status", event.target.value as PreFeedOfftakeStatus)}>
                {OFFTAKE_STATUSES.map((status) => (
                  <option key={status} value={status}>{labelFor(status)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Data status</span>
              <select value={offtakeDraft.data_status} onChange={(event) => updateOfftakeDraft("data_status", event.target.value as DataStatus)}>
                {DATA_STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>{labelFor(status)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Volume t/y</span>
              <input type="number" min="0" value={offtakeDraft.target_volume_tpy} onChange={(event) => updateOfftakeDraft("target_volume_tpy", event.target.value)} />
            </label>
            <label className="field">
              <span>Term years</span>
              <input type="number" min="0" value={offtakeDraft.term_years} onChange={(event) => updateOfftakeDraft("term_years", event.target.value)} />
            </label>
            <label className="field">
              <span>Price USD/t</span>
              <input type="number" min="0" value={offtakeDraft.price_usd_per_ton} onChange={(event) => updateOfftakeDraft("price_usd_per_ton", event.target.value)} />
            </label>
            <label className="field">
              <span>Pricing basis</span>
              <input value={offtakeDraft.pricing_basis} onChange={(event) => updateOfftakeDraft("pricing_basis", event.target.value)} />
            </label>
            <label className="field">
              <span>Document</span>
              <select
                value={offtakeDraft.supporting_document_id}
                onChange={(event) => updateOfftakeDraft("supporting_document_id", event.target.value)}
              >
                <option value="">None</option>
                {documents.map((document) => (
                  <option key={document.id} value={document.id}>{document.original_filename}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Confidence</span>
              <select
                value={offtakeDraft.confidence_level}
                onChange={(event) => updateOfftakeDraft("confidence_level", event.target.value as ConfidenceLevel)}
              >
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>{labelFor(level)}</option>
                ))}
              </select>
            </label>
            <button className="button" type="button" onClick={() => void handleSaveOfftake()} disabled={busy}>
              <Plus size={16} aria-hidden="true" />
              Add Offtake
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table market-table">
              <thead>
                <tr>
                  <th>Counterparty</th>
                  <th>Product</th>
                  <th>Volume</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((prospect) => (
                  <tr key={prospect.id}>
                    <td>
                      <strong>{prospect.counterparty_name}</strong>
                      <span className="table-subtext">{prospect.supporting_document?.original_filename ?? "No document"}</span>
                    </td>
                    <td>{labelFor(prospect.product)}</td>
                    <td>{formatNumber(prospect.target_volume_tpy, " t/y")}</td>
                    <td>{labelFor(prospect.status)}</td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete offtake prospect"
                        title="Delete offtake prospect"
                        onClick={() => void handleDeleteOfftake(prospect.id)}
                        disabled={busy}
                      >
                        <Trash2 size={16} aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <div className="offtake-mrv-grid">
        <article className="card market-panel">
          <div className="setting-card-header">
            <div>
              <h3>MRV Assumptions</h3>
              <span>{mrvSummary?.carbon_credit_eligibility ? labelFor(mrvSummary.carbon_credit_eligibility) : "Unknown eligibility"}</span>
            </div>
            <Leaf size={18} aria-hidden="true" />
          </div>
          <div className="market-form">
            <label className="field">
              <span>Baseline tCO2e/y</span>
              <input
                type="number"
                min="0"
                value={mrvDraft.baseline_emissions_tco2e_per_year}
                onChange={(event) => updateMrvDraft("baseline_emissions_tco2e_per_year", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Captured tCO2/y</span>
              <input
                type="number"
                min="0"
                value={mrvDraft.captured_co2_accounting_tpy}
                onChange={(event) => updateMrvDraft("captured_co2_accounting_tpy", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Intensity tCO2e/t</span>
              <input
                type="number"
                min="0"
                step="0.001"
                value={mrvDraft.product_carbon_intensity_tco2e_per_ton}
                onChange={(event) => updateMrvDraft("product_carbon_intensity_tco2e_per_ton", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Electricity source</span>
              <input value={mrvDraft.electricity_source} onChange={(event) => updateMrvDraft("electricity_source", event.target.value)} />
            </label>
            <label className="field">
              <span>EF tCO2e/MWh</span>
              <input
                type="number"
                min="0"
                step="0.001"
                value={mrvDraft.electricity_emission_factor_tco2e_per_mwh}
                onChange={(event) => updateMrvDraft("electricity_emission_factor_tco2e_per_mwh", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Methanol pathway</span>
              <input value={mrvDraft.methanol_pathway} onChange={(event) => updateMrvDraft("methanol_pathway", event.target.value)} />
            </label>
            <label className="field">
              <span>Methodology</span>
              <input
                value={mrvDraft.carbon_credit_methodology}
                onChange={(event) => updateMrvDraft("carbon_credit_methodology", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Verification</span>
              <select
                value={mrvDraft.verification_status}
                onChange={(event) => updateMrvDraft("verification_status", event.target.value as PreFeedMrvVerificationStatus)}
              >
                {VERIFICATION_STATUSES.map((status) => (
                  <option key={status} value={status}>{labelFor(status)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Eligibility</span>
              <select
                value={mrvDraft.carbon_credit_eligibility}
                onChange={(event) => updateMrvDraft("carbon_credit_eligibility", event.target.value as PreFeedCarbonCreditEligibility)}
              >
                {ELIGIBILITY_OPTIONS.map((eligibility) => (
                  <option key={eligibility} value={eligibility}>{labelFor(eligibility)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Verifier</span>
              <input value={mrvDraft.verifier_name} onChange={(event) => updateMrvDraft("verifier_name", event.target.value)} />
            </label>
            <label className="field">
              <span>Data status</span>
              <select value={mrvDraft.data_status} onChange={(event) => updateMrvDraft("data_status", event.target.value as DataStatus)}>
                {DATA_STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>{labelFor(status)}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Document</span>
              <select value={mrvDraft.supporting_document_id} onChange={(event) => updateMrvDraft("supporting_document_id", event.target.value)}>
                <option value="">None</option>
                {documents.map((document) => (
                  <option key={document.id} value={document.id}>{document.original_filename}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Confidence</span>
              <select value={mrvDraft.confidence_level} onChange={(event) => updateMrvDraft("confidence_level", event.target.value as ConfidenceLevel)}>
                {CONFIDENCE_OPTIONS.map((level) => (
                  <option key={level} value={level}>{labelFor(level)}</option>
                ))}
              </select>
            </label>
            <label className="field market-form-wide">
              <span>Eligibility basis</span>
              <input value={mrvDraft.eligibility_basis} onChange={(event) => updateMrvDraft("eligibility_basis", event.target.value)} />
            </label>
            <button className="button" type="button" onClick={() => void handleSaveMrv()} disabled={busy}>
              <Save size={16} aria-hidden="true" />
              Save MRV
            </button>
          </div>
          <div className="table-wrap">
            <table className="data-table market-table">
              <thead>
                <tr>
                  <th>MRV Record</th>
                  <th>Verification</th>
                  <th>Eligibility</th>
                  <th>Confidence</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {mrvAssumptions.map((assumption) => (
                  <tr key={assumption.id}>
                    <td>
                      <strong>{assumption.carbon_credit_methodology ?? "MRV assumption"}</strong>
                      <span className="table-subtext">{assumption.supporting_document?.original_filename ?? "No document"}</span>
                    </td>
                    <td>{labelFor(assumption.verification_status)}</td>
                    <td>{labelFor(assumption.carbon_credit_eligibility)}</td>
                    <td>{labelFor(assumption.confidence_level)}</td>
                    <td>
                      <button
                        className="icon-button"
                        type="button"
                        aria-label="Delete MRV assumptions"
                        title="Delete MRV assumptions"
                        onClick={() => void handleDeleteMrv(assumption.id)}
                        disabled={busy}
                      >
                        <Trash2 size={16} aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <aside className="market-side">
          <article className="card market-gap-panel">
            <div className="setting-card-header">
              <div>
                <h3>Offtake Gaps</h3>
                <span>{offtakeGaps.length} open</span>
              </div>
              <AlertTriangle size={18} aria-hidden="true" />
            </div>
            <div className="prefeed-gap-list">
              {offtakeSummary?.warnings.map((warning) => <div className="notice" key={warning}>{warning}</div>)}
              {offtakeGaps.map((gap) => (
                <div className="data-gap-row" key={`offtake-${gap.missing_data_name}`}>
                  <strong>{gap.missing_data_name}</strong>
                  <span>{gap.owner} / {labelFor(gap.priority_level)} priority</span>
                  <p>{gap.recommendation}</p>
                </div>
              ))}
              {offtakeGaps.length === 0 ? <p className="muted">No offtake gaps.</p> : null}
            </div>
          </article>

          <article className="card market-gap-panel">
            <div className="setting-card-header">
              <div>
                <h3>MRV Gaps</h3>
                <span>{mrvGaps.length} open</span>
              </div>
              <AlertTriangle size={18} aria-hidden="true" />
            </div>
            <div className="prefeed-gap-list">
              {mrvSummary?.warnings.map((warning) => <div className="notice" key={warning}>{warning}</div>)}
              {mrvGaps.map((gap) => (
                <div className="data-gap-row" key={`mrv-${gap.missing_data_name}`}>
                  <strong>{gap.missing_data_name}</strong>
                  <span>{gap.owner} / {labelFor(gap.priority_level)} priority</span>
                  <p>{gap.recommendation}</p>
                </div>
              ))}
              {mrvGaps.length === 0 ? <p className="muted">No MRV gaps.</p> : null}
            </div>
          </article>
        </aside>
      </div>
    </section>
  );
}
