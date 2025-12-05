from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from operator import itemgetter
from src.common import config
from src.common.logger import log
from dotenv import load_dotenv
from src.common.utils import measure_time
from abc import ABC, abstractmethod
from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, Any
from src.rag.models import UserQueries

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

    def is_any_metadata_match(
        self,
        doc_metadata: Dict[str, Any],
        filter_metadata: Dict[str, Any],
    ) -> bool:
        for key, value in filter_metadata.items():
            if key in doc_metadata and doc_metadata[key] == value:
                return True
        return False

    def is_any_metadata_filter_exists(self, filter_metadata: Dict[str, Any]) -> bool:
        """check if any metadata filter exists"""
        if not filter_metadata:
            return False

        for v in filter_metadata.values():
            if v:
                return True
        return False

    def format_retrieved_document(
        self, inputs: Dict[str, Any], fallback_docs: int = 2
    ) -> str:
        try:
            docs = inputs["docs"]
            if not docs:
                log.warning("No documents retrieved.")
                return {"formatted_context": "", "source_documents": []}

            metadata_filters = inputs["metadata"]

            log.debug(
                f"--- Raw Docs Retrieved: {len(docs)} - first doc value: {docs[0]}---"
            )
            log.debug(
                f"--- Applying Filters: type: {type(metadata_filters)} - value: {metadata_filters} ---"
            )

            formatted_context = ""
            filter_context = []
            is_filter_exists = self.is_any_metadata_filter_exists(metadata_filters)
            doc_i = 0
            for doc in docs:
                # check if either metadata matches or no filter exists
                if (
                    self.is_any_metadata_match(doc.metadata, metadata_filters)
                    or not is_filter_exists
                ):
                    doc_i += 1
                    formatted_context += f"Document-{doc_i}:\n{doc.page_content}\n\n"
                    filter_context.append(doc)

            # fallback case: if no documents matched, return top 2 docs
            if not formatted_context:
                log.warning("No documents matched the metadata filters.")
                if len(docs) < fallback_docs:
                    fallback_docs = len(docs)
                filter_context = docs[:fallback_docs]
                for i, doc in enumerate(docs[:fallback_docs]):
                    formatted_context += f"Document-{i+1}:\n{doc.page_content}\n\n"
            log.debug(f"total source documents after filter: {len(filter_context)}")
            log.debug(f"Updated Document after merging metadata:\n{formatted_context}")
            return {
                "formatted_context": formatted_context,
                "source_documents": filter_context,
            }

        except Exception as e:
            msg = f"Failed to format retrieved documents: {e}"
            log.error(msg)
            raise ValueError(msg)

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

    def breakdown_queries(self, query: str) -> list[str]:
        """If user asked multiple queries in single queries, break down queries to improve the retrieved results"""
        try:
            structured_llm = self.llm.with_structured_output(UserQueries)
            message = config.QUERY_BREAK_PROMPT.format(query=query)
            response = structured_llm.invoke([HumanMessage(content=message)])
            response_dict = response.model_dump()
            log.debug(f"generated sub queries by LLM: {response_dict}")
            queries = response_dict.get("queries", "")
            queries = queries if queries else [query]
            return queries
        except Exception as e:
            log.error(
                f"failed to break down query, so going with original user query for retrieval"
            )
            return [query]

    def deduplicate_docs(self, docs: list[Document]) -> list[Document]:
        unique_docs = []
        seen_content = set()
        for doc in docs:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)
        return unique_docs

    def generate_response(self, query: str, retriever, metadata: dict) -> str:
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
        with measure_time("break down user query", log):
            # if user asked multiple queries in single request, breakdown into list of queries
            queries = self.breakdown_queries(query)

        def retrieve_for_multiple_queries(input_dict: dict) -> list[Document]:
            # Get the list of queries from input, default to original input if missing
            sub_queries = input_dict.get("sub_queries", [input_dict["input"]])

            all_docs = []
            log.debug(f"Retrieving documents for {len(sub_queries)} queries...")
            for q in sub_queries:
                docs = retriever.invoke(q)
                all_docs.extend(docs)

            # Deduplicate documents to avoid passing the same text twice to LLM
            unique_docs = self.deduplicate_docs(all_docs)
            log.debug(f"Total unique docs retrieved: {len(unique_docs)}")
            return unique_docs

        with measure_time("retrieve relevant documents", log):
            retrieval_branch = RunnableParallel(
                docs=RunnableLambda(retrieve_for_multiple_queries),
                metadata=itemgetter("metadata"),
            ) | RunnableLambda(self.format_retrieved_document)

        with measure_time("Augment & Generation Chain initialization", log):
            rag_chain = RunnableParallel(
                retrieved_data=retrieval_branch,
                input=itemgetter("input"),
            ).assign(
                answer=(
                    {
                        "context": lambda x: x["retrieved_data"]["formatted_context"],
                        "input": itemgetter("input"),
                    }
                    | config.RAG_GENERATION_PROMPT
                    | RunnableLambda(self._log_final_prompt)
                    | self.llm
                )
            )

        log.info(
            "RAG chain with document formatting and prompt inspection created successfully."
        )
        with measure_time("RAG answer generation", log):
            response = rag_chain.invoke(
                {
                    "input": query,
                    "sub_queries": queries,
                    "metadata": metadata,
                }
            )
        response = self.validate_and_process_rag_response(response)
        return (
            response
            if response and isinstance(response, dict)
            else "Sorry I am unable to answer from RFP Knowledge base"
        )
