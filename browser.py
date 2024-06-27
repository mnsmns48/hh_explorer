from playwright.async_api import Playwright, Browser

from engine import settings


async def run_browser(playwright: Playwright) -> Browser:
    browser = await playwright.chromium.launch(headless=settings.headless_mode)
    return browser
