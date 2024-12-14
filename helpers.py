"""
Helper functions for selenium.
"""
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv

load_dotenv()

WEB_DRIVER_TIMEOUT = int(os.getenv("WEB_DRIVER_TIMEOUT", 20))
WAIT_TIME = int(os.getenv("WAIT_TIME", 4))


def get_async_ei(driver):
    """
    Getter for 'async-ei' attribute, used to tell if we have scrolled all the way to the bottom of the calendar.
    """
    time.sleep(2)
    return driver.find_element(By.CSS_SELECTOR, '#liveresults-sports-immersive__updatable-league-matches.yf'
                               ).get_attribute('async-ei')


def is_fs_displayed(driver):
    """
    Check if fullpage attribute is present, used to see if page has loaded
    """
    is_fullscreen_loaded = driver.find_element(By.ID, 'liveresults-sports-immersive__league-fullpage').is_displayed()
    print("is_fullscreen_loaded?", is_fullscreen_loaded)
    return is_fullscreen_loaded


def is_cookies_clickable(driver):
    """
    Check if you can click away the cookies modal.
    """
    is_cookies_clickable_result = driver.find_element(By.ID, 'W0wltc').is_displayed()
    print("is_cookies_displayed", is_cookies_clickable_result)
    return is_cookies_clickable_result


def click_cookies(driver):
    """
    Click away the cookies.
    """
    driver.find_element(By.ID, 'W0wltc').click()


def is_page_loaded(driver, async_ei_before):
    """
    Check if the page has loaded.
    """
    async_ei_after = get_async_ei(driver)
    print(f"before:{async_ei_before}, after:{async_ei_after}")
    return async_ei_before != async_ei_after


def decline_cookies(driver):
    """
    Wrapper func to check for cookies and click them away.
    """
    wait = WebDriverWait(driver, timeout=WEB_DRIVER_TIMEOUT)
    driver.get("http://google.com/search")
    wait.until(lambda _: is_cookies_clickable(driver))
    click_cookies(driver)


def get_results(driver, calendar_url):
    """
    Scrape and return calendar page contents.
    """
    wait = WebDriverWait(driver, timeout=WEB_DRIVER_TIMEOUT)
    driver.get(calendar_url)
    wait.until(lambda _: is_fs_displayed(driver))
    scroll_down(driver)
    page_html = driver.page_source
    return page_html


def scroll_down(driver):
    """A method for scrolling the page."""
    wait = WebDriverWait(driver, timeout=WEB_DRIVER_TIMEOUT)

    els = driver.find_elements(By.CLASS_NAME, 'OcbAbf')  # Get container of grid of game panels
    async_ei_before = get_async_ei(driver)
    # Get num of elements
    last_len = len(els)
    print("last_len", last_len)
    is_match_detected = False
    while True:
        print("scrolling")
        # Scroll down to the bottom.
        driver.execute_script("arguments[0].scrollIntoView();", els[-1])
        if not is_match_detected:
            wait.until(lambda _: is_page_loaded(driver, async_ei_before))
        else:
            time.sleep(WAIT_TIME)
        async_ei_after = get_async_ei(driver)
        async_ei_before = async_ei_after
        els = driver.find_elements(By.CLASS_NAME, 'OcbAbf')
        new_len = len(els)
        print("new_len", new_len)

        if last_len == new_len:
            # Match was detected before so assume that we got all the games we could get
            if is_match_detected:
                break
            # Match wasn't detected before so give it one more run to make sure it's not still loading
            is_match_detected = True
            continue
        else:
            last_len = new_len
            is_match_detected = False  # Page was loading so we can reset the value
