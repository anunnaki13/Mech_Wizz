import type { ProjectDocument } from "@/types/document";
import type { ConfidenceLevel, DataStatus } from "@/types/plant";

export type PreFeedPackageStatus = "draft" | "in_review" | "validated" | "archived";

export type PreFeedDocumentRole =
  | "vendor_proposal"
  | "epc_estimate"
  | "offtake_document"
  | "mrv_document"
  | "permit_document"
  | "internal_note";

export type PreFeedPackageDocument = {
  id: string;
  package_id: string;
  document_id: string;
  document_role: PreFeedDocumentRole;
  notes: string | null;
  document: ProjectDocument | null;
  created_at: string;
  updated_at: string;
};

export type PreFeedPackage = {
  id: string;
  plant_id: string;
  scenario_id: string | null;
  package_name: string;
  package_status: PreFeedPackageStatus;
  owner_name: string | null;
  source_organization: string | null;
  received_date: string | null;
  version_label: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes: string | null;
  document_links: PreFeedPackageDocument[];
  created_at: string;
  updated_at: string;
};

export type PreFeedPackagePayload = {
  plant_id: string;
  scenario_id?: string | null;
  package_name: string;
  package_status: PreFeedPackageStatus;
  owner_name?: string | null;
  source_organization?: string | null;
  received_date?: string | null;
  version_label?: string | null;
  data_status: DataStatus;
  confidence_level: ConfidenceLevel;
  notes?: string | null;
};

export type PreFeedPackageUpdatePayload = Partial<PreFeedPackagePayload>;

export type PreFeedPackageDocumentPayload = {
  document_id: string;
  document_role: PreFeedDocumentRole;
  notes?: string | null;
};

export type PreFeedPackageGap = {
  package_id: string;
  source_module: string;
  missing_data_name: string;
  impact_level: string;
  priority_level: string;
  recommendation: string;
  status: string;
  confidence_level: ConfidenceLevel;
};
