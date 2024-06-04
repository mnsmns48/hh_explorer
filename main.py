import asyncio
import time
from datetime import datetime

from engine import sync_db, db_engine, settings
from logic import scrape_resumes
from models import HHBase


async def main():
    await sync_db(engine=db_engine, db_settings=settings, base=HHBase)
    url = (
        'https://hh.ru/search/resume'
        '?text=водитель+трамвая'
        '&area=2'
        '&isDefaultArea=true'
        '&ored_clusters=true'
        '&order_by=relevance'
        '&search_period=0'
        '&logic=normal'
        '&pos=full_text'
        '&exp_period=all_time'
        '&hhtmFrom=resume_search_catalog'
        '&hhtmFromLabel=resume_search_line'
    )
    await scrape_resumes(link=url)


if __name__ == '__main__':
    try:
        start = time.time()
        print('script started', datetime.now())
        asyncio.run(main())
        print(f"Скрипт завершен за {int(time.time() - start)} секунд")
    except (KeyboardInterrupt, SystemExit):
        print('script stopped')
