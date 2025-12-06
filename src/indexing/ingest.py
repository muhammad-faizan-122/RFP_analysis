from src.indexing.utils import (
    split_by_headings,
    get_pdf_markdown,
    rm_markdown,
    extract_rfp_metadata,
    merge_shorter_sections,
    save_documents_to_json,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
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
    rfp_metadata = extract_rfp_metadata(h2h_sections[0], file_name)
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


def create_finalize_chunks(sections: list[str], file_name):
    """
    1- check is any heading to heading section require furter chunking, if require do recurrsive charater for that particular section only.
    2- add Metadata for each chunk
    """
    rfp_metadata = extract_rfp_metadata(sections[0], file_name)
    final_chunks = []
    for section in sections:
        clean_section = rm_markdown(section)
        section_tokens = len(clean_section.split())
        if section_tokens > configs.CHUNK_SIZE:
            sub_chunks = get_recurrsive_chunks(clean_section)
            for sub_chunk in sub_chunks:
                final_chunks.append(
                    Document(page_content=sub_chunk, metadata=rfp_metadata.copy())
                )
        else:
            final_chunks.append(
                Document(page_content=clean_section, metadata=rfp_metadata.copy())
            )
    return final_chunks


def get_recurrsive_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=configs.CHUNK_SIZE,
        chunk_overlap=configs.CHUNK_OVERLAP,
        separators=configs.SEPARATORS,
    )
    chunks = text_splitter.split_text(text)
    return chunks


def chunk_pdf(pdf_path: str) -> list:
    md_text = get_pdf_markdown(pdf_path)
    h2h_sections = split_by_headings(md_text)
    if not h2h_sections:
        log.warning(f"No headings found for {pdf_path}")
        return []
    merged_sections = merge_shorter_sections(h2h_sections)
    chunks = create_finalize_chunks(
        merged_sections, file_name=os.path.basename(pdf_path)
    )
    save_documents_to_json(chunks, os.path.basename(pdf_path))
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
        return len(documents)
    except Exception as e:
        log.error(f"Data ingestion failed: {e}")
        raise e
