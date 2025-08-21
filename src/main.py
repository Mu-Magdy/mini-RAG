from fastapi import FastAPI
from .routes import base, data, nlp
<<<<<<< HEAD
=======
from motor.motor_asyncio import AsyncIOMotorClient
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
<<<<<<< HEAD
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import sessionmaker
=======
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)

app = FastAPI()

async def startup_span():
    settings = get_settings()
<<<<<<< HEAD
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(
        postgres_conn
    )
    app.db_client = sessionmaker(app.db_engine, 
                                 class_=AsyncSession,
                                 expire_on_commit=False
                                )

 
=======
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )


async def shutdown_span():
<<<<<<< HEAD
    app.db_engine.dispose()
=======
    app.mongo_conn.close()
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
    app.vectordb_client.disconnect()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
