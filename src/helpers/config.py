from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

<<<<<<< HEAD
    
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
=======
    MONGODB_URL: str
    MONGODB_DATABASE: str
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

<<<<<<< HEAD
    GENERATION_MODEL_ID_LETIRAL: List[str] = None
=======
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

<<<<<<< HEAD
    VECTOR_DB_BACKEND_LETIRAL: List[str] = None
=======
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None

    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"

    class Config:
        env_file = "src/.env"

def get_settings():
    return Settings()
