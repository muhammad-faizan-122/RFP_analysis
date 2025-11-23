from src.common.utils import measure_time
from abc import ABC, abstractmethod
from src.common.logger import log
from src.common import config


class Embedder(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_embeder(self):
        return


class HfEmbedder(Embedder):
    def __init__(self):
        super().__init__()

    def get_embeder(self):
        try:
            log.info("Loading embedding model...")
            with measure_time("embedding model loading", log):
                from langchain_huggingface import HuggingFaceEmbeddings

                embeddings = HuggingFaceEmbeddings(
                    model_name="BAAI/bge-base-en-v1.5",
                    model_kwargs={"device": "cpu"},  # Use "cuda" for GPU,
                    encode_kwargs={"normalize_embeddings": False},
                )
                return embeddings
        except Exception as e:
            log.error(f"Failed to load the HuggingFace embedding Instance: {e}")
            raise


class JinaEmbedder(Embedder):
    def __init__(self):
        super().__init__()

    def get_embeder(self):
        try:
            log.info("Loading embedding model...")
            with measure_time("embedding model loading", log):
                from langchain_community.embeddings import JinaEmbeddings

                embeddings = JinaEmbeddings(model_name="jina-embeddings-v3")
                return embeddings
        except Exception as e:
            log.error(f"Failed to load the HuggingFace embedding Instance: {e}")
            raise


def get_embeddings_obj():
    log.info(f"Embedding model type: {config.EMBEDDING_TYPE}")
    if config.EMBEDDING_TYPE == "jina":
        return JinaEmbedder().get_embeder()
    elif config.EMBEDDING_TYPE == "hf":
        return HfEmbedder().get_embeder()
    else:
        raise ValueError(f"Wrong embedding type: {config.EMBEDDING_TYPE}")
