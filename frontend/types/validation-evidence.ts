import type { ProjectDocument } from "@/types/document";

export type ValidationEvidenceCategory = "technical" | "economics" | "logistics" | "power_h2" | "commercial_mrv";
export type ValidationEvidenceStatus = "missing" | "requested" | "received" | "verified" | "rejected";
export type ValidationEvidencePriority = "high" | "medium" | "low";
export type ValidationEvidenceConfidence = "high" | "medium" | "low" | "unknown";

export type ValidationEvidenceRecord = {
  id: string;
  plant_id: string;
  scenario_id: string;
  document_id: string | null;
  category: ValidationEvidenceCategory;
  evidence_key: string;
  title: string;
  required_evidence: string | null;
  current_basis: string | null;
  status: ValidationEvidenceStatus;
  priority: ValidationEvidencePriority;
  owner_name: string | null;
  source_organization: string | null;
  reference_url: string | null;
  due_date: string | null;
  received_date: string | null;
  verified_date: string | null;
  confidence_level: ValidationEvidenceConfidence;
  notes: string | null;
  supporting_document: ProjectDocument | null;
  created_at: string;
  updated_at: string;
};

export type ValidationEvidencePayload = {
  plant_id?: string;
  scenario_id?: string;
  document_id?: string | null;
  category?: ValidationEvidenceCategory;
  evidence_key?: string;
  title?: string;
  required_evidence?: string | null;
  current_basis?: string | null;
  status?: ValidationEvidenceStatus;
  priority?: ValidationEvidencePriority;
  owner_name?: string | null;
  source_organization?: string | null;
  reference_url?: string | null;
  due_date?: string | null;
  received_date?: string | null;
  verified_date?: string | null;
  confidence_level?: ValidationEvidenceConfidence;
  notes?: string | null;
};

export type ValidationEvidenceRequirement = {
  plant_id: string;
  scenario_id: string;
  category: ValidationEvidenceCategory;
  evidence_key: string;
  title: string;
  required_evidence: string;
  current_basis: string;
  priority: ValidationEvidencePriority;
  source_validation_status: string;
  status: ValidationEvidenceStatus;
  confidence_level: ValidationEvidenceConfidence;
  status_score: number;
  record: ValidationEvidenceRecord | null;
};

export type ValidationEvidenceCandidate = {
  validation_rank: number;
  site_name: string;
  plant_id: string;
  scenario_id: string;
  province: string | null;
  capacity_mw: number | null;
  final_score: number;
  methanol_tpy: number | null;
  estimated_lcom_usd_ton: number | null;
  nearest_port_name: string | null;
  evidence_readiness_score: number;
  high_priority_open_items: number;
  evidence_items: ValidationEvidenceRequirement[];
};

export type ValidationEvidenceWorkspace = {
  scheme: string;
  limit: number;
  summary: {
    candidate_count: number;
    lead_candidate: string | null;
    total_items: number;
    verified_items: number;
    high_priority_open_items: number;
    evidence_readiness_score: number;
    counts_by_status: Record<ValidationEvidenceStatus, number>;
  };
  candidates: ValidationEvidenceCandidate[];
  warnings: string[];
};
