from pathlib import Path
from typing import List, Dict, Any
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

from ..config.config import DATA_CONFIG, MODEL_CONFIG

class DataProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MODEL_CONFIG["chunk_size"],
            chunk_overlap=MODEL_CONFIG["chunk_overlap"],
            length_function=len
        )
        self.logger = logging.getLogger(__name__)

    def _get_loader(self, file_path: str):
        """Get appropriate loader based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.txt':
            return TextLoader(file_path)
        elif ext == '.docx':
            return Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def process_file(self, file_path: str) -> List[Document]:
        """
        Process a single file and return chunks

        Args:
            file_path (str): Path to the file

        Returns:
            List[Document]: List of document chunks
        """
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            if file_size > DATA_CONFIG["max_file_size"]:
                raise ValueError(f"File too large: {file_path}")

            ext = os.path.splitext(file_path)[1].lower()
            if ext not in DATA_CONFIG["allowed_extensions"]:
                raise ValueError(f"Unsupported file type: {ext}")

            # Load and process file
            loader = self._get_loader(file_path)
            documents = loader.load()

            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)

            self.logger.info(f"Successfully processed {file_path}: {len(chunks)} chunks created")
            return chunks

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def process_directory(self, directory: str) -> Dict[str, List[Document]]:
        """
        Process all supported files in a directory

        Args:
            directory (str): Path to directory

        Returns:
            Dict[str, List[Document]]: Dictionary mapping file paths to their chunks
        """
        results = {}
        directory_path = Path(directory)

        # Find all supported files
        for ext in DATA_CONFIG["allowed_extensions"]:
            for file_path in directory_path.rglob(f"*{ext}"):
                try:
                    chunks = self.process_file(str(file_path))
                    results[str(file_path)] = chunks
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {str(e)}")
                    continue

        return results

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata about a file

        Args:
            file_path (str): Path to the file

        Returns:
            Dict[str, Any]: File metadata
        """
        try:
            stats = os.stat(file_path)
            return {
                "filename": os.path.basename(file_path),
                "file_size": stats.st_size,
                "created_time": stats.st_ctime,
                "modified_time": stats.st_mtime,
                "extension": os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            self.logger.error(f"Error getting metadata for {file_path}: {str(e)}")
            raise
