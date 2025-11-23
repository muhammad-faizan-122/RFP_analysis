from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from src.rag.states import RFPInputState, RFPOutputState
from src.rag.rag_executor import rfp_rag
from langchain_core.messages import AIMessage
from src.common import config
from src.common.logger import log
from dotenv import load_dotenv


load_dotenv(override=True)

llm = ChatGoogleGenerativeAI(
    model=config.LLM_MODEL_NAME,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def rag_search(state: RFPInputState) -> RFPOutputState:
    """
    Executes the RAG logic.
    """
    log.debug(f"Executing ChatbotNode with state: {state}")
    try:
        if not state["user_query"]:
            return {"messages": [AIMessage(content="Please provide a valid question.")]}

        rag_response = rfp_rag.get_response(
            query=state["user_query"], metadata=state.get("metadata", {})
        )
        log.debug("rag_response: ", rag_response)
        return {
            "answer": rag_response["answer"],
            "extracted_requirements": rag_response["extracted_requirements"],
            "reasoning": rag_response["reasoning"],
        }
    except Exception as e:
        log.error(f"Error in RAGNode execution: {e}")
        return {"messages": [AIMessage(content="Failed to generate desired results")]}


def router_function(state: RFPInputState):
    """
    Determines the next step in the graph.
    """
    log.info(f"Executing router for user query: {state['user_query']}.")
    try:
        message = config.ROUTER_PROMPT.format(user_query=state["user_query"])
        router_response = llm.invoke([HumanMessage(content=message)])
        if isinstance(router_response, AIMessage):
            router_response = router_response.content
        log.debug(f"Router decision: {router_response}")
        if router_response == "1" or "1" in router_response:
            return "rag_search"
        else:
            return "general_response"
    except Exception as e:
        log.error(f"Error in router execution: {e}")
        return "general_response"


def general_response(state: RFPInputState) -> RFPOutputState:
    try:
        log.debug(f"Executing general response with user query: {state['user_query']}")
        message = config.GENERAL_SYSTEM_PROMPT.format(user_query=state["user_query"])
        response = llm.invoke([HumanMessage(content=message)])
        if isinstance(response, AIMessage):
            response = response.content
        return {"answer": response}
    except Exception as e:
        msg = f"Failed to response by LLM due to {e}"
        log.error(msg)
        raise ValueError(msg)


def build_graph():
    """
    Builds and compiles the LangGraph.
    """
    try:
        rfp_graph = StateGraph(RFPInputState, output_schema=RFPOutputState)

        # Add nodes to the graph
        rfp_graph.add_node(rag_search)
        rfp_graph.add_node(general_response)

        # add edges
        rfp_graph.add_conditional_edges(
            START,
            router_function,
            ["rag_search", "general_response"],
        )
        rfp_graph.add_edge("rag_search", END)
        rfp_graph.add_edge("general_response", END)

        # Compile the graph with a memory saver
        compiled_graph = rfp_graph.compile()
        log.info("Graph compiled successfully.")
    except Exception as e:
        msg = f"Failed to compile LangGraph graph"
        log.error(msg)
        raise
    return compiled_graph
