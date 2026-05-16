"use client";

import { Save } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import type { FinancialAssumption, FinancialAssumptionPayload } from "@/types/financial-assumption";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";

const emptyDraft: Required<FinancialAssumptionPayload> = {
  methanol_price_usd_per_ton: null,
  grey_methanol_price_usd_per_ton: null,
  hydrogen_price_usd_per_kg: null,
  electricity_price_usd_per_kwh: null,
  carbon_credit_price_idr_per_ton: null,
  exchange_rate_idr_usd: null,
  discount_rate: null,
  tax_rate: null,
  capex_capture_usd: null,
  capex_electrolyzer_usd: null,
  capex_methanol_plant_usd: null,
  capex_storage_port_usd: null,
  opex_percent_capex: null,
  data_status: "benchmark",
  confidence_level: "low",
};

function assumptionToDraft(record?: FinancialAssumption | null): Required<FinancialAssumptionPayload> {
  if (!record) {
    return emptyDraft;
  }
  return {
    methanol_price_usd_per_ton: record.methanol_price_usd_per_ton,
    grey_methanol_price_usd_per_ton: record.grey_methanol_price_usd_per_ton,
    hydrogen_price_usd_per_kg: record.hydrogen_price_usd_per_kg,
    electricity_price_usd_per_kwh: record.electricity_price_usd_per_kwh,
    carbon_credit_price_idr_per_ton: record.carbon_credit_price_idr_per_ton,
    exchange_rate_idr_usd: record.exchange_rate_idr_usd,
    discount_rate: record.discount_rate,
    tax_rate: record.tax_rate,
    capex_capture_usd: record.capex_capture_usd,
    capex_electrolyzer_usd: record.capex_electrolyzer_usd,
    capex_methanol_plant_usd: record.capex_methanol_plant_usd,
    capex_storage_port_usd: record.capex_storage_port_usd,
    opex_percent_capex: record.opex_percent_capex,
    data_status: record.data_status,
    confidence_level: record.confidence_level,
  };
}

function parseNumber(value: string): number | null {
  if (value.trim() === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function numberValue(value: number | null | undefined): string {
  return value === null || value === undefined ? "" : String(value);
}

type NumericField = Exclude<keyof Required<FinancialAssumptionPayload>, "data_status" | "confidence_level">;

const financialFields: Array<{ key: NumericField; label: string; step?: string }> = [
  { key: "methanol_price_usd_per_ton", label: "Methanol price USD/t" },
  { key: "grey_methanol_price_usd_per_ton", label: "Grey methanol USD/t" },
  { key: "hydrogen_price_usd_per_kg", label: "Hydrogen USD/kg" },
  { key: "electricity_price_usd_per_kwh", label: "Electricity USD/kWh", step: "0.01" },
  { key: "carbon_credit_price_idr_per_ton", label: "Carbon credit IDR/tCO2" },
  { key: "exchange_rate_idr_usd", label: "Exchange rate IDR/USD" },
  { key: "discount_rate", label: "Discount rate", step: "0.01" },
  { key: "tax_rate", label: "Tax rate", step: "0.01" },
  { key: "capex_capture_usd", label: "CAPEX capture USD" },
  { key: "capex_electrolyzer_usd", label: "CAPEX electrolyzer USD" },
  { key: "capex_methanol_plant_usd", label: "CAPEX methanol plant USD" },
  { key: "capex_storage_port_usd", label: "CAPEX storage/port USD" },
  { key: "opex_percent_capex", label: "OPEX % CAPEX", step: "0.01" },
];

type FinancialAssumptionsFormProps = {
  assumption: FinancialAssumption | null;
  disabled?: boolean;
  onSave: (payload: FinancialAssumptionPayload) => Promise<void>;
};

export function FinancialAssumptionsForm({ assumption, disabled = false, onSave }: FinancialAssumptionsFormProps) {
  const [draft, setDraft] = useState<Required<FinancialAssumptionPayload>>(() => assumptionToDraft(assumption));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setDraft(assumptionToDraft(assumption));
  }, [assumption]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSave(draft);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="scenario-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        {financialFields.map((field) => (
          <label className="field" key={field.key}>
            <span>{field.label}</span>
            <input
              disabled={disabled || saving}
              inputMode="decimal"
              min="0"
              step={field.step ?? "any"}
              type="number"
              value={numberValue(draft[field.key])}
              onChange={(event) => setDraft({ ...draft, [field.key]: parseNumber(event.target.value) })}
            />
          </label>
        ))}
        <label className="field">
          <span>Data status</span>
          <select
            disabled={disabled || saving}
            value={draft.data_status}
            onChange={(event) => setDraft({ ...draft, data_status: event.target.value as DataStatus })}
          >
            <option value="actual">actual</option>
            <option value="estimated">estimated</option>
            <option value="benchmark">benchmark</option>
            <option value="user_assumption">user_assumption</option>
            <option value="partner_supplied">partner_supplied</option>
            <option value="unknown">unknown</option>
          </select>
        </label>
        <label className="field">
          <span>Confidence</span>
          <select
            disabled={disabled || saving}
            value={draft.confidence_level}
            onChange={(event) => setDraft({ ...draft, confidence_level: event.target.value as ConfidenceLevel })}
          >
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
            <option value="unknown">unknown</option>
          </select>
        </label>
      </div>
      <div className="inline-actions">
        <button className="button" disabled={disabled || saving} type="submit">
          <Save size={16} aria-hidden="true" />
          Save Financial Assumptions
        </button>
      </div>
    </form>
  );
}
