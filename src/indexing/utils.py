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


def has_alpha(line: str) -> bool:
    return bool(re.search(r"[A-Za-z]", line))


def is_heading(line: str) -> bool:
    """Detect if a line is a heading."""
    line = line.strip()
    # Markdown heading
    if line.startswith("## "):
        return True
    # Bold uppercase heading
    bold_match = re.match(r"\*\*(.+?)\*\*", line)
    if bold_match and bold_match.group(1).replace(" ", "").isupper():
        return True
    return False


def save_documents_to_json(documents: list, file_path: str = "./documents.json"):
    """save documents to JSON for verification"""
    with open(file_path, "w") as f:
        json.dumps(documents, f, indent=4)


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

        if not line or not has_alpha(line):
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

            else:
                current_heading = line

        else:
            if current_heading:
                current_content.append(line)
            else:
                # Content without heading
                current_heading = ""
                current_content.append(line)

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
