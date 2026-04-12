from playwright.sync_api import sync_playwright

def save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://web.max.ru/")
        input("После входа нажмите Enter в консоли для сохранения сессии...")
        for i in range(1, 10):
            context.storage_state(path=f"states_max/max{i}.json")
        print("Сессия сохранена в max.json")
        browser.close()

if __name__ == "__main__":
    save_session()
