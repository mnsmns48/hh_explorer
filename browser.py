from playwright.async_api import Playwright, Browser


async def run_browser(playwright: Playwright) -> Browser:
    browser = await playwright.chromium.launch(headless=True)
    return browser
