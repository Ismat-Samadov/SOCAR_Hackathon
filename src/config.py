from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-08-01-preview"

    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""

    # Application Configuration
    data_dir: Path = Path("./data")
    pdf_dir: Path = Path("./data/pdfs")
    vector_db_path: Path = Path("./data/vector_db")
    processed_dir: Path = Path("./data/processed")

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # OCR Settings
    ocr_backend: str = "azure"  # Options: azure, paddle, easy, tesseract

    # LLM Settings
    llm_model: str = "gpt-4o"  # Model deployment name (gpt-4o, gpt-35-turbo, deepseek-chat, etc.)

    # Pinecone Settings
    pinecone_api_key: str = ""
    pinecone_index_name: str = "socar-documents"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    vector_db_type: str = "chroma"  # Options: chroma, pinecone

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


settings = Settings()
