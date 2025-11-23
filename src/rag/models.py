from pydantic import BaseModel
from typing import List, Optional


class Metadata(BaseModel):
    file_name: Optional[str] = ""
    company: Optional[str] = ""
    project: Optional[str] = ""


class RFPRequest(BaseModel):
    user_query: str
    metadata: Metadata


class RFPResponse(BaseModel):
    user_query: str = ""
    answer: str = ""
    reasoning: str = ""
    extracted_requirements: List = []
