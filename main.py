from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import dateutil.parser
import time

IS_HEADLESS = True
WAIT_TIME = 1 # in seconds

ELG_URL = "https://www.google.com/search?hl=en&q=euroleague%20schedule#sie=lg;/g/11kk5tfhf5;3;/m/0b740cl;mt;fp;1;;;"
NBA_URL = "https://www.google.com/search?hl=en&q=nba%20schedule#sie=lg;/g/11snv1vp6v;3;/m/05jvx;mt;fp;1;;;"
KHL_URL = "https://www.google.com/search?hl=en&q=khl%20schedule#sie=lg;/g/11ssq6w841;7;/m/03ykpkx;mt;fp;1;;;"
NHL_URL = "https://www.google.com/search?hl=en&q=nhl%20schedule#sie=lg;/g/11txxwrx35;7;/m/05gwr;mt;fp;1;;;"

SCHEDULE_URL = NBA_URL

opts = Options()
if IS_HEADLESS:
    opts.add_argument("--headless=new")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, timeout=10)

cal_file = open("./calendar-output/elg-file.csv", "w")
cal_file.write("Subject, Start Date, Start Time, End Date, End Time\n")

def get_async_ei():
    return driver.find_element(By.CSS_SELECTOR, '#liveresults-sports-immersive__updatable-league-matches.yf').get_attribute('async-ei')

def is_fs_displayed():
    is_fullscreen_loaded = driver.find_element(By.ID, 'liveresults-sports-immersive__league-fullpage').is_displayed()
    # print("is_fullscreen_loaded?", is_fullscreen_loaded)
    return is_fullscreen_loaded


def is_page_loaded(async_ei_before):
    async_ei_after = get_async_ei()
    print(f"before:{async_ei_before}, after:{async_ei_after}")
    return async_ei_before != async_ei_after

def scroll_down(driver):
    """A method for scrolling the page."""
    els = driver.find_elements(By.CLASS_NAME, 'OcbAbf')
    async_ei_before = get_async_ei()
    # Get num of elements
    ll = len(els)
    print("ll", ll)
    is_match_detected = False
    while True:
        print("scrolling")
        # Scroll down to the bottom.
        driver.execute_script("arguments[0].scrollIntoView();", els[-1])
        if not is_match_detected:
            wait.until(lambda _: is_page_loaded(async_ei_before))
        else:
            time.sleep(WAIT_TIME) # Give elements some extra time to get loaded or sometimes it will exit loop prematurely
        async_ei_after = get_async_ei()
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


driver.get("https://www.google.com/404error") # Go to a non-existing page to allow to set cookies
driver.add_cookie({"name": "CONSENT", "value": "YES+cb.20240114-08-p0.cs+FX+111"})
driver.get(SCHEDULE_URL)
wait.until(lambda _: is_fs_displayed())
scroll_down(driver)
page_html = driver.page_source
driver.quit()


soup = BeautifulSoup(page_html, "html.parser")
trs = soup.select("td.liveresults-sports-immersive__match-tile div[data-start-time]")

# Get time in ISO 8601
now_time = datetime.datetime.now().isoformat()

games = {}
trs_counter = 0
for tr in trs:
    trs_counter += 1
    game_time = tr['data-start-time']

    # Filter out past games
    if game_time < now_time:
        # print("Past game:", game_time)
        continue

    tds = tr.find_all("td")

    spans = []
    for td in tds:
        span = td.select("tr.L5Kkcd span")
        if span:
            spans.append(span[0].decode_contents())
    if len(spans) != 2:
        print("\n\n\n")
        print(tr.prettify())
        print("Couldn't get teams, see element above.")
        print("\n\n\n")
        continue
    team_one = spans[0]
    team_two = spans[1]
    teams = [team_one, team_two]
    teams.sort()

    team_hash = game_time + teams[0] + teams[1]

    if team_hash not in games:
        games[team_hash] = {'game_time': game_time, 'team_home': team_one, 'team_away': team_two}
        subject = team_one + " vs " + team_two
        parsed_date = dateutil.parser.isoparse(game_time)
        start_date = f"{parsed_date.month}/{parsed_date.day}/{parsed_date.year}"
        start_time = f"{parsed_date.hour:02}:{parsed_date.minute:02}"
        end_date = f"{parsed_date.month}/{parsed_date.day}/{parsed_date.year}"
        end_time = f"{(parsed_date.hour + 1):02}:{parsed_date.minute:02}"
        result_str = f"{subject}, {start_date}, {start_time}, {end_date}, {end_time}\n"
        cal_file.write(result_str)

        
    else:
        # The games that are shown when you first load the search
        print("dupe found:", team_hash)


cal_file.close()

for key in list(games.keys()):
    print(key)
print("trs:", trs_counter, "games:", len(games))
