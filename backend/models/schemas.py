from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    date: Optional[datetime] = None
    description: str
    source_document: str
    confidence: Optional[float] = None


class ChronologyRequest(BaseModel):
    case_description: str = Field(..., description="Brief description of the case")
    documents_text: List[str] = Field(..., description="List of document contents")
    document_names: List[str] = Field(..., description="List of document names")


class ChronologyResponse(BaseModel):
    events: List[Event]
    markdown_output: str
