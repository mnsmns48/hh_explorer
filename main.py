import asyncio
import time
from datetime import datetime

from logic import scrape_resumes


async def main():
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
