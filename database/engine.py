from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()
DB_URL = f'postgresql+asyncpg://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@postgres:5432/{os.getenv("DB_NAME")}'


engine = create_async_engine(
    DB_URL,
    echo=False      #TODO отключить потом
) 

async_session = sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession,
    autoflush=True
)
