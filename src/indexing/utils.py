from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.indexing import configs
from src.indexing import prompt
from dotenv import load_dotenv
import re
import pymupdf4llm
import strip_markdown
import json
from src.common.logger import setup_logger
import os

log = setup_logger("indexing.log")


load_dotenv()


class RFPMetadata(BaseModel):
    company: str = Field(description="Name of organization or company")
    project: str = Field(description="Name of project")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def extract_rfp_metadata(md_text: list[dict], file_name: str) -> dict:
    structured_llm = llm.with_structured_output(RFPMetadata)
    message = prompt.EXTRACT_RFP_METADATA_PROMPT.format(first_page_content=md_text)
    rfp_metadata = structured_llm.invoke([HumanMessage(content=message)])
    rfp_metadata = rfp_metadata.model_dump()
    if isinstance(rfp_metadata, dict):
        rfp_metadata["file_name"] = file_name
    else:
        rfp_metadata = {"file_name": file_name}
    return rfp_metadata


def rm_markdown(md_text: str):
    return strip_markdown.strip_markdown(md_text)


def get_pdf_markdown(pdf_path: str) -> str:
    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text


def has_alphabet(line: str) -> bool:
    """Check if line contains at least one alphabetic character."""
    return bool(re.search(r"[A-Za-z]", line))


def is_markdown_heading(line: str) -> bool:
    """Check if line is a markdown heading (##, ###, etc.)."""
    return bool(re.match(r"^#{1,6}\s+.+", line.strip()))


def is_bold_heading(line: str) -> bool:
    """Check if line is bold text heading (**text** or __text__)."""
    line = line.strip()
    bold_match = re.match(r"^(\*\*|__)(.+?)(\*\*|__)$", line)

    if not bold_match:
        return False

    inner_text = bold_match.group(2).strip()

    # Check if mostly uppercase or title case
    return inner_text.replace(" ", "").isupper() or inner_text.istitle()


def is_all_caps_heading(line: str) -> bool:
    """Check if line is ALL CAPS (common heading style)."""
    line = line.strip()

    # Must be uppercase, not end with period, and be reasonably short
    return line.isupper() and not line.endswith(".") and len(line.split()) <= 10


def is_title_case_heading(line: str) -> bool:
    """"""
    line = line.strip()
    words = line.split()

    # Must be short, not end with period
    if len(words) > 10 or line.endswith("."):
        return False

    # At least 70% of words must start with uppercase
    uppercase_count = sum(1 for w in words if w and w[0].isupper())
    return uppercase_count >= len(words) * 0.7


def is_numbered_heading(line: str) -> bool:
    """Check if line is a numbered heading (1. Introduction, 1.1 Overview)."""
    line = line.strip()

    # Match patterns like "1. Text" or "1.1 Text" or "1.1.1 Text"
    # Must start with capital letter after number
    has_number_pattern = bool(re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", line))

    # Should not end with period (likely a sentence then)
    return has_number_pattern and not line.endswith(".")


def is_heading(line: str) -> bool:
    """
    Detect if a line is a heading using multiple heuristics.

    Checks for:
    - Markdown headings (##, ###)
    - Bold headings (**text**)
    - ALL CAPS headings
    """
    line = line.strip()

    # Basic validation
    if not line or not has_alphabet(line):
        return False

    # Must be short, not end with period
    if len(line.split()) > 10 or line.endswith("."):
        return False

    # Check all heading patterns
    return (
        is_markdown_heading(line) or is_bold_heading(line) or is_all_caps_heading(line)
    )


def save_to_json(data: list, file_name, dir_path="src/indexing/chunks"):
    """
    Save a list of Document-like objects to a JSON file.

    Args:
        documents (list): List of objects with attributes 'page_content' and 'metadata'
        file_name (str): Name of the output JSON file
    """
    # Convert each Document into a plain dict
    file_name = (
        f"{os.path.splitext(file_name)[0]}.json"
        if not file_name.endswith(".json")
        else file_name
    )
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    log.info(f"Saved {len(data)} data to {file_name}")


def save_documents_to_json(documents, file_name, dir_path="src/indexing/chunks"):
    """
    Save a list of Document-like objects to a JSON file.

    Args:
        documents (list): List of objects with attributes 'page_content' and 'metadata'
        file_name (str): Name of the output JSON file
    """
    # Convert each Document into a plain dict
    json_list = []
    for doc in documents:
        json_list.append(
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "total_tokens": len(doc.page_content.split()),
            }
        )
    file_name = (
        f"{os.path.splitext(file_name)[0]}.json"
        if not file_name.endswith(".json")
        else file_name
    )
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_list, f, ensure_ascii=False, indent=4)

    log.info(f"Saved {len(documents)} documents to {file_name}")


def split_by_headings(markdown_text: str) -> list[str]:
    """
    Split markdown text into sections starting with a heading.
    If a heading has no content, it is concatenated to the next section.
    """
    lines = markdown_text.splitlines()
    sections = []
    current_heading = None
    current_content = []

    for line in lines:
        line = line.strip()

        if not line or not has_alphabet(line):
            continue

        if is_heading(line):

            # If previous heading has content, save it
            if current_heading and current_content:
                sections.append(current_heading + "\n" + "\n".join(current_content))
                current_content = []
                current_heading = line

            # If previous heading had no content, carry it forward
            elif current_heading and not current_content:
                # Concatenate repeated heading
                current_heading += "\n" + line

            # if first line is heading
            else:
                current_heading = line

        else:
            # just add content of current heading
            if current_heading:
                current_content.append(line)
            else:
                # Content without heading
                current_content.append(line)
                current_heading = ""

    # Add last section
    if current_heading:
        sections.append(current_heading + "\n" + "\n".join(current_content))

    return sections


def merge_shorter_sections(sections: list[str]):
    """merge shorter heading to heading sections"""
    merged_shorter_sections = []
    prev_section = ""
    for curr_section in sections:

        if prev_section:
            # update the current section by concatenate with prev section
            curr_section = f"{prev_section}\n{curr_section}"

        # if tokens shorter than thresh: update prev section with current
        curr_tokens = len(curr_section.split())
        if curr_tokens < configs.MIN_TOKENS:
            prev_section = curr_section

        # if tokens are normal just append it merge section
        else:
            merged_shorter_sections.append(curr_section)
            prev_section = ""

    # for last unmerge section or only one section which is shorter than required
    if prev_section:
        if merged_shorter_sections:
            merged_shorter_sections[-1] += f"\n{prev_section}"
        else:
            merged_shorter_sections.append(prev_section)

    return merged_shorter_sections
