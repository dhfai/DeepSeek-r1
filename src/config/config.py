from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MEMORY_DIR = BASE_DIR / "memory"

# Model configurations
MODEL_CONFIG = {
    "local_model": "rpp:latest",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "temperature": 0.7,
    "max_tokens": 2000
}

# Vector Store configurations
VECTOR_STORE_CONFIG = {
    "collection_name": "rpp_knowledge_base",
    "persist_directory": str(MODELS_DIR / "vector_store")
}

# Memory Store configurations
MEMORY_STORE_CONFIG = {
    "persist_directory": str(MEMORY_DIR / "personal_memory"),
    "max_memory_items": 1000
}

# API configurations
API_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_model": "gpt-4o-mini"
}

# Data processing configurations
DATA_CONFIG = {
    "allowed_extensions": [".pdf", ".docx", ".txt"],
    "max_file_size": 10 * 1024 * 1024
}

# Create necessary directories
for directory in [DATA_DIR, MODELS_DIR, MEMORY_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
