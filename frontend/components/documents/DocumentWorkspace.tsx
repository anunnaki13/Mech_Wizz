"use client";

import { FileQuestion, RefreshCw, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  askDocument,
  extractDocument,
  getDocuments,
  getPlantScenarios,
  getPlants,
  uploadDocument,
} from "@/lib/api";
import type { LlmInsight } from "@/types/llm";
import type { Plant } from "@/types/plant";
import type { BusinessScenario } from "@/types/scenario";
import type { ProjectDocument } from "@/types/document";

type ScenarioOption = BusinessScenario & {
  plant_name: string;
  unit_name: string;
};

function formatSize(value: number | null) {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  return `${(value / 1024).toLocaleString("en-US", { maximumFractionDigits: 1 })} KB`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function DocumentWorkspace() {
  const [documents, setDocuments] = useState<ProjectDocument[]>([]);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioOption[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState("");
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState("emission_report");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<LlmInsight | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedDocumentId) ?? documents[0] ?? null,
    [documents, selectedDocumentId],
  );

  const scenarioOptions = useMemo(
    () => scenarios.filter((scenario) => !selectedPlantId || scenario.plant_id === selectedPlantId),
    [scenarios, selectedPlantId],
  );

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

  async function loadDocuments() {
    setErrorMessage(null);
    const records = await getDocuments();
    setDocuments(records);
    setSelectedDocumentId((current) => current || records[0]?.id || "");
  }

  async function loadAll() {
    setLoading(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await Promise.all([loadReferenceData(), loadDocuments()]);
      setStatusMessage("Document repository loaded.");
    } catch {
      setErrorMessage("Document repository could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload() {
    if (!selectedFile) {
      setErrorMessage("Select a file before uploading.");
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const uploaded = await uploadDocument({
        file: selectedFile,
        plantId: selectedPlantId || undefined,
        scenarioId: selectedScenarioId || undefined,
        documentCategory: category,
      });
      setDocuments((current) => [uploaded, ...current.filter((document) => document.id !== uploaded.id)]);
      setSelectedDocumentId(uploaded.id);
      setSelectedFile(null);
      setStatusMessage("Document uploaded.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Document upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleExtract() {
    if (!selectedDocument) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const extracted = await extractDocument(selectedDocument.id);
      setDocuments((current) => current.map((document) => (document.id === extracted.id ? extracted : document)));
      setSelectedDocumentId(extracted.id);
      setStatusMessage(extracted.extraction_status === "extracted" ? "Text extracted." : "Extraction failed.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Extraction failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleAsk() {
    if (!selectedDocument || !question.trim()) {
      return;
    }
    setBusy(true);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const insight = await askDocument(selectedDocument.id, { question: question.trim() });
      setAnswer(insight);
      setStatusMessage("Document answer generated.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Document question failed.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, []);

  return (
    <div className="document-workspace">
      <section className="page-header">
        <div>
          <h2>Document Intelligence</h2>
          <p>Upload project documents, extract text, and ask grounded questions from stored context.</p>
        </div>
        <button className="button secondary" type="button" onClick={() => void loadAll()} disabled={loading}>
          <RefreshCw size={16} aria-hidden="true" />
          {loading ? "Refreshing" : "Refresh"}
        </button>
      </section>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}
      {statusMessage ? <div className="status-line">{statusMessage}</div> : null}

      <section className="document-layout">
        <div className="document-main-stack">
          <article className="card document-upload-panel">
            <h3>Upload</h3>
            <div className="document-upload-grid">
              <label className="field">
                <span>File</span>
                <input
                  type="file"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
              </label>
              <label className="field">
                <span>Category</span>
                <input value={category} onChange={(event) => setCategory(event.target.value)} />
              </label>
              <label className="field">
                <span>Plant</span>
                <select
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
                <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
                  {scenarioOptions.map((scenario) => (
                    <option key={scenario.id} value={scenario.id}>
                      {scenario.scenario_name}
                    </option>
                  ))}
                </select>
              </label>
              <button className="button" type="button" disabled={busy} onClick={() => void handleUpload()}>
                <Upload size={16} aria-hidden="true" />
                {busy ? "Working" : "Upload"}
              </button>
            </div>
          </article>

          <article className="card document-repository-panel">
            <div className="setting-card-header">
              <div>
                <h3>Repository</h3>
                <span>{documents.length} documents</span>
              </div>
            </div>
            <div className="table-wrap">
              <table className="data-table document-table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Category</th>
                    <th>Upload</th>
                    <th>Extraction</th>
                    <th>Size</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((document) => (
                    <tr
                      className={selectedDocument?.id === document.id ? "active" : ""}
                      key={document.id}
                      onClick={() => setSelectedDocumentId(document.id)}
                    >
                      <td>
                        <button className="table-link" type="button">
                          {document.original_filename}
                        </button>
                        <span className="table-subtext">{document.file_type}</span>
                      </td>
                      <td>{document.document_category ?? "uncategorized"}</td>
                      <td>{document.upload_status}</td>
                      <td>{document.extraction_status}</td>
                      <td>{formatSize(document.file_size_bytes)}</td>
                      <td>{formatDate(document.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {documents.length === 0 ? <div className="muted">No documents uploaded yet.</div> : null}
          </article>
        </div>

        <aside className="document-detail-stack">
          <article className="card document-detail-panel">
            <div className="setting-card-header">
              <div>
                <h3>Selected Document</h3>
                <span>{selectedDocument?.original_filename ?? "None"}</span>
              </div>
              <button className="button secondary" type="button" disabled={!selectedDocument || busy} onClick={() => void handleExtract()}>
                <RefreshCw size={16} aria-hidden="true" />
                Extract
              </button>
            </div>
            {selectedDocument ? (
              <div className="detail-list">
                <div className="detail-row">
                  <span>Status</span>
                  <span>{selectedDocument.extraction_status}</span>
                </div>
                <div className="detail-row">
                  <span>Category</span>
                  <span>{selectedDocument.document_category ?? "uncategorized"}</span>
                </div>
                <div className="detail-row">
                  <span>Error</span>
                  <span>{selectedDocument.extraction_error ?? "None"}</span>
                </div>
              </div>
            ) : (
              <p className="muted">Select a document to inspect details.</p>
            )}
          </article>

          <article className="card document-preview-panel">
            <h3>Extracted Text</h3>
            <pre>{selectedDocument?.extracted_text?.slice(0, 2500) ?? "No extracted text yet."}</pre>
          </article>

          <article className="card document-qa-panel">
            <h3>Document Q&A</h3>
            <textarea
              className="json-editor qa-input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question grounded in the extracted document text."
            />
            <button
              className="button"
              type="button"
              disabled={!selectedDocument?.extracted_text || busy || !question.trim()}
              onClick={() => void handleAsk()}
            >
              <FileQuestion size={16} aria-hidden="true" />
              Ask
            </button>
            <div className="insight-output">
              <p>{answer?.response_text || answer?.error_message || "No document answer yet."}</p>
            </div>
          </article>
        </aside>
      </section>
    </div>
  );
}
