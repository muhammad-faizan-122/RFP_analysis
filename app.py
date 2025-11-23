from src.rag.models import RFPRequest, RFPResponse
from src.indexing.model import IngestResponse
from fastapi import FastAPI, HTTPException
import uvicorn
import logging
from src.eval.models import RFPResponseSchema

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
            user_query=request.user_query,
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


@app.post("/eval_rfp")
def eval_rfp(rag_response: RFPResponseSchema):
    """
    Endpoint to evaluate a RAG response using evaluate_rag_response.
    Accepts a validated RAG response dict and returns evaluation results.
    """
    try:
        from src.eval.eval_rag import evaluate_rag_response

        # Convert Pydantic model to dict
        rag_response_dict = rag_response.model_dump()
        eval_result = evaluate_rag_response(rag_response_dict)

        return {"evaluation": eval_result}

    except Exception as e:
        logger.error(f"RAG evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to evaluate RAG response: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
