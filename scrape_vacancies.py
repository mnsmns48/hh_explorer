import asyncio
import json
import re
from datetime import datetime

from aiohttp import ClientSession

from config import ua
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


async def logic_vacancies(aio_session: ClientSession, text: str, area: int):
    SCHEDULES = ['fullDay', 'shift', 'flexible', 'remote', 'flyInFlyOut']
    EXPERIENCE = ['noExperience', 'between1And3', 'between3And6', 'moreThan6']
    async with db_engine.scoped_session() as db_session:
        area_name = await get_area_title(session=db_session, id_=area)
    SEARCH_LINE = (f'?text={text}'
                   f'&area={area}'
                   f'&per_page=100')
    jobs_count = int()
    for SCHEDULE in SCHEDULES:
        for EXP in EXPERIENCE:
            data = await get_data(aio_session=aio_session, url=f'{API_URL}'
                                                               f'{SEARCH_LINE}'
                                                               f'&schedule={SCHEDULE}'
                                                               f'&experience={EXP}')
            logger.debug(f"{text} {area_name} {SCHEDULE}__{EXP}// vacancies: {data['found']} pages: {data['pages']}")
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


async def process_vac_list(job_list: list):
    result = list()
    for job in job_list:
        result.append(
            {
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
        )
    async with db_engine.scoped_session() as db_session:
        await write_data(session=db_session, table=Vacancies, data=result)


async def job_text_filing(aio_session: ClientSession):
    async with db_engine.scoped_session() as db_session:
        job_url_list = await get_joblist_without_text(session=db_session)
        logger.debug(f"Start collecting texts from {len(job_url_list)} vacancies\n\n")
        for url in job_url_list:
            job_id = url.rsplit('/', 1)[-1]
            job = await get_data(aio_session=aio_session, url=f"{API_URL}/{job_id}")
            text = re.sub(r'<[^<>]*>', '', job['description'])
            result = {'skills': [n['name'] for n in job['key_skills']], 'text': text}
            await asyncio.sleep(0.4)
            await update_data(session=db_session,
                              table=Vacancies,
                              data=result,
                              column=Vacancies.url,
                              value=url)
