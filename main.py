from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

IS_HEADLESS = True

ELG_URL = "https://www.google.com/search?hl=en&q=euroleague%20schedule#sie=lg;/g/11kk5tfhf5;3;/m/0b740cl;mt;fp;1;;;"
NBA_URL = "https://www.google.com/search?hl=en&q=nba%20schedule#sie=lg;/g/11snv1vp6v;3;/m/05jvx;mt;fp;1;;;"


def scroll_down(driver):
    """A method for scrolling the page."""
    els = driver.find_elements(By.CLASS_NAME, 'GVj7ae')
    # Get num of elements
    ll = len(els)
    print("ll", ll)
    while True:
        print("scrolling")
        # Scroll down to the bottom.
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("arguments[0].scrollIntoView();", els[-1])
        # Wait to load the page.
        time.sleep(5)
        # See if new els are present
        els = driver.find_elements(By.CLASS_NAME, 'GVj7ae')
        nl = len(els)
        print("nl", nl)

        if ll == nl:
            break
        ll = nl

opts = Options()
opts.headless = IS_HEADLESS
driver = webdriver.Firefox(options=opts)
driver.get("https://www.google.com/404error")
driver.add_cookie({"name": "CONSENT", "value": "YES+cb.20240114-08-p0.cs+FX+111"})
driver.get(ELG_URL)
time.sleep(5)
scroll_down(driver)
page_html = driver.page_source
driver.quit()


soup = BeautifulSoup(page_html, "html.parser")
trs = soup.find_all(attrs={'data-start-time': True})

games = {}
trs_counter = 0
for tr in trs:
    trs_counter += 1
    game_time = tr['data-start-time']
    tds = tr.find_all("td")
    team_one = tds[13].find("span").decode_contents()
    team_two = tds[16].find("span").decode_contents()
    teams = [team_one, team_two]
    teams.sort()

    team_hash = game_time + teams[0] + teams[1]

    if team_hash not in games:
        games[team_hash] = {'game_time': game_time, 'team_home': team_one, 'team_away': team_two}
    else:
        # The games that are shown when you first load the search
        print("dupe found:", team_hash)

for key in list(games.keys()):
    print(key)
print("trs:", trs_counter, "games:", len(games))
