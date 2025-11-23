from pydantic import BaseModel
from typing import List, Optional


class RFPRequest(BaseModel):
    user_query: str
    # metadata is optional
    metadata: Optional[dict] = None


class RFPResponse(BaseModel):
    answer: str = ""
    reasoning: str = ""
    extracted_requirements: List = []


class IngestResponse(BaseModel):
    message: str
    total_chunks: int
