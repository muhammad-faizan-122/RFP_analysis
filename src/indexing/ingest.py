from src.indexing.utils import (
    split_by_headings,
    get_pdf_markdown,
    rm_markdown,
    extract_rfp_metadata,
    save_documents_to_json,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.indexing import configs
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import JinaEmbeddings
from src.common.logger import setup_logger
from dotenv import load_dotenv
import os
import shutil


load_dotenv()


log = setup_logger("indexing.log")


def chunk_h2h_sections(h2h_sections: list[str], file_name: str) -> list[Document]:
    rfp_metadata = extract_rfp_metadata(h2h_sections[0])
    if isinstance(rfp_metadata, dict):
        rfp_metadata["file_name"] = file_name
    else:
        rfp_metadata = {"file_name": file_name}

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=configs.CHUNK_SIZE,
        chunk_overlap=configs.CHUNK_OVERLAP,
        separators=configs.SEPARATORS,
    )

    chunks = text_splitter.create_documents(h2h_sections)
    for i in range(len(chunks)):
        chunks[i].page_content = rm_markdown(chunks[i].page_content)
        chunks[i].metadata = rfp_metadata.copy()
    return chunks


def chunk_pdf(pdf_path: str) -> list:
    md_text = get_pdf_markdown(pdf_path)
    h2h_sections = split_by_headings(md_text)
    if not h2h_sections:
        log.warning(f"No headings found for {pdf_path}")
        return []
    chunks = chunk_h2h_sections(h2h_sections, file_name=os.path.basename(pdf_path))
    log.info(f"Total Chunks Created from {pdf_path}: {len(chunks)}")
    return chunks


def chunk_all_pdfs(pdfs_dir: str) -> list[str]:
    all_chunks = []
    for file in os.listdir(pdfs_dir):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdfs_dir, file)
            chunks = chunk_pdf(pdf_path)
            all_chunks.extend(chunks)
    log.info(f"Total Chunks Created from all PDFs: {len(all_chunks)}")
    return all_chunks


def ingest_data():
    # Clear existing database directory
    log.info("Starting data ingestion process...")
    try:
        if os.path.exists(configs.DB_PERSIST_DIRECTORY):
            shutil.rmtree(configs.DB_PERSIST_DIRECTORY)

        log.info("Cleared existing database directory.")
        # get chunks of all pdf files
        documents = chunk_all_pdfs(configs.DATA_DIR)
        if not documents:
            log.warning("No documents to ingest. Exiting ingestion process.")
            return
        # save_documents_to_json(documents)
        # embed documents and store in ChromaDB
        Chroma.from_documents(
            documents=documents,
            embedding=JinaEmbeddings(model_name="jina-embeddings-v3"),
            persist_directory=configs.DB_PERSIST_DIRECTORY,
        )
        log.info("Data ingestion completed successfully.")
    except Exception as e:
        log.error(f"Data ingestion failed: {e}")
        raise e
