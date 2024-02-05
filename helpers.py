from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

WEB_DRIVER_TIMEOUT = 10
WAIT_TIME = 1 # in seconds

def get_async_ei(driver):
    return driver.find_element(By.CSS_SELECTOR, '#liveresults-sports-immersive__updatable-league-matches.yf').get_attribute('async-ei')


def is_fs_displayed(driver):
    is_fullscreen_loaded = driver.find_element(By.ID, 'liveresults-sports-immersive__league-fullpage').is_displayed()
    print("is_fullscreen_loaded?", is_fullscreen_loaded)
    return is_fullscreen_loaded


def is_page_loaded(driver, async_ei_before):
    async_ei_after = get_async_ei(driver)
    print(f"before:{async_ei_before}, after:{async_ei_after}")
    return async_ei_before != async_ei_after


def get_results(driver, calendar_url):
    wait = WebDriverWait(driver, timeout=WEB_DRIVER_TIMEOUT)
    
    driver.get(calendar_url)
    wait.until(lambda _: is_fs_displayed(driver))
    scroll_down(driver)
    page_html = driver.page_source
    return page_html


def scroll_down(driver):
    """A method for scrolling the page."""
    wait = WebDriverWait(driver, timeout=WEB_DRIVER_TIMEOUT)

    els = driver.find_elements(By.CLASS_NAME, 'OcbAbf')
    async_ei_before = get_async_ei(driver)
    # Get num of elements
    ll = len(els)
    print("ll", ll)
    is_match_detected = False
    while True:
        print("scrolling")
        # Scroll down to the bottom.
        driver.execute_script("arguments[0].scrollIntoView();", els[-1])
        if not is_match_detected:
            wait.until(lambda _: is_page_loaded(driver, async_ei_before))
        else:
            time.sleep(WAIT_TIME) # Give elements some extra time to get loaded or sometimes it will exit loop prematurely
        async_ei_after = get_async_ei(driver)
        async_ei_before = async_ei_after
        els = driver.find_elements(By.CLASS_NAME, 'OcbAbf')
        nl = len(els)
        print("nl", nl)

        if ll == nl:
            # Match was detected before so assume that we got all the games we could get
            if is_match_detected:
                break
            # Match wasn't detected before so give it one more run to make sure it's not just loading
            else:
                is_match_detected = True
                continue
        else:
            ll = nl
            is_match_detected = False # Page was loading so we can reset the value
