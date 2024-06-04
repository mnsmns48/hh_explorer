import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from browser import run_browser
from crud import write_data
from engine import db_engine
from models import Resume


async def bs4_resumes(soup: BeautifulSoup) -> list:
    result = list()
    resumes_list = soup.find_all('div', {'data-qa': 'resume-serp__resume'})
    for res in resumes_list:
        title = res.find('a', {'data-qa': 'serp-item__title'})
        excpirience = res.find('div', {'data-qa': 'resume-serp__resume-excpirience-sum'})
        age = res.find('span', {'data-qa': 'resume-serp__resume-age'})
        salary = age.find_next('div', {'class': ['bloko-text', 'bloko-text_strong']}) if age else None
        status = res.find('div', {'class': re.compile(' tag_job-search-status--')})
        prev_employment = res.find('div', {'data-qa': 'resume-serp_resume-item-content'})
        result.append(
            {
                'title': title.span.text,
                'age': age.text.strip() if age else None,
                'link': f"https://hh.ru{title.get('href').split('?query=')[0]}",
                'excpirience': excpirience.text.strip()if excpirience else None,
                'salary': salary.text.strip() if salary and salary.text.strip() != 'Опыт работы' else None,
                'status': status.text.strip() if status else None,
                'prev_employment': prev_employment.text.strip() if prev_employment else None
            }
        )
    return result


async def scrape_resumes(link):
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(link, wait_until="domcontentloaded")
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
                await write_data(session=session, table=Resume, data=data)
                print('page:', count, 'added')
                count += 1
