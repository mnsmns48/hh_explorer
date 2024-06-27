import pandas as pd
from sqlalchemy import select, Result, update, Column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept, DeclarativeBase

from config import today
from engine import db_engine, settings
from models import Areas, Vacancies


async def get_area_title(session: AsyncSession, id_: int) -> str:
    query = select(Areas.name).filter(Areas.id == id_)
    response = await session.execute(query)
    result = response.scalar_one()
    return result


async def get_job_without_text(session: AsyncSession):
    query = (select(Vacancies.url)
             .order_by(Vacancies.id).limit(settings.job_texts_quantity))
    response = await session.execute(query)
    result = response.scalars().all()
    return result


async def write_data(session: AsyncSession, table: DeclarativeAttributeIntercept, data: list | dict) -> None:
    await session.execute(insert(table).values(data).on_conflict_do_nothing())
    await session.commit()


async def update_data(session: AsyncSession,
                      table: DeclarativeAttributeIntercept,
                      data: list | dict,
                      column: Column,
                      **kwargs) -> None:
    await session.execute(update(table).values(data).where(column == kwargs.get('value')))
    await session.commit()


async def resumes_out(base: DeclarativeAttributeIntercept) -> None:
    query = select(
        base.id, base.title, base.age, base.excpirience, base.salary, base.status, base.prev_employment, base.date,
        base.link
    ).order_by(base.id)
    async with db_engine.scoped_session() as session:
        data: Result = await session.execute(query)
        result = data.all()
    df = pd.DataFrame(result)
    writer = pd.ExcelWriter(
        f'{base.__tablename__}_{today}.xlsx'
    )
    try:
        df.to_excel(writer, index=False)
    finally:
        writer.close()
        print(f'Ready')
