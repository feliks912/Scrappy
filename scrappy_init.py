import json
from pathlib import Path
from playwright.sync_api import Browser, Page, TimeoutError


def init_context(browser: Browser, user_file: Path):
    ublock_path = '/home/feliks/Work/Python/Scweet_PyCharm/uBlock'

    user_data = {}

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

    context = browser.new_context(
        bypass_csp=True,
        # proxy={"server": "socks5://" + user_data['proxy']} if user_data['proxy'] != '' else None,
        user_agent=user_data['user_agent']
    )

    context.add_cookies(cookies)

    page = context.new_page()

    page.goto("https://twitter.com/home")

    # This can redirect us to twitter.com, twitter.com/i/flow/login or twitter.com/home.
    # We need to handle all of these cases

    if page.url == "https://twitter.com/home":
        return context
    elif page.url == "https://twitter.com":
        page.goto("https://twitter.com/i/flow/login")
        page.wait_for_url("https://twitter.com/i/flow/login", timeout=5000)

    if "https://twitter.com/i/flow/login" not in page.url:
        print("Login redirect failed")
        exit(1)

    log_in(page, user_data)

    return context


def log_in(page: Page, user_data, attempt=3):
    """
    Logs in to twitter
    #TODO: Check each element's existence
    :param attempt:
    :param page:
    :param user_data:
    :return:
    """
    if attempt == 0:
        print("Login failed")
        exit(1)

    email_input = page.get_by_label("Phone, email, or username")

    try:
        email_input.wait_for(timeout=5000)
    except TimeoutError:
        page.reload()
        log_in(page, user_data, attempt - 1)
        return

    email_input.click()
    email_input.fill(user_data['email'])
    email_input.press("Enter")

    username_input = page.locator("input[data-testid='ocfEnterTextTextInput']")
    username_input.wait_for(timeout=1000)

    if username_input.is_visible():
        username_input.fill(user_data['username'])
        username_input.press("Enter")

    password_input = page.get_by_label("Password", exact=True)
    password_input.wait_for(timeout=1000)

    password_input.fill(user_data['password'])
    password_input.press("Enter")

    page.wait_for_url("https://twitter.com/home", timeout=5000)

    if page.url != "https://twitter.com/home":
        print("Login failed")
        exit(1)


