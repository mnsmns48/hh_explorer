import asyncio

from playwright.async_api import async_playwright

from browser import run_browser


async def scrape_resumes(link):
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(link)
        print('here')
        await asyncio.sleep(10)