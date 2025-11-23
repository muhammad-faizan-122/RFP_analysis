from src.common.models import RFPRequest, RFPResponse, IngestResponse
from fastapi import FastAPI, HTTPException
import uvicorn
import logging


app = FastAPI(title="RFP RAG API")
logger = logging.getLogger("uvicorn.error")


@app.post("/query", response_model=RFPResponse)
def query_rfp(request: RFPRequest):
    """
    Endpoint to query the LangGraph RAG graph.
    Returns structured output including answer, reasoning, and extracted requirements.
    """
    try:
        from src.rag.graph import build_graph

        # Initialize the RAG graph
        graph = build_graph()

        # Invoke the graph
        response = graph.invoke({"user_query": request.user_query})

        # Build output with defaults
        output = RFPResponse(
            answer=response.get("answer", ""),
            reasoning=response.get("reasoning", ""),
            extracted_requirements=response.get("extracted_requirements", []),
        )
        return output

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to process query: {str(e)}"
        )


@app.post("/ingest", response_model=IngestResponse)
def ingest_pdfs():
    """
    Trigger ingestion of PDFs into the vector database.
    Returns the total number of chunks created.
    """
    try:
        from src.indexing.ingest import ingest_data

        total_chunks = ingest_data()
        return IngestResponse(
            message="Ingestion completed successfully.",
            total_chunks=total_chunks,
        )

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to ingest PDFs: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
