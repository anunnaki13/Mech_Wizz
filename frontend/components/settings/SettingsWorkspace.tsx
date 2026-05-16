"use client";

import { AlertTriangle, KeyRound, RefreshCw, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  getDataQualitySummary,
  getOpenRouterSettings,
  getPlantScenarios,
  getPlants,
  getSettings,
  updateOpenRouterSettings,
  updateSetting,
} from "@/lib/api";
import type { ConfidenceLevel, DataStatus, Plant } from "@/types/plant";
import type { BusinessScenario } from "@/types/scenario";
import type { ApplicationSetting, DataQualitySummary, OpenRouterSettings } from "@/types/settings";

const DATA_STATUS_OPTIONS: DataStatus[] = [
  "actual",
  "estimated",
  "benchmark",
  "user_assumption",
  "partner_supplied",
  "unknown",
];

const CONFIDENCE_OPTIONS: ConfidenceLevel[] = ["high", "medium", "low", "unknown"];

type ScenarioOption = BusinessScenario & {
  plant_name: string;
  unit_name: string;
};

type OpenRouterDraft = {
  apiKey: string;
  baseUrl: string;
  model: string;
  siteUrl: string;
  appName: string;
};

function titleForSetting(key: string) {
  if (key === "default_financial_assumptions") {
    return "Default assumptions";
  }
  if (key === "scoring_weights") {
    return "Scoring weights";
  }
  return key.replaceAll("_", " ");
}

function labelForKey(key: string) {
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function SettingsWorkspace() {
  const [settings, setSettings] = useState<ApplicationSetting[]>([]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [openRouter, setOpenRouter] = useState<OpenRouterSettings | null>(null);
  const [openRouterDraft, setOpenRouterDraft] = useState<OpenRouterDraft>({
    apiKey: "",
    baseUrl: "https://openrouter.ai/api/v1",
    model: "openai/gpt-5.2",
    siteUrl: "http://localhost:3000",
    appName: "MECH WIZ AI Digital Twin",
  });
  const [plants, setPlants] = useState<Plant[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState("");
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [qualitySummary, setQualitySummary] = useState<DataQualitySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingQuality, setLoadingQuality] = useState(false);
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [savingOpenRouter, setSavingOpenRouter] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const scenarioOptions = useMemo(
    () => scenarios.filter((scenario) => !selectedPlantId || scenario.plant_id === selectedPlantId),
    [scenarios, selectedPlantId],
  );

  function updateSettingState(key: string, patch: Partial<ApplicationSetting>) {
    setSettings((current) => current.map((setting) => (setting.key === key ? { ...setting, ...patch } : setting)));
  }

  async function loadSettingsData() {
    setErrorMessage(null);
    const records = await getSettings();
    setSettings(records);
    setDrafts(
      Object.fromEntries(records.map((record) => [record.key, JSON.stringify(record.value, null, 2)])),
    );
  }

  async function loadOpenRouterData() {
    const record = await getOpenRouterSettings();
    setOpenRouter(record);
    setOpenRouterDraft((current) => ({
      ...current,
      apiKey: "",
      baseUrl: record.base_url,
      model: record.model,
      siteUrl: record.site_url,
      appName: record.app_name,
    }));
  }

  async function loadReferenceData() {
    const plantRecords = await getPlants();
    const scenarioRecords = (
      await Promise.all(
        plantRecords.map(async (plant) => {
          const plantScenarios = await getPlantScenarios(plant.id);
          return plantScenarios.map((scenario) => ({
            ...scenario,
            plant_name: plant.plant_name,
            unit_name: plant.unit_name,
          }));
        }),
      )
    ).flat();
    setPlants(plantRecords);
    setScenarios(scenarioRecords);
    setSelectedPlantId((current) => current || plantRecords[0]?.id || "");
    setSelectedScenarioId((current) => current || scenarioRecords[0]?.id || "");
  }

  async function loadAll() {
    setLoading(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      await Promise.all([loadSettingsData(), loadOpenRouterData(), loadReferenceData()]);
      setStatusMessage("Settings loaded.");
    } catch {
      setErrorMessage("Settings data is not reachable.");
    } finally {
      setLoading(false);
    }
  }

  async function loadQualitySummary(plantId = selectedPlantId, scenarioId = selectedScenarioId) {
    if (!plantId) {
      setQualitySummary(null);
      return;
    }
    setLoadingQuality(true);
    setErrorMessage(null);
    try {
      const summary = await getDataQualitySummary({
        plantId,
        scenarioId: scenarioId || undefined,
      });
      setQualitySummary(summary);
    } catch {
      setQualitySummary(null);
      setErrorMessage("Data quality summary could not be loaded.");
    } finally {
      setLoadingQuality(false);
    }
  }

  async function saveSetting(setting: ApplicationSetting) {
    setSavingKey(setting.key);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const parsed = JSON.parse(drafts[setting.key] ?? "{}");
      if (!isRecord(parsed)) {
        throw new Error("Setting value must be a JSON object.");
      }
      const saved = await updateSetting(setting.key, {
        value: parsed,
        data_status: setting.data_status,
        confidence_level: setting.confidence_level,
      });
      updateSettingState(setting.key, saved);
      setDrafts((current) => ({
        ...current,
        [setting.key]: JSON.stringify(saved.value, null, 2),
      }));
      setStatusMessage(`${titleForSetting(setting.key)} saved.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Setting could not be saved.");
    } finally {
      setSavingKey(null);
    }
  }

  async function saveOpenRouterSettings() {
    setSavingOpenRouter(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const saved = await updateOpenRouterSettings({
        api_key: openRouterDraft.apiKey || null,
        base_url: openRouterDraft.baseUrl,
        model: openRouterDraft.model,
        site_url: openRouterDraft.siteUrl,
        app_name: openRouterDraft.appName,
      });
      setOpenRouter(saved);
      setOpenRouterDraft((current) => ({ ...current, apiKey: "" }));
      setStatusMessage("OpenRouter settings saved.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "OpenRouter settings could not be saved.");
    } finally {
      setSavingOpenRouter(false);
    }
  }

  async function clearOpenRouterKey() {
    setSavingOpenRouter(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const saved = await updateOpenRouterSettings({ clear_api_key: true });
      setOpenRouter(saved);
      setOpenRouterDraft((current) => ({ ...current, apiKey: "" }));
      setStatusMessage("OpenRouter API key cleared.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "OpenRouter API key could not be cleared.");
    } finally {
      setSavingOpenRouter(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, []);

  useEffect(() => {
    if (!loading && selectedPlantId) {
      void loadQualitySummary(selectedPlantId, selectedScenarioId);
    }
  }, [loading, selectedPlantId, selectedScenarioId]);

  return (
    <div className="settings-workspace">
      <section className="page-header">
        <div>
          <h2>Settings & Data Quality</h2>
          <p>Editable assumptions, scoring weights, source status, output confidence, and current data gaps.</p>
        </div>
        <div className="inline-actions">
          <button className="button secondary" type="button" onClick={() => void loadAll()} disabled={loading}>
            <RefreshCw size={16} aria-hidden="true" />
            {loading ? "Refreshing" : "Refresh"}
          </button>
        </div>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="card openrouter-card" aria-label="OpenRouter provider settings">
        <div className="setting-card-header">
          <div>
            <h3>OpenRouter Provider</h3>
            <span>
              {openRouter?.has_api_key
                ? `API key active (${openRouter.api_key_source}: ${openRouter.api_key_masked})`
                : "API key not configured"}
            </span>
          </div>
          <KeyRound size={18} aria-hidden="true" />
        </div>
        <div className="openrouter-grid">
          <label className="field">
            <span>API Key</span>
            <input
              autoComplete="off"
              placeholder={openRouter?.has_api_key ? "Leave blank to keep current key" : "Paste OpenRouter API key"}
              type="password"
              value={openRouterDraft.apiKey}
              onChange={(event) =>
                setOpenRouterDraft((current) => ({ ...current, apiKey: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Model</span>
            <input
              value={openRouterDraft.model}
              onChange={(event) =>
                setOpenRouterDraft((current) => ({ ...current, model: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Base URL</span>
            <input
              value={openRouterDraft.baseUrl}
              onChange={(event) =>
                setOpenRouterDraft((current) => ({ ...current, baseUrl: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>Site URL</span>
            <input
              value={openRouterDraft.siteUrl}
              onChange={(event) =>
                setOpenRouterDraft((current) => ({ ...current, siteUrl: event.target.value }))
              }
            />
          </label>
          <label className="field">
            <span>App Name</span>
            <input
              value={openRouterDraft.appName}
              onChange={(event) =>
                setOpenRouterDraft((current) => ({ ...current, appName: event.target.value }))
              }
            />
          </label>
          <div className="openrouter-actions">
            <button
              className="button"
              disabled={savingOpenRouter}
              type="button"
              onClick={() => void saveOpenRouterSettings()}
            >
              <Save size={16} aria-hidden="true" />
              {savingOpenRouter ? "Saving" : "Save OpenRouter"}
            </button>
            <button
              className="button secondary"
              disabled={savingOpenRouter || openRouter?.api_key_source !== "stored"}
              type="button"
              onClick={() => void clearOpenRouterKey()}
            >
              <Trash2 size={16} aria-hidden="true" />
              Clear Key
            </button>
          </div>
        </div>
      </section>

      <section className="settings-grid">
        {settings.map((setting) => (
          <article className="card setting-card" key={setting.key}>
            <div className="setting-card-header">
              <div>
                <h3>{titleForSetting(setting.key)}</h3>
                <span>{setting.key}</span>
              </div>
              <button
                className="button"
                type="button"
                disabled={savingKey === setting.key}
                onClick={() => void saveSetting(setting)}
              >
                <Save size={16} aria-hidden="true" />
                {savingKey === setting.key ? "Saving" : "Save"}
              </button>
            </div>
            <div className="setting-controls">
              <label className="field">
                <span>Data status</span>
                <select
                  value={setting.data_status}
                  onChange={(event) =>
                    updateSettingState(setting.key, { data_status: event.target.value as DataStatus })
                  }
                >
                  {DATA_STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Confidence</span>
                <select
                  value={setting.confidence_level}
                  onChange={(event) =>
                    updateSettingState(setting.key, { confidence_level: event.target.value as ConfidenceLevel })
                  }
                >
                  {CONFIDENCE_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <textarea
              aria-label={titleForSetting(setting.key)}
              className="json-editor"
              spellCheck={false}
              value={drafts[setting.key] ?? ""}
              onChange={(event) => setDrafts((current) => ({ ...current, [setting.key]: event.target.value }))}
            />
          </article>
        ))}
      </section>

      <section className="settings-quality-grid">
        <article className="card settings-quality-panel">
          <div className="setting-card-header">
            <div>
              <h3>Data Quality</h3>
              <span>{loadingQuality ? "Refreshing" : "Current summary"}</span>
            </div>
            <button className="button secondary" type="button" onClick={() => void loadQualitySummary()}>
              <RefreshCw size={16} aria-hidden="true" />
              Refresh
            </button>
          </div>
          <div className="quality-controls">
            <label className="field">
              <span>Plant</span>
              <select
                disabled={plants.length === 0}
                value={selectedPlantId}
                onChange={(event) => {
                  const plantId = event.target.value;
                  setSelectedPlantId(plantId);
                  setSelectedScenarioId(scenarios.find((scenario) => scenario.plant_id === plantId)?.id || "");
                }}
              >
                {plants.map((plant) => (
                  <option key={plant.id} value={plant.id}>
                    {plant.plant_name} {plant.unit_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Scenario</span>
              <select
                disabled={scenarioOptions.length === 0}
                value={selectedScenarioId}
                onChange={(event) => setSelectedScenarioId(event.target.value)}
              >
                {scenarioOptions.map((scenario) => (
                  <option key={scenario.id} value={scenario.id}>
                    {scenario.scenario_name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="quality-matrix">
            <div>
              <h4>Input status</h4>
              {Object.entries(qualitySummary?.input_status ?? {}).map(([key, value]) => (
                <div className="detail-row" key={key}>
                  <span>{labelForKey(key)}</span>
                  <span>{value}</span>
                </div>
              ))}
            </div>
            <div>
              <h4>Output confidence</h4>
              {Object.entries(qualitySummary?.output_confidence ?? {}).map(([key, value]) => (
                <div className="detail-row" key={key}>
                  <span>{labelForKey(key)}</span>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </article>

        <article className="card settings-reference">
          <h3>Reference</h3>
          <div>
            <h4>Allowed data status</h4>
            <div className="chip-row">
              {DATA_STATUS_OPTIONS.map((status) => (
                <span className="chip" key={status}>
                  {status}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h4>Allowed confidence</h4>
            <div className="chip-row">
              {CONFIDENCE_OPTIONS.map((level) => (
                <span className="chip" key={level}>
                  {level}
                </span>
              ))}
            </div>
          </div>
        </article>

        <article className="card settings-gap-panel wide">
          <div className="setting-card-header">
            <div>
              <h3>Data Gap Recommendations</h3>
              <span>{qualitySummary?.gaps.length ?? 0} open gaps</span>
            </div>
            <AlertTriangle size={18} aria-hidden="true" />
          </div>
          <div className="data-gap-list">
            {(qualitySummary?.gaps ?? []).map((gap) => (
              <div className="data-gap-row" key={gap.id}>
                <strong>{gap.missing_data_name}</strong>
                <span>
                  {gap.source_module} / {gap.impact_level} impact / {gap.priority_level} / {gap.recommendation}
                </span>
              </div>
            ))}
            {qualitySummary && qualitySummary.gaps.length === 0 ? (
              <div className="status-line">No open data gaps for this selection.</div>
            ) : null}
          </div>
        </article>
      </section>
    </div>
  );
}
