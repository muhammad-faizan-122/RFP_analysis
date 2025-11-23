from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from operator import itemgetter
from typing import List
from src.common import config
from src.common.logger import log
from dotenv import load_dotenv
from src.common.utils import measure_time
from abc import ABC, abstractmethod
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()


class Generation(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate_response(self, query, retriever) -> str:
        return


class LcGeneration(Generation):
    """generation using Langchain module"""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL_NAME, temperature=config.TEMPERATURE
        )

        super().__init__()

    def format_retrieved_document(self, docs: List[Document]) -> str:
        log.debug(f"--- Inspecting Retrieved Documents ---: {docs}")
        formatted_context = ""

        for i, doc in enumerate(docs):
            formatted_context += f"Document-{i+1}:\n{doc.page_content}\n\n"

        log.debug(
            f"Updated Document after merging metadata: {formatted_context[:500]}..."
        )
        return {"formatted_context": formatted_context, "source_documents": docs}

    def _log_final_prompt(self, prompt: ChatPromptTemplate):
        """
        A function to debug the final prompt object before it goes to the LLM.
        """
        log.debug("--- Final Prompt Sent to LLM ---", prompt.to_string())
        return prompt  # Pass the prompt through unchanged

    def generate_retrieval_resoning(
        self,
        user_query: str,
        retrieved_documents: str,
    ) -> str:
        try:
            message = config.RETRIEVAL_REASON_PROMPT.format(
                user_query=user_query,
                retrieved_documents=retrieved_documents,
            )
            retrieval_relevany_response = self.llm.invoke(
                [HumanMessage(content=message)]
            )

            if isinstance(retrieval_relevany_response, AIMessage):
                retrieval_relevany_response = retrieval_relevany_response.content

            return retrieval_relevany_response

        except Exception as e:
            msg = f"Failed to generate retrieval reasoning for query: {user_query}\nError: {e}"
            log.error(msg)
            raise ValueError(msg)

    def validate_and_process_rag_response(self, rag_response: dict) -> dict:
        try:
            extracted_docs, extracted_formatted_docs = [], ""
            user_query = rag_response.get("input", "")
            answer = rag_response.get("answer", "")

            if isinstance(answer, AIMessage):
                answer = answer.content

            retrieved_data = rag_response.get("retrieved_data", {})
            if retrieved_data:
                extracted_docs = retrieved_data.get("source_documents", [])
                extracted_formatted_docs = retrieved_data.get("formatted_context", "")

            return {
                "user_query": user_query,
                "answer": answer,
                "extracted_requirements": extracted_docs,
                "reasoning": (
                    self.generate_retrieval_resoning(
                        user_query,
                        extracted_formatted_docs,
                    )
                    if extracted_formatted_docs
                    else ""
                ),
            }
        except Exception as e:
            msg = f"Failed to valid to RAG response: {rag_response}\nError: {e}"
            log.error(msg)
            raise ValueError(msg)

    def generate_response(self, query, retriever) -> str:
        """
        Creates and returns the main RAG chain. This chain:
        1. Retrieves documents.
        2. Allows inspection of the Document objects.
        3. Formats the documents' page_content into a single string.
        4. Assigns that string to the 'context' variable.
        5. Logs the final prompt before sending it to the LLM.
        6. Invokes the LLM and parses the output.

        Args:
            retriever: The configured EnsembleRetriever to use for fetching context.

        Returns:
            A runnable RAG chain.
        """

        with measure_time("retrieve relevant documents", log):
            retrieval_branch = (
                itemgetter("input")
                | retriever
                | RunnableLambda(self.format_retrieved_document)
            )

        with measure_time("Augment & Generation Chain initialization", log):
            rag_chain = RunnableParallel(
                # Get the dictionary (contains both string and docs)
                retrieved_data=retrieval_branch,
                # Pass input through
                input=itemgetter("input"),
            ).assign(
                # pull 'formatted_context' from the dictionary for the prompt
                answer=(
                    {
                        "context": lambda x: x["retrieved_data"]["formatted_context"],
                        "input": itemgetter("input"),
                    }
                    | config.RAG_GENERATION_PROMPT
                    | self.llm
                )
            )

        log.info(
            "RAG chain with document formatting and prompt inspection created successfully."
        )
        with measure_time("RAG answer generation", log):
            response = rag_chain.invoke({"input": query})
        response = self.validate_and_process_rag_response(response)
        return (
            response
            if response and isinstance(response, dict)
            else "Sorry I am unable to answer from RFP Knowledge base"
        )
