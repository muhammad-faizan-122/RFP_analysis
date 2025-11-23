from typing import List
import re


def extract_scores(text: str) -> dict:
    """
    Extract Score + Explanation pairs and convert to JSON.
    """
    pattern = r"""
        (?P<name>\w+)\s+Score:\s*(?P<score>\d+)\s*
        (?P<name2>\w+)\s+Explanation:\s*(?P<explanation>.*?)(?=\n\w+\s+Score:|\Z)
    """

    matches = re.finditer(pattern, text, re.DOTALL | re.VERBOSE)

    result = {}

    for m in matches:
        name = m.group("name").strip().lower()  # clarity, relevance, depth
        score = int(m.group("score"))
        explanation = m.group("explanation").strip()

        result[name] = {"score": score, "explanation": explanation}

    return result


def format_retrieved_document(retrieved_docs: List[dict]):
    relevant_document = ""
    for i, doc in enumerate(retrieved_docs):
        relevant_document += f"Document-{i+1}:\n{doc['page_content']}\n\n"
    return relevant_document
