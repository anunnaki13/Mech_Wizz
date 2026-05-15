"use client";

import { useState } from "react";

import { saveSiteReadiness } from "@/lib/api";
import type { SiteReadiness } from "@/types/site-readiness";

type FormState = {
  available_land_ha: string;
  land_status: string;
  distance_to_stack_km: string;
  has_port_or_jetty: string;
  distance_to_port_km: string;
  port_capacity_dwt: string;
  road_access: string;
  water_availability: string;
  power_availability: string;
  utility_readiness: string;
  permit_risk: string;
  social_risk: string;
  data_status: SiteReadiness["data_status"];
  confidence_level: SiteReadiness["confidence_level"];
};

function toForm(record: SiteReadiness | null): FormState {
  return {
    available_land_ha: record?.available_land_ha?.toString() ?? "",
    land_status: record?.land_status ?? "",
    distance_to_stack_km: record?.distance_to_stack_km?.toString() ?? "",
    has_port_or_jetty: record?.has_port_or_jetty === null || record?.has_port_or_jetty === undefined ? "" : String(record.has_port_or_jetty),
    distance_to_port_km: record?.distance_to_port_km?.toString() ?? "",
    port_capacity_dwt: record?.port_capacity_dwt?.toString() ?? "",
    road_access: record?.road_access ?? "",
    water_availability: record?.water_availability ?? "",
    power_availability: record?.power_availability ?? "",
    utility_readiness: record?.utility_readiness ?? "",
    permit_risk: record?.permit_risk ?? "",
    social_risk: record?.social_risk ?? "",
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

export function SiteReadinessSection({
  plantId,
  initialSiteReadiness,
}: {
  plantId: string;
  initialSiteReadiness: SiteReadiness | null;
}) {
  const [record, setRecord] = useState(initialSiteReadiness);
  const [form, setForm] = useState<FormState>(toForm(initialSiteReadiness));
  const [editing, setEditing] = useState(initialSiteReadiness === null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      const saved = await saveSiteReadiness(
        plantId,
        {
          available_land_ha: parseNumber(form.available_land_ha),
          land_status: form.land_status || null,
          distance_to_stack_km: parseNumber(form.distance_to_stack_km),
          has_port_or_jetty: parseBoolean(form.has_port_or_jetty),
          distance_to_port_km: parseNumber(form.distance_to_port_km),
          port_capacity_dwt: parseNumber(form.port_capacity_dwt),
          road_access: form.road_access || null,
          water_availability: form.water_availability || null,
          power_availability: form.power_availability || null,
          utility_readiness: form.utility_readiness || null,
          permit_risk: form.permit_risk || null,
          social_risk: form.social_risk || null,
          data_status: form.data_status,
          confidence_level: form.confidence_level,
        },
        record?.id,
      );
      setRecord(saved);
      setForm(toForm(saved));
      setEditing(false);
    } catch {
      setError("Unable to save site readiness.");
    }
  }

  return (
    <section className="card">
      <div className="page-header" style={{ marginBottom: 12 }}>
        <div>
          <h3>Site Readiness</h3>
          <p>Land, access, utility, and risk inputs for the unit location.</p>
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
          <Field label="Available land ha" value={form.available_land_ha} onChange={(value) => setForm((current) => ({ ...current, available_land_ha: value }))} />
          <Field label="Land status" value={form.land_status} onChange={(value) => setForm((current) => ({ ...current, land_status: value }))} />
          <Field label="Stack distance km" value={form.distance_to_stack_km} onChange={(value) => setForm((current) => ({ ...current, distance_to_stack_km: value }))} />
          <div className="field">
            <label htmlFor="has_port_or_jetty">Port or jetty</label>
            <select id="has_port_or_jetty" value={form.has_port_or_jetty} onChange={(event) => setForm((current) => ({ ...current, has_port_or_jetty: event.target.value }))}>
              <option value="">unknown</option>
              <option value="true">yes</option>
              <option value="false">no</option>
            </select>
          </div>
          <Field label="Port distance km" value={form.distance_to_port_km} onChange={(value) => setForm((current) => ({ ...current, distance_to_port_km: value }))} />
          <Field label="Port capacity dwt" value={form.port_capacity_dwt} onChange={(value) => setForm((current) => ({ ...current, port_capacity_dwt: value }))} />
          <Field label="Road access" value={form.road_access} onChange={(value) => setForm((current) => ({ ...current, road_access: value }))} />
          <Field label="Water availability" value={form.water_availability} onChange={(value) => setForm((current) => ({ ...current, water_availability: value }))} />
          <Field label="Power availability" value={form.power_availability} onChange={(value) => setForm((current) => ({ ...current, power_availability: value }))} />
          <Field label="Utility readiness" value={form.utility_readiness} onChange={(value) => setForm((current) => ({ ...current, utility_readiness: value }))} />
          <Field label="Permit risk" value={form.permit_risk} onChange={(value) => setForm((current) => ({ ...current, permit_risk: value }))} />
          <Field label="Social risk" value={form.social_risk} onChange={(value) => setForm((current) => ({ ...current, social_risk: value }))} />
          <SelectField label="data_status" value={form.data_status} values={["actual", "estimated", "benchmark", "user_assumption", "unknown", "partner_supplied"]} onChange={(value) => setForm((current) => ({ ...current, data_status: value as FormState["data_status"] }))} />
          <SelectField label="confidence_level" value={form.confidence_level} values={["high", "medium", "low", "unknown"]} onChange={(value) => setForm((current) => ({ ...current, confidence_level: value as FormState["confidence_level"] }))} />
          <div className="field">
            <label>&nbsp;</label>
            <button className="button" type="submit">Save</button>
          </div>
        </form>
      ) : (
        <div className="detail-list" style={{ marginTop: 14 }}>
          <div className="detail-row"><span>Available land</span><span>{record?.available_land_ha ?? "Unknown"} ha</span></div>
          <div className="detail-row"><span>Land status</span><span>{record?.land_status ?? "Unknown"}</span></div>
          <div className="detail-row"><span>Utility readiness</span><span>{record?.utility_readiness ?? "Unknown"}</span></div>
          <div className="detail-row"><span>Permit risk</span><span>{record?.permit_risk ?? "Unknown"}</span></div>
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
