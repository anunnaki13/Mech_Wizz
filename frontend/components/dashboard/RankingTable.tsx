"use client";

import type { UnitRankingRow } from "@/types/scoring";

type RankingTableProps = {
  ranking: UnitRankingRow[];
  selectedPlantId: string;
  loading: boolean;
  onSelectUnit: (plantId: string) => void;
};

function formatNumber(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Not calculated";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1 })}${suffix}`;
}

function formatScore(value: number) {
  return value.toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 });
}

function formatPercent(value: number | null) {
  if (value === null) {
    return "Not calculated";
  }
  return `${(value * 100).toLocaleString("en-US", { maximumFractionDigits: 1 })}%`;
}

export function RankingTable({ loading, ranking, selectedPlantId, onSelectUnit }: RankingTableProps) {
  return (
    <section className="ranking-panel" aria-label="Unit ranking">
      <div className="map-panel-header">
        <div>
          <h3>Ranking</h3>
          <span>{loading ? "Loading ranking records" : `${ranking.length} ranked unit${ranking.length === 1 ? "" : "s"}`}</span>
        </div>
      </div>
      <div className="table-wrap">
        <table className="data-table map-ranking-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Unit/Site</th>
              <th>Province</th>
              <th>Composite Score</th>
              <th>Opportunity Score</th>
              <th>Readiness Score</th>
              <th>Confidence Score</th>
              <th>CO2 Available</th>
              <th>E-Methanol Potential</th>
              <th>Estimated IRR</th>
              <th>Recommended Scheme</th>
              <th>Key Bottleneck</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((row) => (
              <tr
                className={row.plant_id === selectedPlantId ? "active" : ""}
                key={row.scoring_result_id}
                onClick={() => onSelectUnit(row.plant_id)}
              >
                <td>#{row.rank}</td>
                <td>
                  <button className="table-link" type="button" onClick={() => onSelectUnit(row.plant_id)}>
                    {row.site_name} {row.unit_name}
                  </button>
                </td>
                <td>{row.province ?? "Unknown"}</td>
                <td>{formatScore(row.composite_score)}</td>
                <td>{formatScore(row.opportunity_score)}</td>
                <td>{formatScore(row.readiness_score)}</td>
                <td>
                  {formatScore(row.confidence_score)}
                  <span className="table-subtext">{row.data_confidence_label}</span>
                </td>
                <td>{formatNumber(row.co2_tpy, " t/y")}</td>
                <td>{formatNumber(row.methanol_tpy, " t/y")}</td>
                <td>{formatPercent(row.estimated_irr)}</td>
                <td>{row.recommended_scheme}</td>
                <td>{row.key_bottleneck}</td>
              </tr>
            ))}
            {!loading && ranking.length === 0 ? (
              <tr>
                <td colSpan={12}>No ranking records.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
