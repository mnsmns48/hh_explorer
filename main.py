import asyncio
import time
from datetime import datetime

import aiohttp

from engine import database_sync, db_engine, settings
from scrape_resumes import logic_resumes

from scrape_vacancies import logic_vacancies
from models import Base

TEXT = 'Технолог'
AREA = 1844


async def start_scrape():
    # Создаем таблицы, если они ещё не созданы или очищаем данные, если есть
    # await database_sync(engine=db_engine, db_settings=settings, base=Base)
    # Собираем вакансии и добавляем в БД
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as aio_session:
    #     await logic_vacancies(aio_session=aio_session, text=TEXT, area=AREA)
    await logic_resumes(text=TEXT, area=2)



if __name__ == '__main__':
    try:
        start = time.time()
        print('script started', datetime.now())
        asyncio.run(start_scrape())
        print(f"Скрипт завершен за {int(time.time() - start)} секунд")
    except (KeyboardInterrupt, SystemExit):
        print('script stopped')
