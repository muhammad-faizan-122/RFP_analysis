from typing import Optional
from typing_extensions import TypedDict


class MetadataSchema(TypedDict):
    file_name: Optional[str] = ""
    company: Optional[str] = ""
    project: Optional[str] = ""


class RFPInputState(TypedDict):
    """
    TypedDict for LangGraph input.
    - `user_query` is required
    - `metadata` is optional
    """

    user_query: str
    metadata: MetadataSchema


class RFPOutputState(TypedDict):
    """
    TypedDict for LangGraph Output.
    - `user_query` is required
    - `metadata` is optional
    """

    answer: str
    reasoning: str
    extracted_requirements: list[str]
