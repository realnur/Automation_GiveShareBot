import asyncio
from playwright.async_api import async_playwright

class Open_max:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(storage_state="states_max/max.json")
        self.page = await self.context.new_page()

    async def goto_to_url(self, url):
        await self.page.goto(url, timeout=15000)
        await self.page.locator("//a[@class='button button--link button--big svelte-1ykbbcv']").click(timeout=5000)
        await self.page.locator("//button[@aria-label='Проверить подписку']").last.click(timeout=5000)
        await self.page.wait_for_timeout(15000)
        await self.page.locator("//button[@aria-label='Закрыть']").click(timeout=5000)
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
