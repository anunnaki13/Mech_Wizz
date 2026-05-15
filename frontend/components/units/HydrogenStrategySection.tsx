"use client";

import { useState } from "react";

import { saveHydrogenStrategy } from "@/lib/api";
import type { HydrogenStrategy } from "@/types/hydrogen-strategy";

type FormState = {
  existing_h2_available: string;
  h2_strategy: string;
  h2_cost_case: string;
  h2_cost_usd_per_kg: string;
  h2_readiness_score: string;
  data_status: HydrogenStrategy["data_status"];
  confidence_level: HydrogenStrategy["confidence_level"];
};

function toForm(record: HydrogenStrategy | null): FormState {
  return {
    existing_h2_available: record?.existing_h2_available === null || record?.existing_h2_available === undefined ? "" : String(record.existing_h2_available),
    h2_strategy: record?.h2_strategy ?? "",
    h2_cost_case: record?.h2_cost_case ?? "",
    h2_cost_usd_per_kg: record?.h2_cost_usd_per_kg?.toString() ?? "",
    h2_readiness_score: record?.h2_readiness_score?.toString() ?? "",
    data_status: record?.data_status ?? "unknown",
    confidence_level: record?.confidence_level ?? "unknown",
  };
}

function parseNumber(value: string) {
  return value.trim() === "" ? null : Number(value);
}

function parseBoolean(value: string) {
  if (value === "") {
    return null;
  }
  return value === "true";
}

export function HydrogenStrategySection({
  plantId,
  initialHydrogenStrategy,
}: {
  plantId: string;
  initialHydrogenStrategy: HydrogenStrategy | null;
}) {
  const [record, setRecord] = useState(initialHydrogenStrategy);
  const [form, setForm] = useState<FormState>(toForm(initialHydrogenStrategy));
  const [editing, setEditing] = useState(initialHydrogenStrategy === null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      const saved = await saveHydrogenStrategy(
        plantId,
        {
          existing_h2_available: parseBoolean(form.existing_h2_available),
          h2_strategy: form.h2_strategy || null,
          h2_cost_case: form.h2_cost_case || null,
          h2_cost_usd_per_kg: parseNumber(form.h2_cost_usd_per_kg),
          h2_readiness_score: parseNumber(form.h2_readiness_score),
          data_status: form.data_status,
          confidence_level: form.confidence_level,
        },
        record?.id,
      );
      setRecord(saved);
      setForm(toForm(saved));
      setEditing(false);
    } catch {
      setError("Unable to save hydrogen strategy.");
    }
  }

  return (
    <section className="card">
      <div className="page-header" style={{ marginBottom: 12 }}>
        <div>
          <h3>Hydrogen Strategy</h3>
          <p>Hydrogen availability and supply strategy inputs for future scenario work.</p>
        </div>
        <button className="button" type="button" onClick={() => setEditing((value) => !value)}>
          {editing ? "Close" : "Edit"}
        </button>
      </div>

      <div className="chip-row">
        <span className="chip">data_status: {record?.data_status ?? form.data_status}</span>
        <span className="chip">confidence_level: {record?.confidence_level ?? form.confidence_level}</span>
      </div>

      {editing ? (
        <form className="form-grid" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="existing_h2_available">Existing H2 available</label>
            <select id="existing_h2_available" value={form.existing_h2_available} onChange={(event) => setForm((current) => ({ ...current, existing_h2_available: event.target.value }))}>
              <option value="">unknown</option>
              <option value="true">yes</option>
              <option value="false">no</option>
            </select>
          </div>
          <Field label="H2 strategy" value={form.h2_strategy} onChange={(value) => setForm((current) => ({ ...current, h2_strategy: value }))} />
          <Field label="H2 cost case" value={form.h2_cost_case} onChange={(value) => setForm((current) => ({ ...current, h2_cost_case: value }))} />
          <Field label="H2 cost usd per kg" value={form.h2_cost_usd_per_kg} onChange={(value) => setForm((current) => ({ ...current, h2_cost_usd_per_kg: value }))} />
          <Field label="H2 readiness score" value={form.h2_readiness_score} onChange={(value) => setForm((current) => ({ ...current, h2_readiness_score: value }))} />
          <SelectField label="data_status" value={form.data_status} values={["actual", "estimated", "benchmark", "user_assumption", "unknown", "partner_supplied"]} onChange={(value) => setForm((current) => ({ ...current, data_status: value as FormState["data_status"] }))} />
          <SelectField label="confidence_level" value={form.confidence_level} values={["high", "medium", "low", "unknown"]} onChange={(value) => setForm((current) => ({ ...current, confidence_level: value as FormState["confidence_level"] }))} />
          <div className="field">
            <label>&nbsp;</label>
            <button className="button" type="submit">Save</button>
          </div>
        </form>
      ) : (
        <div className="detail-list" style={{ marginTop: 14 }}>
          <div className="detail-row"><span>Existing H2 available</span><span>{record?.existing_h2_available === null || record?.existing_h2_available === undefined ? "Unknown" : record.existing_h2_available ? "Yes" : "No"}</span></div>
          <div className="detail-row"><span>H2 strategy</span><span>{record?.h2_strategy ?? "Unknown"}</span></div>
          <div className="detail-row"><span>H2 cost case</span><span>{record?.h2_cost_case ?? "Unknown"}</span></div>
          <div className="detail-row"><span>H2 readiness score</span><span>{record?.h2_readiness_score ?? "Unknown"}</span></div>
        </div>
      )}

      {error ? <p className="notice">{error}</p> : null}
    </section>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input id={id} value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function SelectField({
  label,
  value,
  values,
  onChange,
}: {
  label: string;
  value: string;
  values: string[];
  onChange: (value: string) => void;
}) {
  return (
    <div className="field">
      <label htmlFor={label}>{label}</label>
      <select id={label} value={value} onChange={(event) => onChange(event.target.value)}>
        {values.map((item) => (
          <option value={item} key={item}>{item}</option>
        ))}
      </select>
    </div>
  );
}
