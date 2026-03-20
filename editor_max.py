
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    context = p.chromium.launch_persistent_context("user_max_data",headless=False)
    page = context.new_page()
    page.goto("https://web.max.ru/")
    input("Войдите и нажмите Enter в консоли...")
    context.close()

