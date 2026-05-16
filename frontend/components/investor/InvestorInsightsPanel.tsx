"use client";

import { FileText, RefreshCw, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  generateDataGapExplanation,
  generateExecutiveSummary,
  generateInvestorMemo,
  generateSensitivityExplanation,
  getLlmInsights,
} from "@/lib/api";
import type { InsightType, LlmInsight } from "@/types/llm";

type InsightAction = {
  type: Exclude<InsightType, "document_qa">;
  label: string;
};

const INSIGHT_ACTIONS: InsightAction[] = [
  { type: "executive_summary", label: "Executive Summary" },
  { type: "investor_memo", label: "Investor Memo" },
  { type: "data_gap_explanation", label: "Data Gap Explanation" },
  { type: "sensitivity_explanation", label: "Sensitivity Explanation" },
];

function insightLabel(type: string) {
  return INSIGHT_ACTIONS.find((item) => item.type === type)?.label ?? type.replaceAll("_", " ");
}

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function InvestorInsightsPanel({
  plantId,
  scenarioId,
}: {
  plantId: string;
  scenarioId: string;
}) {
  const [insights, setInsights] = useState<LlmInsight[]>([]);
  const [selectedInsightId, setSelectedInsightId] = useState("");
  const [activeType, setActiveType] = useState<InsightAction["type"]>("executive_summary");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedInsight = useMemo(
    () => insights.find((insight) => insight.id === selectedInsightId) ?? insights[0] ?? null,
    [insights, selectedInsightId],
  );

  async function loadInsights() {
    if (!scenarioId) {
      setInsights([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const records = await getLlmInsights({ scenarioId });
      setInsights(records);
      setSelectedInsightId((current) => current || records[0]?.id || "");
    } catch {
      setErrorMessage("Generated insights could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function generateSelectedInsight() {
    if (!plantId || !scenarioId) {
      return;
    }
    setGenerating(true);
    setErrorMessage(null);
    try {
      let record: LlmInsight;
      if (activeType === "executive_summary") {
        record = await generateExecutiveSummary(scenarioId);
      } else if (activeType === "investor_memo") {
        record = await generateInvestorMemo(scenarioId);
      } else if (activeType === "data_gap_explanation") {
        record = await generateDataGapExplanation({ plantId, scenarioId });
      } else {
        record = await generateSensitivityExplanation(scenarioId);
      }
      setInsights((current) => [record, ...current.filter((item) => item.id !== record.id)]);
      setSelectedInsightId(record.id);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Insight generation failed.");
      await loadInsights();
    } finally {
      setGenerating(false);
    }
  }

  useEffect(() => {
    setSelectedInsightId("");
    void loadInsights();
  }, [scenarioId]);

  return (
    <div className="card investor-panel wide insight-panel">
      <div className="setting-card-header">
        <div>
          <h3>AI Narrative Insights</h3>
          <span>{loading ? "Loading" : `${insights.length} stored insights`}</span>
        </div>
        <button className="button secondary" type="button" onClick={() => void loadInsights()}>
          <RefreshCw size={16} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {errorMessage ? <div className="notice">{errorMessage}</div> : null}

      <div className="insight-actions">
        {INSIGHT_ACTIONS.map((action) => (
          <button
            className={`button ${activeType === action.type ? "" : "secondary"}`}
            key={action.type}
            type="button"
            onClick={() => setActiveType(action.type)}
          >
            <FileText size={16} aria-hidden="true" />
            {action.label}
          </button>
        ))}
        <button
          className="button"
          type="button"
          disabled={generating || !scenarioId}
          onClick={() => void generateSelectedInsight()}
        >
          <Sparkles size={16} aria-hidden="true" />
          {generating ? "Generating" : "Generate"}
        </button>
      </div>

      <div className="insight-layout">
        <div className="insight-list">
          {insights.map((insight) => (
            <button
              className={selectedInsight?.id === insight.id ? "active" : ""}
              key={insight.id}
              type="button"
              onClick={() => setSelectedInsightId(insight.id)}
            >
              <strong>{insightLabel(insight.insight_type)}</strong>
              <span>{insight.status} / {formatTimestamp(insight.created_at)}</span>
            </button>
          ))}
          {insights.length === 0 ? <div className="muted">No generated insights yet.</div> : null}
        </div>
        <div className="insight-output">
          {selectedInsight ? (
            <>
              <div className="confidence-strip">
                <span className="chip">{insightLabel(selectedInsight.insight_type)}</span>
                <span className="chip">{selectedInsight.model_name}</span>
                <span className="chip">{selectedInsight.status}</span>
              </div>
              <p>{selectedInsight.response_text || selectedInsight.error_message || "No response text stored."}</p>
            </>
          ) : (
            <p className="muted">Generate or select an insight to review the narrative output.</p>
          )}
        </div>
      </div>
    </div>
  );
}
