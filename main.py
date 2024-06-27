import asyncio
import time
from datetime import datetime

import aiohttp

from engine import database_sync, db_engine, settings

from scrape_vacancies import logic_vacancies
from scrape_areas import get_areas
from models import Base

TEXT = 'Аналитик данных'
AREA = 1


async def start_scrape():
    async with db_engine.engine.begin() as async_connect:
        await async_connect.run_sync(Base.metadata.drop_all)  # Очищаем таблицы БД
    await database_sync(engine=db_engine, db_settings=settings, base=Base)  # Создаем таблицы если они ещё не созданы
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as aio_session:
        await logic_vacancies(aio_session=aio_session, text=TEXT, area=AREA)  # Собираем данные и добавляем в БД
    # print('Введите текст запроса')
    # text = str(input())
    # print('Введите регион (целое число)')
    # area = int(input())
    # await scrape_resumes(text='Садовник', area=2)
    # await resumes_out(base=Resumes)
    # await scrape_vacancies(
    #     search_line='?text=Java+разработчик&area=113&hhtmFrom=resume_search_result&hhtmFromLabel=vacancy_search_line'
    # )


if __name__ == '__main__':
    try:
        start = time.time()
        print('script started', datetime.now())
        asyncio.run(start_scrape())
        print(f"Скрипт завершен за {int(time.time() - start)} секунд")
    except (KeyboardInterrupt, SystemExit):
        print('script stopped')
