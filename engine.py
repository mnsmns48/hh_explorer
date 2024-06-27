from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Type

import asyncpg
from asyncpg import InvalidCatalogNameError
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session
from sqlalchemy.orm import DeclarativeBase

from config import Settings

settings = Settings()


def get_url(engine_settings: Settings) -> URL:
    # формирует строку для движка обращения к БД
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


db_engine = DataBase(get_url(engine_settings=settings), echo=settings.echo)


async def database_sync(engine: DataBase,
                        db_settings: Settings,
                        base: Type[
                            DeclarativeBase]):
    # Функция создания БД и таблиц.
    # Не работает под Windows.
    # Если работаете под Windows, просто создайте БД вручную. Таблицы "подтянуться"
    try:
        async with engine.engine.begin() as async_connect:
            await async_connect.run_sync(base.metadata.create_all)
    except InvalidCatalogNameError:
        conn = await asyncpg.connect(database='postgres',
                                     user=db_settings.username,
                                     password=db_settings.password.get_secret_value(),
                                     host=db_settings.host,
                                     port=db_settings.port
                                     )
        sql = f'CREATE DATABASE "{db_settings.database}"'
        await conn.execute(sql)
        await conn.close()
        print(f"DB <{db_settings.database}> success created")
    async with engine.engine.begin() as async_connect:
        await async_connect.run_sync(base.metadata.create_all)
