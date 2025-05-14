import os
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from pathlib import Path

class PDFRAG:
    def __init__(self, model_name: str = "rpp:latest"):
        """
        Inisialisasi PDFRAG dengan model yang diinginkan

        Args:
            model_name (str): Nama model Ollama yang akan digunakan
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.llm = Ollama(model=model_name)
        self.vector_store = None
        self.loaded_docs = {}  # Menyimpan informasi dokumen yang sudah dimuat

    def scan_pdf_directory(self, directory: str) -> List[str]:
        """
        Memindai direktori untuk file PDF

        Args:
            directory (str): Path ke direktori yang akan dipindai

        Returns:
            List[str]: List path file PDF yang ditemukan
        """
        pdf_files = []
        for file in Path(directory).rglob("*.pdf"):
            pdf_files.append(str(file))
        return pdf_files

    def load_pdf(self, pdf_path: str) -> List[str]:
        """
        Memuat dan memproses file PDF

        Args:
            pdf_path (str): Path ke file PDF

        Returns:
            List[str]: List dari chunks teks
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File PDF tidak ditemukan: {pdf_path}")

        # Load PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        # Split text menjadi chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(pages)

        # Simpan informasi dokumen
        self.loaded_docs[pdf_path] = {
            "chunks": len(chunks),
            "pages": len(pages)
        }

        # Buat vector store
        if self.vector_store is None:
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
        else:
            # Tambahkan dokumen baru ke vector store yang sudah ada
            self.vector_store.add_documents(chunks)

        return chunks

    def load_directory(self, directory: str) -> Dict[str, int]:
        """
        Memuat semua file PDF dalam direktori

        Args:
            directory (str): Path ke direktori yang berisi file PDF

        Returns:
            Dict[str, int]: Informasi tentang dokumen yang dimuat
        """
        pdf_files = self.scan_pdf_directory(directory)
        if not pdf_files:
            print(f"Tidak ditemukan file PDF di direktori: {directory}")
            return {}

        print(f"\nDitemukan {len(pdf_files)} file PDF:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"{i}. {os.path.basename(pdf_file)}")

        print("\nMemuat dokumen...")
        for pdf_file in pdf_files:
            try:
                self.load_pdf(pdf_file)
                print(f"✓ Berhasil memuat: {os.path.basename(pdf_file)}")
            except Exception as e:
                print(f"✗ Gagal memuat {os.path.basename(pdf_file)}: {str(e)}")

        return self.loaded_docs

    def query(self, question: str) -> str:
        """
        Melakukan query terhadap dokumen yang sudah di-load

        Args:
            question (str): Pertanyaan yang ingin diajukan

        Returns:
            str: Jawaban dari model
        """
        if self.vector_store is None:
            raise ValueError("Harap load PDF terlebih dahulu menggunakan load_directory()")

        # Buat chain untuk QA
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3})
        )

        # Lakukan query
        response = qa_chain.invoke({"query": question})
        return response["result"]

def main():
    # Contoh penggunaan
    rag = PDFRAG(model_name="rpp:latest")

    # Load PDF dari direktori
    pdf_dir = input("Masukkan path direktori yang berisi file PDF: ")
    try:
        loaded_docs = rag.load_directory(pdf_dir)

        if loaded_docs:
            print("\nRingkasan dokumen yang dimuat:")
            for doc_path, info in loaded_docs.items():
                print(f"- {os.path.basename(doc_path)}: {info['pages']} halaman, {info['chunks']} chunks")

            # Loop untuk bertanya
            while True:
                question = input("\nMasukkan pertanyaan (ketik 'keluar' untuk berhenti): ")
                if question.lower() == 'keluar':
                    break

                try:
                    answer = rag.query(question)
                    print("\nJawaban:", answer)
                except Exception as e:
                    print(f"Error saat query: {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
