"use client";

import { Save, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import type { ConfidenceLevel, DataStatus } from "@/types/plant";
import type { BusinessScenario, BusinessScenarioPayload, BusinessScheme } from "@/types/scenario";

const schemeLabels: Record<BusinessScheme, string> = {
  access: "WIZ Access",
  align: "WIZ Align",
  augment: "WIZ Augment",
};

const defaultDraft: BusinessScenarioPayload = {
  scenario_name: "WIZ Align Base Case",
  scheme: "align",
  pln_ownership_percent: 25,
  partner_capex_responsibility_percent: 100,
  pln_capex_responsibility_percent: 0,
  revenue_model: "equity_share_plus_asset_revenue",
  capture_rate: 0.85,
  process_efficiency: 0.60,
  data_status: "user_assumption",
  confidence_level: "medium",
};

function scenarioToDraft(scenario?: BusinessScenario | null): BusinessScenarioPayload {
  if (!scenario) {
    return defaultDraft;
  }
  return {
    scenario_name: scenario.scenario_name,
    scheme: scenario.scheme,
    pln_ownership_percent: scenario.pln_ownership_percent,
    partner_capex_responsibility_percent: scenario.partner_capex_responsibility_percent,
    pln_capex_responsibility_percent: scenario.pln_capex_responsibility_percent,
    revenue_model: scenario.revenue_model,
    capture_rate: scenario.capture_rate,
    process_efficiency: scenario.process_efficiency,
    data_status: scenario.data_status,
    confidence_level: scenario.confidence_level,
  };
}

function parseNumber(value: string): number | null {
  if (value.trim() === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function numberValue(value: number | null): string {
  return value === null ? "" : String(value);
}

type ScenarioFormProps = {
  mode: "create" | "edit";
  scenario?: BusinessScenario | null;
  disabled?: boolean;
  onSubmit: (payload: BusinessScenarioPayload) => Promise<void>;
  onDelete?: () => Promise<void>;
};

export function ScenarioForm({ mode, scenario, disabled = false, onSubmit, onDelete }: ScenarioFormProps) {
  const [draft, setDraft] = useState<BusinessScenarioPayload>(() => scenarioToDraft(scenario));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setDraft(scenarioToDraft(scenario));
  }, [scenario]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSubmit(draft);
      if (mode === "create") {
        setDraft(defaultDraft);
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="scenario-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <label className="field">
          <span>Scenario name</span>
          <input
            disabled={disabled || saving}
            maxLength={160}
            required
            value={draft.scenario_name}
            onChange={(event) => setDraft({ ...draft, scenario_name: event.target.value })}
          />
        </label>
        <label className="field">
          <span>Scheme</span>
          <select
            disabled={disabled || saving}
            value={draft.scheme}
            onChange={(event) => setDraft({ ...draft, scheme: event.target.value as BusinessScheme })}
          >
            {Object.entries(schemeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Revenue model</span>
          <input
            disabled={disabled || saving}
            value={draft.revenue_model ?? ""}
            onChange={(event) => setDraft({ ...draft, revenue_model: event.target.value || null })}
          />
        </label>
        <label className="field">
          <span>PLN ownership %</span>
          <input
            disabled={disabled || saving}
            inputMode="decimal"
            type="number"
            value={numberValue(draft.pln_ownership_percent)}
            onChange={(event) => setDraft({ ...draft, pln_ownership_percent: parseNumber(event.target.value) })}
          />
        </label>
        <label className="field">
          <span>Partner CAPEX %</span>
          <input
            disabled={disabled || saving}
            inputMode="decimal"
            type="number"
            value={numberValue(draft.partner_capex_responsibility_percent)}
            onChange={(event) =>
              setDraft({ ...draft, partner_capex_responsibility_percent: parseNumber(event.target.value) })
            }
          />
        </label>
        <label className="field">
          <span>PLN CAPEX %</span>
          <input
            disabled={disabled || saving}
            inputMode="decimal"
            type="number"
            value={numberValue(draft.pln_capex_responsibility_percent)}
            onChange={(event) =>
              setDraft({ ...draft, pln_capex_responsibility_percent: parseNumber(event.target.value) })
            }
          />
        </label>
        <label className="field">
          <span>Capture rate</span>
          <input
            disabled={disabled || saving}
            inputMode="decimal"
            max="1"
            min="0"
            step="0.01"
            type="number"
            value={numberValue(draft.capture_rate)}
            onChange={(event) => setDraft({ ...draft, capture_rate: parseNumber(event.target.value) })}
          />
        </label>
        <label className="field">
          <span>Process efficiency</span>
          <input
            disabled={disabled || saving}
            inputMode="decimal"
            max="1"
            min="0"
            step="0.01"
            type="number"
            value={numberValue(draft.process_efficiency)}
            onChange={(event) => setDraft({ ...draft, process_efficiency: parseNumber(event.target.value) })}
          />
        </label>
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
          {mode === "create" ? "Create Scenario" : "Save Scenario"}
        </button>
        {mode === "edit" && onDelete ? (
          <button
            className="button danger"
            disabled={disabled || saving}
            type="button"
            onClick={() => void onDelete()}
          >
            <Trash2 size={16} aria-hidden="true" />
            Delete
          </button>
        ) : null}
      </div>
    </form>
  );
}
