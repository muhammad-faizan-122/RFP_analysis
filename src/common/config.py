from langchain_core.prompts import ChatPromptTemplate

# --- Paths and Directories ---
DB_PERSIST_DIRECTORY = "chroma_db"

# --- Embedding Model Configuration ---
EMBEDDING_TYPE = "jina"


# --- Retriever Configuration ---
ENSEMBLE_RETRIEVER_WEIGHTS = [0.5, 0.5]  # [dense, sparse]
DENSE_RETRIEVED_DOCUMENTS = 3
SPARSE_RETRIEVED_DOCUMENTS = 3

# --- LLM and Prompt Configuration ---
LLM_MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.0

ROUTER_PROMPT = """You are a router. Your job is to decide whether the user's query is related to RFP (Request for Proposal) documents or not. 
Return:
- "1" if the query is related to RFPs (e.g., proposals, bidding, procurement, deadlines, scope of work, requirements, compliance, evaluation criteria, or anything that should be answered from RFP documents).
- "0" if the query is general or conversation and not related to RFPs.

Only return "1" or "0" with no additional text.
<user_query>
{user_query}
</user_query>"""

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant. Given RFP document similar for user's query, your task is to answer the user's query "
    "based *only* on these documents.\n"
    "Do NOT make up any answers. If the answer is not found in it, respond with: "
    "'I cannot answer this based on the provided information.'\n\n"
    "RFP document: {context}"
)
GENERAL_SYSTEM_PROMPT = """You're helpful assistant. Response User query very concisely and friendly.
{user_query}"""
RAG_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)

RETRIEVAL_REASON_PROMPT = """Your are expert RAG retrieval evaluator. \
Given user query and retrieved documents, your task is to validate with \
valid reasoning whether each retrieved document are relevant with respect to user query. \
Your evaluating reasoning must be concise and factual.
<user_query>
{user_query}
</user_query?

<retrieved_documents>
{retrieved_documents}
</retrieved_documents>

Follow this output format to evalute each document
Document-index
Relevance: Yes/No
Reasoning: Why Relevant or not relevant?
"""

QUERY_BREAK_PROMPT = """You are given RAG bot user query. If user asked multiple queries in single given query, you have to break all unique query in output. If there is only query, return empty list.
<query>
{query}
</query>"""
