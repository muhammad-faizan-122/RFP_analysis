from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.eval.utils import format_retrieved_document, extract_scores
from langchain_core.messages import AIMessage, HumanMessage
from src.common.logger import setup_logger
from src.eval import prompts
from dotenv import load_dotenv

load_dotenv()


log = setup_logger("eval_rag.log")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def rag_answer_eval(rag_response: dict):
    user_query = rag_response.get("user_query", "")
    if not user_query:
        log.error("user_query is missing in rag_response")
        raise ValueError("user_query is missing in rag_response")
    answer = rag_response.get("answer", "")
    if not answer:
        log.error("answer is missing in rag_response")
        raise ValueError("answer is missing in rag_response")
    retrieved_docs = rag_response.get("extracted_requirements", [])
    if not retrieved_docs:
        log.error("extracted_requirements is missing in rag_response")
        raise ValueError("extracted_requirements is missing in rag_response")

    message = prompts.ANSWER_RELEVANCY.format(
        user_query=user_query,
        relevant_documents=format_retrieved_document(retrieved_docs),
        answer=answer,
    )

    # Generate question
    answer_eval_response = llm.invoke([HumanMessage(content=message)])
    log.info(f"Answer Evaluation Response: {answer_eval_response}")
    if isinstance(answer_eval_response, AIMessage):
        answer_eval_response = answer_eval_response.content
    return answer_eval_response


def rag_reasoning_eval(rag_response: dict):
    user_query = rag_response.get("user_query", "")
    if not user_query:
        log.error("user_query is missing in rag_response")
        raise ValueError("user_query is missing in rag_response")
    reasoning = rag_response.get("reasoning", "")
    if not reasoning:
        log.error("reasoning is missing in rag_response")
        raise ValueError("reasoning is missing in rag_response")
    retrieved_docs = rag_response.get("extracted_requirements", [])
    if not retrieved_docs:
        log.error("extracted_requirements is missing in rag_response")
        raise ValueError("extracted_requirements is missing in rag_response")
    # System message
    message = prompts.EVAL_REASONING_QUALITY.format(
        user_query=user_query,
        reasoning_text=reasoning,
        retrieved_documents=format_retrieved_document(retrieved_docs),
    )

    resoning_eval_response = llm.invoke([HumanMessage(content=message)])
    if isinstance(resoning_eval_response, AIMessage):
        resoning_eval_response = resoning_eval_response.content
    log.info(f"Reasoning Evaluation Response: {resoning_eval_response}")
    return resoning_eval_response


def calculate_retrieved_relevancy_score(rag_response: dict):
    total_retrieved_docs = len(rag_response["extracted_requirements"])
    relevant_count = rag_response["reasoning"].lower().count("relevance: yes")
    relevant_doc_percentage = (relevant_count / total_retrieved_docs) * 100
    log.info(f"Retrieved Documents Relevancy scores: {relevant_doc_percentage}")
    return relevant_doc_percentage


def calculate_answer_relevancy_scores(rag_response: dict, total_scores=30):
    answer_eval_output = rag_answer_eval(rag_response)
    scores = extract_scores(answer_eval_output)
    log.info(f"Extracted Answer Relevancy Scores: {scores}")

    # Extract individual scores
    accuracy_scores = (
        scores["accuracy"]["score"]
        if scores.get("accuracy") and "score" in scores.get("accuracy", {})
        else 0
    )
    completeness_scores = (
        scores["completeness"]["score"]
        if scores.get("completeness") and "score" in scores.get("completeness", {})
        else 0
    )

    clarity_scores = (
        scores["clarity"]["score"]
        if scores.get("clarity") and "score" in scores.get("clarity", {})
        else 0
    )
    log.info(
        f"Individual Answer Relevancy Scores - Accuracy: {accuracy_scores}, Completeness: {completeness_scores}, Clarity: {clarity_scores}"
    )
    # Calculate combined score out of 100
    obtained_scores = clarity_scores + accuracy_scores + completeness_scores
    combined_score = round((obtained_scores / total_scores) * 100, 2)
    return combined_score


def calculate_reasoning_eval_scores(rag_response: dict, total_scores=30):
    reasoning_eval_output = rag_reasoning_eval(rag_response)
    scores = extract_scores(reasoning_eval_output)
    log.info(f"Extracted Reasoning Quality Scores: {scores}")

    # Extract individual scores
    clarity_scores = (
        scores["clarity"]["score"]
        if scores.get("clarity") and "score" in scores.get("clarity", {})
        else 0
    )
    relevance_scores = (
        scores["relevance"]["score"]
        if scores.get("relevance") and "score" in scores.get("relevance", {})
        else 0
    )

    depth_scores = (
        scores["depth"]["score"]
        if scores.get("depth") and "score" in scores.get("depth", {})
        else 0
    )
    log.info(
        f"Individual Reasoning Quality Scores - Clarity: {clarity_scores}, Relevance: {relevance_scores}, Depth: {depth_scores}"
    )
    # Calculate combined score out of 100
    obtained_scores = clarity_scores + relevance_scores + depth_scores
    combined_score = round((obtained_scores / total_scores) * 100, 2)
    return combined_score


def evaluate_rag_response(rag_response: dict):
    answer_relevancy_score = calculate_answer_relevancy_scores(rag_response)
    reasoning_quality_score = calculate_reasoning_eval_scores(rag_response)
    retrieved_relevancy_score = calculate_retrieved_relevancy_score(rag_response)

    evaluation_summary = {
        "answer_relevancy_score": answer_relevancy_score,
        "reasoning_quality_score": reasoning_quality_score,
        "retrieved_relevancy_score": retrieved_relevancy_score,
    }
    return evaluation_summary
