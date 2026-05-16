from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    id: str
    plant_id: str | None
    scenario_id: str | None
    filename: str
    original_filename: str
    file_type: str
    storage_path: str
    document_category: str | None
    upload_status: str
    extraction_status: str
    extracted_text: str | None
    extraction_error: str | None
    file_size_bytes: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    model_name: str | None = None
