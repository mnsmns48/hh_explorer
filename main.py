import asyncio
import time
from datetime import datetime

import aiohttp

from engine import database_sync, db_engine, settings
from logger_config import logger
from scrape_resumes import scrape_resumes

from scrape_vacancies import scrape_vacancies
from models import Base

TEXT = 'Python разработчик'
AREA = 2


async def start_scrape():
    # Создаем таблицы, если они ещё не созданы или очищаем данные, если есть
    await database_sync(engine=db_engine, db_settings=settings, base=Base)
    logger.info('DataBase synchronized')
    # Собираем вакансии и добавляем в БД
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as aio_session:
        await scrape_vacancies(aio_session=aio_session, text=TEXT, area=AREA)
    # Собираем резюме и добавляем в БД
    # await scrape_resumes(text=TEXT, area=AREA)


if __name__ == '__main__':
    try:
        start = time.time()
        logger.info(f'Script started {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
        asyncio.run(start_scrape())
        logger.info(f"Script completed in {int(time.time() - start)} seconds --------------------------\n")

    except (KeyboardInterrupt, SystemExit):
        logger.info(f"Script stopped")
