from config import load_database_config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


config = load_database_config()
engine = create_async_engine(
    url=f"postgresql+asyncpg://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}",
    echo=False,
)
session_factory = async_sessionmaker(engine)
