import json
from pathlib import Path
from playwright.async_api import Browser, Page, TimeoutError
import re


async def init_context(browser: Browser, user_file: Path):
    with user_file.open('r') as file:
        user_data = json.loads(file.read())

    cookies = []

    # Get cookies
    for cookie in user_data['cookies']:
        if cookie.get('sameSite') in ['no_restriction', 'unspecified']:
            cookie['sameSite'] = 'None'
        elif cookie.get('sameSite') == 'lax':
            cookie['sameSite'] = 'Lax'
        else:
            cookie['sameSite'] = 'None'

        cookie.pop('expirationDate', None)
        cookie.pop('storeId', None)
        cookie.pop('hostOnly', None)
        cookie.pop('session', None)

        cookies.append(cookie)

    context = await browser.new_context(
        # proxy={"server": "socks5://" + user_data['proxy']} if user_data['proxy'] != '' else None,
        user_agent=user_data['user_agent']
    )

    if cookies is not None:
        await context.add_cookies(cookies)

    page = await context.new_page()

    await page.goto("https://twitter.com/home")

    # Handling different redirect cases
    if page.url == "https://twitter.com/home":
        return context
    elif page.url == "https://twitter.com":
        await page.goto("https://twitter.com/i/flow/login")
        await page.wait_for_url("https://twitter.com/i/flow/login", timeout=5000)

    if "https://twitter.com/i/flow/login" not in page.url:
        print("Login redirect failed")
        exit(1)

    await log_in(page, user_data)

    return context


async def log_in(page: Page, user_data, attempt=3):
    """
    Logs in to twitter
    :param attempt: Number of login attempts
    :param page: Playwright page instance
    :param user_data: User data for login
    :return: None
    """
    if attempt == 0:
        print("Login failed")
        exit(1)

    email_input = page.get_by_label("Phone, email, or username")

    try:
        await email_input.wait_for(timeout=5000)
    except TimeoutError:
        await page.reload()
        await log_in(page, user_data, attempt - 1)
        return

    await email_input.click()
    await email_input.fill(user_data['email'])
    await email_input.press("Enter")

    username_input = page.locator("input[data-testid='ocfEnterTextTextInput']")
    await username_input.wait_for(timeout=1000)

    if await username_input.is_visible():
        await username_input.fill(user_data['username'])
        await username_input.press("Enter")

    password_input = page.get_by_label("Password", exact=True)
    await password_input.wait_for(timeout=1000)

    await password_input.fill(user_data['password'])
    await password_input.press("Enter")

    await page.wait_for_url("https://twitter.com/home", timeout=5000)

    if page.url != "https://twitter.com/home":
        print("Login failed")
        exit(1)
