import asyncio
import json
import re
import time
from datetime import datetime
from tqdm import tqdm
from aiohttp import ClientSession

from config import ua, SCHEDULES, EXPERIENCE
from crud import get_area_title, write_data, get_joblist_without_text, update_data
from engine import db_engine
from logger_config import logger
from models import Vacancies

API_URL = 'https://api.hh.ru/vacancies'


async def get_data(aio_session: ClientSession, url: str) -> json:
    async with aio_session.get(url, headers={'user-agent': ua.random}, allow_redirects=False, timeout=10) as response:
        if response.status == 200:
            result = await response.json()
            return result
        return await response.text()


async def scrape_vacancies(aio_session: ClientSession, text: str, area: int) -> None:
    async with db_engine.scoped_session() as db_session:
        area_name = await get_area_title(session=db_session, id_=area)
    SEARCH_LINE = (f'?text={text}'
                   f'&area={area}'
                   f'&per_page=100')
    jobs_count = int()
    for SCHEDULE in SCHEDULES.keys():
        for EXP in EXPERIENCE.keys():
            data = await get_data(aio_session=aio_session, url=f'{API_URL}'
                                                               f'{SEARCH_LINE}'
                                                               f'&schedule={SCHEDULE}'
                                                               f'&experience={EXP}')
            logger.debug(f"{text} {area_name} {SCHEDULES.get(SCHEDULE)}__{EXPERIENCE.get(EXP)}"
                         f" // vacancies: {data['found']}")
            if data['found'] > 0:
                await process_vac_list(job_list=data['items'])
                jobs_count += len(data['items'])
            if data['pages'] > 1:
                page = 1
                while page != data['pages']:
                    next_page_data = await get_data(aio_session=aio_session,
                                                    url=f'{API_URL}'
                                                        f'{SEARCH_LINE}'
                                                        f'&schedule={SCHEDULE}&page={page}')
                    if isinstance(next_page_data, dict):
                        await process_vac_list(job_list=next_page_data['items'])
                        page += 1
                        jobs_count += len(next_page_data['items'])
                    else:
                        logger.debug('Error scraping', next_page_data)
                await asyncio.sleep(0.4)
    logger.debug(f"--------------------------TOTAL: {text} {area_name} {jobs_count} vacancies")
    await job_text_filing(aio_session=aio_session)


async def process_vac_list(job_list: list) -> None:
    result = list()
    for job in job_list:
        data = {
            'scrape_date': datetime.now().date(),
            'schedule': job['schedule']['name'],
            'experience': job['experience']['name'],
            'job_title': job['name'],
            'url': job['alternate_url'],
            'salary_from': job.get('salary')['from'] if job.get('salary') else None,
            'salary_to': job.get('salary')['to'] if job.get('salary') else None,
            'currency': job.get('salary')['currency'] if job.get('salary') else None,
            'company_title': job['employer']['name'],
            'publication_date': datetime.strptime(job['published_at'], '%Y-%m-%dT%H:%M:%S%z'),
        }
        if data.get('salary_from') and data.get('salary_to') is None:
            data['salary_to'] = data.get('salary_from')
        result.append(data)
    async with db_engine.scoped_session() as db_session:
        await write_data(session=db_session, table=Vacancies, data=result)


async def job_text_filing(aio_session: ClientSession) -> None:
    async with db_engine.scoped_session() as db_session:
        job_url_list = await get_joblist_without_text(session=db_session)
        logger.debug(f"Start collecting texts from {len(job_url_list)} vacancies")
        for i, url in zip(tqdm(job_url_list), job_url_list):
            job_id = url.rsplit('/', 1)[-1]
            job = await get_data(aio_session=aio_session, url=f"{API_URL}/{job_id}")
            text = re.sub(r'<[^<>]*>', '', job['description'])
            result = {'skills': [n['name'] for n in job['key_skills']], 'text': text}
            await update_data(session=db_session,
                              table=Vacancies,
                              data=result,
                              column=Vacancies.url,
                              value=url)
            await asyncio.sleep(0.4)

