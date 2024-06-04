import os
from asyncio import current_task
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session

today = date.today()
root_path = Path(os.path.abspath(__file__)).parent


class Settings(BaseSettings):
    driver_name: str
    username: str
    password: SecretStr
    host: str
    port: int
    echo: bool
    database: str


settings = Settings(_env_file=f"{root_path}/.env")


def get_url(engine_settings: Settings) -> URL:
    url_object = URL.create(
        drivername=engine_settings.driver_name,
        username=engine_settings.username,
        password=engine_settings.password.get_secret_value(),
        host=engine_settings.host,
        database=engine_settings.database,
        port=engine_settings.port
    )
    return url_object


class DataBase:
    def __init__(self, url: URL, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            poolclass=NullPool
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def scoped_session(self) -> AsyncSession:
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        try:
            async with session() as s:
                yield s
        finally:
            await session.remove()


