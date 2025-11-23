from typing import Optional
from typing_extensions import TypedDict


class MetadataSchema(TypedDict):
    company_name: str
    organization_name: str
    file_name: str


class RFPInputState(TypedDict):
    """
    TypedDict for LangGraph input.
    - `user_query` is required
    - `metadata` is optional
    """

    user_query: str
    metadata: Optional[MetadataSchema]


class RFPOutputState(TypedDict):
    """
    TypedDict for LangGraph Output.
    - `user_query` is required
    - `metadata` is optional
    """

    answer: str
    reasoning: str
    extracted_requirements: list[str]
