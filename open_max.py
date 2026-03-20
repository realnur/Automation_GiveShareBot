import asyncio
from playwright.async_api import async_playwright

class Open_max:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch_persistent_context("user_max_data",headless=False)
        self.page = await self.browser.new_page()

    async def goto_to_url(self, url):
        await self.page.goto(url)
        await self.page.locator("//a[@class='button button--link button--big svelte-1ykbbcv']").click()
        await self.page.wait_for_timeout(5000)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()