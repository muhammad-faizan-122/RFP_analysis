from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from src.rag.graph import build_graph

# Initialize the RAG graph
graph = build_graph()


# Pydantic models for request and response
class RFPRequest(BaseModel):
    user_query: str
    # metadata is optional
    metadata: Optional[dict] = None


class RFPResponse(BaseModel):
    answer: str = ""
    reasoning: str = ""
    extracted_requirements: List = []


# Create FastAPI app
app = FastAPI(title="RFP LangGraph API")


@app.post("/query", response_model=RFPResponse)
def query_rfp(request: RFPRequest):
    """
    Endpoint to query the LangGraph RAG graph.
    Returns structured output including answer, reasoning, and extracted requirements.
    """
    # Invoke the graph
    response = graph.invoke({"user_query": request.user_query})

    # Build output with defaults
    output = RFPResponse(
        answer=response.get("answer", ""),
        reasoning=response.get("reasoning", ""),
        extracted_requirements=response.get("extracted_requirements", []),
    )

    return output


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
