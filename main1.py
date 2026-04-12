number_thread = 1
import os
import asyncio
import re
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout, Error as PlaywrightError
from open_max import Open_max
# --- читаем links.txt ---
def read_links():
    links = []
    with open("links.txt", "r", encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if not s:
                continue
            links.append(s)
    return links


# --- читаем sessions.txt ---
def read_sessions():
    sessions = []
    with open(f"sessions{number_thread}.txt", "r", encoding="utf-8") as f:
        for ln in f:
            s = ln.strip()
            if not s:
                continue
            sessions.append(s)
    return sessions


async def open_telegram_web(page, session_name, browser):
    await page.goto("https://web.telegram.org/a/")
    await asyncio.sleep(15)

    async def check_qr():
        if await page.locator("#auth-qr-form").is_visible():
            print(f"❌ Сессия - {session_name} -> не залогинена (QR)")
            with open(f"qr.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            clean_lines = [" ".join(line.strip().split()) for line in lines if line.strip()]
            with open(f"qr.txt", "w", encoding="utf-8") as f:
                for line in clean_lines:
                    f.write(line + "\n")
            with open(f"qr.txt", "a", encoding="utf-8") as f:
                f.write(session_name + "\n")
            return True
        return False

    if await check_qr():
        return False

    try:
        await page.get_by_role("textbox", name="Search").wait_for(timeout=60000)
        await asyncio.sleep(1)
        await page.get_by_role("textbox", name="Search").first.click(timeout=60000)
        await page.get_by_role("textbox", name="Search").first.fill("forex_signals_upwork_example_bot", timeout=60000)
        await page.locator("(//div[@class='search-section']//div[@class='ListItem chat-item-clickable search-result'])[1]").click(timeout=60000)
    except PlaywrightTimeout:
        if await check_qr():
            return False
        else:
            print(f"❌ Сессия - {session_name} -> ЗАВЕРШЕН ИЗ ЗА НЕИЗВЕСТНЫХ ПРИЧИН")
            return False

    try:
        await page.get_by_role("button", name="Start").first.click(timeout=4000)
    except PlaywrightTimeout:
        pass

    print("✅ Страница загрузилась полностью")
    return True

async def main():
    sessions = read_sessions()
    links = read_links()

    if not sessions:
        print("[ERR] sessions.txt пустой или не найден")
        return
    if not links:
        print("[ERR] links.txt пустой или не найден")
        return
    open_max = Open_max()
    await open_max.init_browser(number_thread)
    async with async_playwright() as p:
        for session_name in sessions:
            aleksei = True
            state_file = f"states/{session_name}.json"
            if not os.path.exists(state_file):
                print(f"[WARN] state-файл не найден для {session_name}: {state_file} — пропускаю")
                continue

            print(f"\n============================")
            print(f"=== СЕССИЯ: {session_name} ===")
            print(f"=== STATE:  {state_file} ===")
            print(f"============================")

            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state=state_file)
            page = await context.new_page()

            if not await open_telegram_web(page, session_name, browser):
                continue

            leshik = 0

            for link in links:
                try:
                    try:
                        await page.get_by_role("button", name="Close").first.click(timeout=2000)
                        await asyncio.sleep(1)
                    except PlaywrightTimeout:
                        pass

                    print(f"\n[{session_name}] Обрабатываю ссылку: {link}")

                    try:
                        await page.get_by_role("textbox", name="Message").first.fill(link, timeout=10000)
                    except (PlaywrightTimeout, PlaywrightError):
                        await page.get_by_role("button", name="Close").first.click(timeout=2000)
                        await asyncio.sleep(1)
                        await page.get_by_role("textbox", name="Message").first.fill(link, timeout=10000)

                    await page.keyboard.press("Enter")
                    await page.keyboard.press("Enter")
                    await page.click(f'a[href="{link}"]', timeout=60000)

                    try:
                        if aleksei == True:
                            await page.get_by_role("button", name="Confirm").first.click(timeout=60000)
                            aleksei = False
                    except PlaywrightTimeout:
                        pass

                    lesha = 0
                    boot = True

                    while boot == True:
                        lesha += 1
                        try:
                            iframe_el = await page.wait_for_selector("iframe")
                            frame = await iframe_el.content_frame()

                            await frame.wait_for_load_state("load")
                            await frame.wait_for_load_state("domcontentloaded")
                            await frame.wait_for_load_state("networkidle")
                            await frame.wait_for_function("document.readyState === 'complete'")
                            await frame.wait_for_function("""() => document.querySelectorAll("div.boxIntro_text").length > 0""")

                            await frame.locator("div.boxIntro_text").wait_for(state="visible", timeout=60000)
                            await asyncio.sleep(4)

                            iframe_el = await page.wait_for_selector("iframe")
                            frame = await iframe_el.content_frame()

                            if await frame.locator("div.boxIntro_title:has-text('Загружаем данные...')").count() > 0:
                                print("АЛЕКСЕЙ если ты это читаеш, сообщи об этом сообщение НУРКАНАТУ, это связыно со разработкой")
                                await asyncio.sleep(15)

                            if await frame.locator("div.boxIntro_title:has-text('Поздравляем победителей!')").count() > 0:
                                print("Срок розыгрыша истек. Пропускаем!")
                                boot = False
                                break

                            elif await frame.locator("div.boxIntro_title:has-text('Вы участвуете в розыгрыше!')").count() > 0:
                                print("Розыгрыш уже активирован. Пропускаем!")
                                boot = False
                                break

                            elif await frame.locator("div.boxIntro_title:has-text('Поздравляем победителя!')").count() > 0:
                                print("Срок розыгрыша истек. Пропускаем!")
                                boot = False
                                break

                            elif await frame.locator("div.boxIntro_title:has-text('Упс! Что-то пошло не так...')").count() > 0:
                                print("Что-то пошло не так...(ссылка подвержен). Пропускаем!")
                                boot = False
                                break

                            elif await frame.locator("div.boxIntro_title:has-text('Определяем победителей')").count() > 0:
                                print("Победителей определяется. Пропускаем!")
                                boot = False
                                break

                            raffle_div = frame.locator("div.boxIntro_text").filter(has_text=re.compile(r"Теперь вы участвуете в розыгрыше"))
                            if await raffle_div.count() > 0:
                                print("Вы уже заранее подписались на каналы и сразу успешно получили билет!")
                                boot = False
                                break

                            copy_btn = frame.locator("button.btn.btn--tt-none").filter(has_text=re.compile(r"Скопировать"))
                            if await copy_btn.count() > 0:
                                print("Требует поделиться со друзьями! Пропускаем!")
                                boot = False
                                break

                        except PlaywrightTimeout:
                            pass

                        try:
                            while True:
                                old_height = await frame.evaluate("document.body.scrollHeight")
                                await frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                await page.wait_for_timeout(200)
                                new_height = await frame.evaluate("document.body.scrollHeight")
                                if new_height == old_height:
                                    break

                            await asyncio.sleep(1)

                            iframe_el = await page.wait_for_selector("iframe")
                            frame = await iframe_el.content_frame()

                            buttons = frame.locator("div.btn.btn--sm:has-text('Подписаться'), div.btn.btn--sm:has-text('Проверить')")
                            count = await buttons.count()

                            if lesha >= 5:
                                boot = False
                                break

                            if count == 0:
                                continue
                            exit_while= False
                            for i in range(count):
                                await asyncio.sleep(1)
                                iframe_el = await page.wait_for_selector("iframe")
                                frame = await iframe_el.content_frame()
                                buttons = frame.locator("div.btn.btn--sm:has-text('Подписаться'), div.btn.btn--sm:has-text('Проверить')")
                                await buttons.nth(i).click(timeout=20000)
                                await asyncio.sleep(3)
                                
                                if len(context.pages) > 1:
                                    print(2)
                                    new_page = context.pages[-1]
                                    print(1)
                                    await open_max.goto_to_url(new_page.url)
                                    print(3)
                                    await new_page.close()
                                    print(4)
                                    await page.bring_to_front()
                                    print(9999)
                                    continue

                                join_buttons = [
                                    ("Join Channel", 15000),
                                    ("Join Group", 1000),
                                    ("APPLY TO JOIN GROUP", 1000),
                                    ("OK", 1000)
                                ]

                                exit_while = False

                                for name, timeout in join_buttons:
                                    try:
                                        await page.get_by_role("button", name=name).first.click(timeout=timeout)

                                        if name == "OK":
                                            print("КАНАЛ ПРИВАТНЫЙ")
                                            boot = False
                                            exit_while = True
                                            break

                                        await asyncio.sleep(2)
                                        break

                                    except (PlaywrightTimeout, PlaywrightError):
                                        continue

                                if exit_while == True:
                                    break

                                await page.locator("#portals").get_by_role("button").nth(1).click(timeout=60000)
                                await asyncio.sleep(2)
                            if exit_while == True:
                                break

                        except PlaywrightTimeout:
                            if lesha >= 5:
                                boot = False
                                break
                            continue

                        except PlaywrightError:
                            if lesha >= 5:
                                boot = False
                                break
                            continue

                        print("Начинаем на подписку каналов!")
                        iframe_el = await page.wait_for_selector("iframe")
                        frame = await iframe_el.content_frame()

                        await frame.locator("button:has-text('Проверить подписку')").first.click(timeout=60000)
                        await asyncio.sleep(5)

                        await page.get_by_role("button", name="Close").first.click(timeout=60000)
                        await asyncio.sleep(0.5)

                        await page.get_by_role("textbox", name="Search").first.click(timeout=60000)
                        await asyncio.sleep(2)

                        await page.get_by_role("textbox", name="Search").first.fill("forex_signals_upwork_example_bot", timeout=60000)
                        await asyncio.sleep(2)

                        await page.get_by_role("button", name="Forex Signals (upwork) Forex Signals (upwork) bot").first.click(timeout=60000)
                        await asyncio.sleep(2)

                        leshik += 1
                        boot = False

                except PlaywrightTimeout:
                    print("Скрипт сломался!")
                    await page.screenshot(path=f"scr_{int(asyncio.get_event_loop().time())}_{session_name}.png")

                except PlaywrightError:
                    print("Скрипт сломался!")
                    await page.screenshot(path=f"scr_{int(asyncio.get_event_loop().time())}_{session_name}.png")

            await browser.close()
    await open_max.close()
    print("\nГотово.")
    await asyncio.sleep(99999)


if __name__ == "__main__":
    asyncio.run(main())
