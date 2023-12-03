from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import json
from pathlib import Path
import random
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def init(user_data: Path):
    ublock_path = '/home/feliks/Work/Python/Scweet_PyCharm/uBlock'

    user_info = {}
    proxy = ''
    cookies = {}

    with user_data.open('r') as file:
        data = json.loads(file.read())
        user_info['username'] = data['username']
        user_info['password'] = data['password']
        user_info['email'] = data['email']
        cookies = data['cookies']
        proxy = data['proxy']

    proxy = ''

    options = Options()

    if proxy != '':
        options.add_argument("--proxy-server=socks5://" + proxy)


    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("load-extension=" + ublock_path)

    driver = webdriver.Chrome(options=options)

    sleep(4) #Wait for uBlock to load properly

    # Navigate to Twitter
    driver.get("https://www.twitter.com")

    # Load cookies from file
    for cookie in cookies:
        if 'twitter.com' in cookie['domain']:
            # Map sameSite values
            if cookie.get('sameSite') in ['no_restriction', 'unspecified']:
                cookie['sameSite'] = 'None'
            elif cookie.get('sameSite') == 'lax':
                cookie['sameSite'] = 'Lax'
            else:
                # Set a default value or handle error
                cookie['sameSite'] = 'None'

            # Remove fields that are not recognized by Selenium
            cookie.pop('expirationDate', None)
            cookie.pop('storeId', None)
            cookie.pop('hostOnly', None)
            cookie.pop('session', None)

            # Add the cookie to the browser
            driver.add_cookie(cookie)

    driver.refresh()

    counter = 5

    while driver.current_url != "https://twitter.com/home" and counter > 0:
        driver.implicitly_wait(1)

        counter -= 1

        if counter == 0 or "https://twitter.com/i/flow/login" in driver.current_url:
            if 'https://twitter.com/i/flow/login' not in driver.current_url:
                driver.get('https://twitter.com/i/flow/login')

            log_in(driver, user_info)
            if driver.current_url != "https://twitter.com/home":
                print("Login failed")
                exit(1)
            break

    #TODO: Add error handling when login is not done properly

    return driver


def log_in(driver, user_data, timeout=20, wait=4):

    email_xpath = '//input[@autocomplete="username"]'
    password_xpath = '//input[@autocomplete="current-password"]'
    username_xpath = '//input[@data-testid="ocfEnterTextTextInput"]'

    sleep(random.uniform(wait, wait + 1))

    # enter email
    email_el = driver.find_element(By.XPATH, email_xpath)
    sleep(random.uniform(wait, wait + 1))
    email_el.send_keys(user_data['email'])
    sleep(random.uniform(wait, wait + 1))
    email_el.send_keys(Keys.RETURN)
    sleep(random.uniform(wait, wait + 1))
    # in case twitter spotted unusual login activity : enter your username
    if check_exists_by_xpath(username_xpath, driver):
        username_el = driver.find_element(By.XPATH, username_xpath)
        sleep(random.uniform(wait, wait + 1))
        username_el.send_keys(user_data['username'])
        sleep(random.uniform(wait, wait + 1))
        username_el.send_keys(Keys.RETURN)
        sleep(random.uniform(wait, wait + 1))
    # enter password
    password_el = driver.find_element(By.XPATH, password_xpath)
    password_el.send_keys(user_data['password'])
    sleep(random.uniform(wait, wait + 1))
    password_el.send_keys(Keys.RETURN)
    sleep(random.uniform(wait, wait + 1))


def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
