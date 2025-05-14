from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import logging

from ..config.config import MODEL_CONFIG, VECTOR_STORE_CONFIG

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_CONFIG["embedding_model"]
        )
        self.vector_store = None
        self.logger = logging.getLogger(__name__)
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize or load existing vector store"""
        try:
            self.vector_store = Chroma(
                collection_name=VECTOR_STORE_CONFIG["collection_name"],
                embedding_function=self.embeddings,
                persist_directory=VECTOR_STORE_CONFIG["persist_directory"]
            )
            self.logger.info("Vector store initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(self, documents: List[Document], metadata: Dict[str, Any] = None):
        """
        Add documents to vector store

        Args:
            documents (List[Document]): List of documents to add
            metadata (Dict[str, Any], optional): Additional metadata
        """
        try:
            if not self.vector_store:
                self._initialize_vector_store()

            # Add metadata to documents if provided
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            # Add documents to vector store
            self.vector_store.add_documents(documents)
            self.vector_store.persist()

            self.logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search

        Args:
            query (str): Search query
            k (int): Number of results to return

        Returns:
            List[Document]: List of similar documents
        """
        try:
            if not self.vector_store:
                self._initialize_vector_store()

            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            self.logger.error(f"Error performing similarity search: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection

        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            if not self.vector_store:
                self._initialize_vector_store()

            collection = self.vector_store._collection
            stats = {
                "count": collection.count(),
                "name": collection.name,
                "metadata": collection.metadata
            }
            return stats
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            raise

    def clear_collection(self):
        """Clear all documents from the vector store"""
        try:
            if not self.vector_store:
                self._initialize_vector_store()

            self.vector_store._collection.delete(where={})
            self.vector_store.persist()
            self.logger.info("Vector store collection cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing vector store: {str(e)}")
            raise
