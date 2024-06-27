import asyncio
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from browser import run_browser
from crud import write_data
from engine import db_engine
from models import Resumes


async def bs4_resumes(soup: BeautifulSoup) -> list:
    result = list()
    resumes_list = soup.find_all('div', {'data-qa': 'resume-serp__resume'})
    count = 1
    for res in resumes_list:
        title = res.find('a', {'data-qa': re.compile(r'serp-item__title')})
        print(count, title.span.text)
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
                'title': title.span.text,
                'url': f"https://hh.ru{title.get('href').split('?query=')[0]}",
                'experience': experience.text.strip() if experience else None,
                'schedule': '',
                'gender': '',
                'education': '',
                'salary': salary.text.strip() if salary and salary.text.strip() != 'Опыт работы' else None,
                'age': '',
                'experience_number': '',
                'status': '',
                'relevance_date': '',
                'prev_employment_place': '',
                'prev_employment_period': '',
                'prev_employment_job': '',
                'skills': '',
                'city': '',
                'business_trip_ready': '',
                'languages': '',
                'university': ''
            }
        )
        count += 1
    return result


async def scrape_resumes(text: str, area: int):
    url = (
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
        f"&hhtmFrom=resume_search_result"
        f"&hhtmFromLabel=resume_search_line"
    )
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")
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
                data = await bs4_resumes(soup=soup)
                await write_data(session=session, table=Resumes, data=data)
                print('page:', count, 'added')
                count += 1
