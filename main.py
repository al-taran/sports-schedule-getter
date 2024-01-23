from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import datetime
import dateutil.parser

IS_HEADLESS = True
WAIT_TIME = 1 # in seconds

ELG_URL = "https://www.google.com/search?hl=en&q=euroleague%20schedule#sie=lg;/g/11kk5tfhf5;3;/m/0b740cl;mt;fp;1;;;"
NBA_URL = "https://www.google.com/search?hl=en&q=nba%20schedule#sie=lg;/g/11snv1vp6v;3;/m/05jvx;mt;fp;1;;;"

cal_file = open("./calendar-output/elg-file.csv", "w")
cal_file.write("Subject, Start Date, Start Time, End Date, End Time\n")


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
        time.sleep(WAIT_TIME)
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
driver.get(NBA_URL)
time.sleep(WAIT_TIME)
scroll_down(driver)
page_html = driver.page_source
driver.quit()


soup = BeautifulSoup(page_html, "html.parser")
trs = soup.find_all(attrs={'data-start-time': True})

# Get time in ISO 8601
now_time = datetime.datetime.now().isoformat()

games = {}
trs_counter = 0
for tr in trs:
    trs_counter += 1
    game_time = tr['data-start-time']
    if game_time < now_time:
        print("Past game:", game_time)
        continue
    tds = tr.find_all("td")

    spans = []
    for td in tds:
        span = td.select("tr.L5Kkcd span")
        if span:
            spans.append(span[0].decode_contents())

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
