from pydantic import BaseModel
from typing import List, Optional


class Metadata(BaseModel):
    company: str
    project: str
    file_name: str


class ExtractedRequirement(BaseModel):
    id: Optional[str]
    metadata: Optional[Metadata]
    page_content: str
    type: Optional[str]


class RFPResponseSchema(BaseModel):
    user_query: str
    answer: str
    reasoning: str
    extracted_requirements: List[ExtractedRequirement]
