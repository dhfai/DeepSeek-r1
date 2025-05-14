from typing import Dict, Any, List, Optional
import logging
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from ..config.config import MODEL_CONFIG, API_CONFIG
from ..data.data_processor import DataProcessor
from ..models.vector_store import VectorStoreManager
from ..memory.memory_store import MemoryStoreManager

class RPPAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.data_processor = DataProcessor()
        self.vector_store = VectorStoreManager()
        self.memory_store = MemoryStoreManager()

        # Initialize local model
        self.llm = Ollama(
            model=MODEL_CONFIG["local_model"],
            temperature=MODEL_CONFIG["temperature"],
            num_ctx=MODEL_CONFIG["max_tokens"]
        )

        # Initialize local embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_CONFIG["embedding_model"]
        )

        # Initialize RAG chain
        self._initialize_rag_chain()

    def _initialize_rag_chain(self):
        """Initialize the RAG chain with custom prompt for local model"""
        try:
            # Custom prompt template untuk RPP dengan model lokal
            prompt_template = """
            Kamu adalah asisten yang ahli dalam membuat Rencana Pelaksanaan Pembelajaran (RPP).
            Berdasarkan informasi dari dokumen sumber, buatkan RPP yang sesuai dengan kurikulum dan kebutuhan siswa.

            Informasi dari Dokumen Sumber:
            {context}

            Detail RPP yang Diminta:
            {question}

            Buatkan RPP yang lengkap dengan komponen berikut:
            1. Identitas (Sekolah, Mata Pelajaran, Kelas/Semester, Materi, Alokasi Waktu)
            2. Kompetensi Dasar dan Indikator Pencapaian Kompetensi
            3. Tujuan Pembelajaran
            4. Materi Pembelajaran
            5. Metode Pembelajaran
            6. Media, Alat, dan Sumber Belajar
            7. Langkah-langkah Pembelajaran:
               - Pendahuluan: Apersepsi dan motivasi
               - Inti:
                 * Kegiatan mengamati
                 * Kegiatan menanya
                 * Kegiatan mengumpulkan informasi
                 * Kegiatan mengasosiasi
                 * Kegiatan mengkomunikasikan
                 * Berikan contoh soal yang relevan dan bervariasi
               - Penutup: Refleksi dan evaluasi
            8. Penilaian:
               - Teknik penilaian
               - Bentuk instrumen
               - Rubrik penilaian
               - Contoh soal dan jawaban

            Berikan jawaban yang terstruktur dan sesuai dengan format RPP yang baik.
            Pastikan contoh soal yang diberikan bervariasi dan sesuai dengan tingkat kesulitan siswa.
            """

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )

            # Inisialisasi RAG chain dengan model lokal
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.vector_store.as_retriever(
                    search_kwargs={"k": 3}
                ),
                chain_type_kwargs={
                    "prompt": prompt,
                    "verbose": True
                }
            )

            self.logger.info("RAG chain initialized successfully with local model")
        except Exception as e:
            self.logger.error(f"Error initializing RAG chain: {str(e)}")
            raise

    def _get_relevant_feedback(self, context: Dict[str, Any]) -> str:
        """Get relevant feedback based on context"""
        try:
            # Get recent feedback
            feedback_memories = self.memory_store.get_memories(
                memory_type="feedback",
                limit=5
            )

            if not feedback_memories:
                return ""

            # Filter feedback based on context
            relevant_feedback = []
            for memory in feedback_memories:
                if memory["metadata"].get("context", {}).get("mata_pelajaran") == context.get("mata_pelajaran"):
                    relevant_feedback.append(memory["content"].get("feedback", ""))

            return "\n".join(relevant_feedback) if relevant_feedback else ""
        except Exception as e:
            self.logger.error(f"Error getting relevant feedback: {str(e)}")
            return ""

    def process_documents(self, directory: str) -> Dict[str, Any]:
        """
        Process documents in a directory and add to vector store

        Args:
            directory (str): Path to directory containing documents

        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            # Process documents
            processed_docs = self.data_processor.process_directory(directory)

            # Add to vector store
            for file_path, chunks in processed_docs.items():
                metadata = self.data_processor.get_metadata(file_path)
                self.vector_store.add_documents(chunks, metadata)

                # Store processing memory
                self.memory_store.add_memory(
                    "document_processing",
                    {
                        "file_path": file_path,
                        "chunks_count": len(chunks)
                    },
                    metadata
                )

            return {
                "processed_files": len(processed_docs),
                "total_chunks": sum(len(chunks) for chunks in processed_docs.values())
            }
        except Exception as e:
            self.logger.error(f"Error processing documents: {str(e)}")
            raise

    def generate_rpp(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate RPP based on query and context using local model

        Args:
            query (str): Query for RPP generation
            context (Dict[str, Any], optional): Additional context

        Returns:
            Dict[str, Any]: Generated RPP
        """
        try:
            # Get relevant documents using local embeddings
            relevant_docs = self.vector_store.similarity_search(query)

            # Prepare context from relevant documents
            context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

            # Generate RPP using local model
            response = self.qa_chain.invoke({
                "query": query,
                "context": context_text,
            })

            # Store interaction memory
            self.memory_store.add_memory(
                "rpp_generation",
                {
                    "query": query,
                    "response": response["result"],
                    "context": context,
                    "sources": [doc.metadata for doc in relevant_docs],
                }
            )

            return {
                "rpp": response["result"],
                "sources": [doc.metadata for doc in relevant_docs]
            }
        except Exception as e:
            self.logger.error(f"Error generating RPP: {str(e)}")
            raise

    def get_feedback(self, rpp_id: str, feedback: Dict[str, Any]):
        """
        Store feedback for generated RPP

        Args:
            rpp_id (str): ID of the RPP
            feedback (Dict[str, Any]): Feedback content
        """
        try:
            # Add feedback type for better categorization
            feedback_type = "content" if "contoh soal" in feedback.get("feedback", "").lower() else "general"

            self.memory_store.add_memory(
                "feedback",
                {
                    **feedback,
                    "feedback_type": feedback_type
                },
                {"rpp_id": rpp_id}
            )
            self.logger.info(f"Feedback stored for RPP: {rpp_id}")
        except Exception as e:
            self.logger.error(f"Error storing feedback: {str(e)}")
            raise

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics

        Returns:
            Dict[str, Any]: System statistics
        """
        try:
            vector_store_stats = self.vector_store.get_collection_stats()
            memory_stats = {
                "total_memories": len(self.memory_store.get_memories()),
                "memory_types": {
                    "document_processing": len(self.memory_store.get_memories("document_processing")),
                    "rpp_generation": len(self.memory_store.get_memories("rpp_generation")),
                    "feedback": len(self.memory_store.get_memories("feedback"))
                }
            }

            return {
                "vector_store": vector_store_stats,
                "memory_store": memory_stats,
                "model": {
                    "name": MODEL_CONFIG["local_model"],
                    "embedding_model": MODEL_CONFIG["embedding_model"]
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {str(e)}")
            raise
