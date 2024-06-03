import asyncio

from playwright.async_api import async_playwright

from browser import run_browser


async def scrape_resumes(link):
    async with async_playwright() as playwright:
        browser = await run_browser(playwright)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(link, wait_until="domcontentloaded")
        page.set_default_timeout(0)
        last_pag = await page.locator("//a[@class='bloko-button']").nth(-2).inner_text()
        count = 1
        while count != int(last_pag) + 1:
            if count == 1:
                pass
            else:
                await page.goto(f'{link}&page={count - 1}, wait_until="domcontentloaded"')
            await asyncio.sleep(3)
            print('page', count)
            count += 1
