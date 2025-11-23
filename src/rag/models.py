from pydantic import BaseModel
from typing import List, Optional


class RFPRequest(BaseModel):
    user_query: str
    # metadata is optional
    metadata: Optional[dict] = None


class RFPResponse(BaseModel):
    user_query: str = ""
    answer: str = ""
    reasoning: str = ""
    extracted_requirements: List = []
