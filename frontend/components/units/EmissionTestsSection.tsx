"use client";

import { useState } from "react";

import { createEmissionTest } from "@/lib/api";
import type { EmissionTest } from "@/types/emission-test";

type FormState = {
  stack_id: string;
  co2_percent_dry: string;
  gas_velocity_m_s: string;
  flue_gas_temperature_c: string;
  data_status: EmissionTest["data_status"];
  confidence_level: EmissionTest["confidence_level"];
};

const emptyForm: FormState = {
  stack_id: "",
  co2_percent_dry: "",
  gas_velocity_m_s: "",
  flue_gas_temperature_c: "",
  data_status: "actual",
  confidence_level: "medium",
};

function formatValue(value: number | null, suffix = "") {
  if (value === null) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}${suffix}`;
}

function parseNumber(value: string) {
  return value.trim() === "" ? null : Number(value);
}

export function EmissionTestsSection({
  plantId,
  initialEmissionTests,
}: {
  plantId: string;
  initialEmissionTests: EmissionTest[];
}) {
  const [emissionTests, setEmissionTests] = useState(initialEmissionTests);
  const [formOpen, setFormOpen] = useState(false);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      const created = await createEmissionTest(plantId, {
        stack_id: form.stack_id,
        co2_percent_dry: parseNumber(form.co2_percent_dry),
        gas_velocity_m_s: parseNumber(form.gas_velocity_m_s),
        flue_gas_temperature_c: parseNumber(form.flue_gas_temperature_c),
        data_status: form.data_status,
        confidence_level: form.confidence_level,
      });
      setEmissionTests((current) => [...current, created]);
      setForm(emptyForm);
      setFormOpen(false);
    } catch {
      setError("Unable to create emission test record.");
    }
  }

  return (
    <section className="card">
      <div className="page-header" style={{ marginBottom: 12 }}>
        <div>
          <h3>Emission Tests</h3>
          <p>Stack-level Phase 1 inputs stored without scenario calculations.</p>
        </div>
        <button className="button" type="button" onClick={() => setFormOpen((value) => !value)}>
          Add Emission Test
        </button>
      </div>

      {formOpen ? (
        <form onSubmit={handleSubmit} className="form-grid">
          <div className="field">
            <label htmlFor="stack_id">Stack ID</label>
            <input
              id="stack_id"
              required
              value={form.stack_id}
              onChange={(event) => setForm((current) => ({ ...current, stack_id: event.target.value }))}
            />
          </div>
          <div className="field">
            <label htmlFor="co2_percent_dry">CO2 dry %</label>
            <input
              id="co2_percent_dry"
              inputMode="decimal"
              value={form.co2_percent_dry}
              onChange={(event) => setForm((current) => ({ ...current, co2_percent_dry: event.target.value }))}
            />
          </div>
          <div className="field">
            <label htmlFor="gas_velocity_m_s">Velocity m/s</label>
            <input
              id="gas_velocity_m_s"
              inputMode="decimal"
              value={form.gas_velocity_m_s}
              onChange={(event) => setForm((current) => ({ ...current, gas_velocity_m_s: event.target.value }))}
            />
          </div>
          <div className="field">
            <label htmlFor="flue_gas_temperature_c">Temperature C</label>
            <input
              id="flue_gas_temperature_c"
              inputMode="decimal"
              value={form.flue_gas_temperature_c}
              onChange={(event) =>
                setForm((current) => ({ ...current, flue_gas_temperature_c: event.target.value }))
              }
            />
          </div>
          <div className="field">
            <label htmlFor="data_status">data_status</label>
            <select
              id="data_status"
              value={form.data_status}
              onChange={(event) =>
                setForm((current) => ({ ...current, data_status: event.target.value as FormState["data_status"] }))
              }
            >
              <option value="actual">actual</option>
              <option value="estimated">estimated</option>
              <option value="benchmark">benchmark</option>
              <option value="user_assumption">user_assumption</option>
              <option value="unknown">unknown</option>
              <option value="partner_supplied">partner_supplied</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="confidence_level">confidence_level</label>
            <select
              id="confidence_level"
              value={form.confidence_level}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  confidence_level: event.target.value as FormState["confidence_level"],
                }))
              }
            >
              <option value="high">high</option>
              <option value="medium">medium</option>
              <option value="low">low</option>
              <option value="unknown">unknown</option>
            </select>
          </div>
          <div className="field">
            <label>&nbsp;</label>
            <button className="button" type="submit">
              Save
            </button>
          </div>
        </form>
      ) : null}

      {error ? <p className="notice">{error}</p> : null}

      <div className="table-wrap" style={{ marginTop: 14 }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Stack</th>
              <th>CO2 dry</th>
              <th>Velocity</th>
              <th>Temp</th>
              <th>data_status</th>
              <th>confidence_level</th>
            </tr>
          </thead>
          <tbody>
            {emissionTests.length === 0 ? (
              <tr>
                <td colSpan={6}>No emission tests recorded.</td>
              </tr>
            ) : (
              emissionTests.map((record) => (
                <tr key={record.id}>
                  <td>{record.stack_id}</td>
                  <td>{formatValue(record.co2_percent_dry, "%")}</td>
                  <td>{formatValue(record.gas_velocity_m_s, " m/s")}</td>
                  <td>{formatValue(record.flue_gas_temperature_c, " C")}</td>
                  <td>{record.data_status}</td>
                  <td>{record.confidence_level}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
