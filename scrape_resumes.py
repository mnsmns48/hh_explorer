import asyncio
import json
import re
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from browser import run_browser
from config import SCHEDULES, GENDERS, EXPERIENCE
from crud import write_data
from engine import db_engine
from logger_config import logger
from models import Resumes


async def scrape_resumes(text: str, area: int):
    SEARCH_LINE = (
        f"https://hh.ru/search/resume?text={text}"
        f"&area={area}"
        f"&isDefaultArea=true"
        f"&exp_period=all_time"
        f"&ored_clusters=true"
        f"&order_by=relevance"
        f"&items_on_page=100"
        f"&search_period=0"
        f"&logic=phrase"
        f"&pos=position"
        f"&search_period=365"
        f"&hhtmFrom=resume_search_result"
        f"&hhtmFromLabel=resume_search_line"
    )
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url='https://hh.ru', wait_until='domcontentloaded')

        with open("cookies.json", "r") as f:
            cookies = json.loads(f.read())
        await context.add_cookies(cookies)
        for SCHEDULE in SCHEDULES.keys():
            for EXP in EXPERIENCE.keys():
                for GENDER in GENDERS.keys():
                    await page.goto(url=f"{SEARCH_LINE}"
                                        f"&schedule={SCHEDULE}"
                                        f"&experience={EXP}"
                                        f"&gender={GENDER}", wait_until="domcontentloaded")
                    # logger.
                    page.set_default_timeout(0)
                    last_pag = await page.locator("//a[@class='bloko-button']").nth(-2).inner_text()
                    count = 1
                    print('pages:', last_pag)
                    async with db_engine.scoped_session() as session:
                        while count != int(last_pag) + 1:
                            if count == 1:
                                pass
                            else:
                                await page.locator("//a[@class='bloko-button']").nth(count - 1).click()
                            html = await page.locator("xpath=//main[@class='resume-serp-content']").inner_html()
                            soup = BeautifulSoup(markup=html, features='lxml')
                            data = await bs4_resumes(soup=soup,
                                                     schedule=SCHEDULES.get(SCHEDULE),
                                                     experience=EXPERIENCE.get(EXP),
                                                     gender=GENDERS.get(GENDER))
                            # await write_data(session=session, table=Resumes, data=data)
                            # print('page:', count, 'added')
                            count += 1


async def bs4_resumes(soup: BeautifulSoup, **kwargs) -> list:
    result = list()
    resumes_list = soup.find_all('div', {'data-qa': 'resume-serp__resume'})
    for res in resumes_list:
        title = res.find('a', {'data-qa': re.compile(r'serp-item__title')})
        print(title.span.text)
        experience = res.find('div', {'data-qa': 'resume-serp__resume-excpirience-sum'})
        age = res.find('span', {'data-qa': 'resume-serp__resume-age'})
        salary = age.find_next('div', {'class': ['bloko-text', 'bloko-text_strong']}) if age else None
        status = res.find('div', {'class': re.compile(' tag_job-search-status--')})
        prev_employment = res.find('div', {'data-qa': 'resume-serp_resume-item-content'})
        result.append(
            # {
            #     'title': title.span.text,
            #     'age_line': age.text.strip() if age else None,
            #     'url': f"https://hh.ru{title.get('href').split('?query=')[0]}",
            #     'experience': excpirience.text.strip() if excpirience else None,
            #     'salary': salary.text.strip() if salary and salary.text.strip() != 'Опыт работы' else None,
            #     'status': status.text.strip() if status else None,
            #     'prev_employment_place': prev_employment.text.strip() if prev_employment else None
            # },
            {
                'scrape_date': datetime.now().date(),
                'schedule': kwargs.get('schedule'),
                'experience': kwargs.get('experience'),
                'gender': kwargs.get('gender'),
                'job_title': title.span.text,
                'url': f"https://hh.ru{title.get('href').split('?query=')[0]}",
                'salary_from': salary.text.strip() if salary and salary.text.strip() != 'Опыт работы' else None,
                'salary_to': salary.text.strip() if salary and salary.text.strip() != 'Опыт работы' else None,
                'currency': salary.text[-1] if salary and salary.text[-1] != 'Опыт работы' else None,
                # 'experience_number': None,
            }
        )
    for line in result:
        for k, v in line.items():
            print(f"{k}: {v}")
    await asyncio.sleep(3)
    return result
