import pandas as pd
from sqlalchemy import select, Result
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from engine import db_engine, today


async def write_data(session: AsyncSession, table: DeclarativeAttributeIntercept, data: list | dict) -> None:
    await session.execute(insert(table).values(data).on_conflict_do_nothing())
    await session.commit()


async def resumes_out(base: DeclarativeAttributeIntercept):
    query = select(
        base.id, base.title, base.age, base.excpirience, base.salary, base.status, base.prev_employment
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
