export type ProjectDocument = {
  id: string;
  plant_id: string | null;
  scenario_id: string | null;
  filename: string;
  original_filename: string;
  file_type: string;
  storage_path: string;
  document_category: string | null;
  upload_status: string;
  extraction_status: string;
  extracted_text: string | null;
  extraction_error: string | null;
  file_size_bytes: number | null;
  created_at: string;
  updated_at: string;
};

export type DocumentAskPayload = {
  question: string;
  model_name?: string | null;
};
