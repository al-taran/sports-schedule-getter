from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import datetime
import dateutil.parser
import pytz
import helpers

load_dotenv()

IS_HEADLESS = True if os.getenv("IS_HEADLESS", None) == "True" else False

ELG_URL = os.getenv("ELG_URL", None)
NBA_URL = os.getenv("NBA_URL", None)
KHL_URL = os.getenv("KHL_URL", None)
NHL_URL = os.getenv("NHL_URL", None)

tz_env = os.getenv("LOCAL_TZ", "Europe/London")
LOCAL_TZ = pytz.timezone("Europe/London")
UTC_TZ = pytz.timezone("UTC")

opts = Options()
if IS_HEADLESS:
    opts.add_argument("--headless=new")
driver = webdriver.Chrome(options=opts)

calendar_requests = {
    "requests": [
        {
            "url": NBA_URL, # URL of your google schedule
            "includeTeams": ['Mavericks', 'Nuggets'], # Optional, if included only get games with these teams
            "excludeTeams": [], # Optional, if included doesn't get games with these teams(but is overriden by `includeTeams`)
            "gameTimeFloor": {'hour': 6, 'minute': 0}, # After what local time are games included
            "gameTimeCeiling": {'hour': 23, 'minute': 59} # Before what local time are games included
        },
        {
            "url": ELG_URL, # URL of your google schedule
            "includeTeams": ['Žalgiris'], # Optional, if included only get games with these teams
            "gameTimeFloor": {'hour': 6, 'minute': 0}, # After what local time are games included
            "gameTimeCeiling": {'hour': 23, 'minute': 59} # Before what local time are games included

        },
        {
            "url": KHL_URL, # URL of your google schedule
            "includeTeams": ['CSKA', 'Torpedo', 'Traktor'], # Optional, if included only get games with these teams
            "gameTimeFloor": {'hour': 6, 'minute': 0}, # After what local time are games included
            "gameTimeCeiling": {'hour': 23, 'minute': 59} # Before what local time are games included

       },
       {
           "url": NHL_URL, # URL of your google schedule
           "includeTeams": ['Capitals', 'Lightning'], # Optional, if included only get games with these teams
           "excludeTeams": [], # Optional, if included doesn't get games with these teams(but is overriden by `includeTeams`)
           "gameTimeFloor": {'hour': 6, 'minute': 0}, # After what local time are games included
           "gameTimeCeiling": {'hour': 23, 'minute': 59} # Before what local time are games included
       }
    ]
}

cal_file = open("./calendar-output/sports-calendar.csv", "w")
cal_file.write("Subject, Start Date, Start Time, End Date, End Time\n")

helpers.decline_cookies(driver)

for request in calendar_requests["requests"]:
    CALENDAR_URL = request["url"]
    INCLUDE_TEAMS = request["includeTeams"] if "includeTeams" in request else []
    EXCLUDE_TEAMS = request["excludeTeams"] if "excludeTeams" in request else []
    GAME_AFTER = request["gameTimeFloor"]
    GAME_BEFORE = request["gameTimeCeiling"]
    page_html = helpers.get_results(driver, CALENDAR_URL)

    soup = BeautifulSoup(page_html, "html.parser")
    trs = soup.select("td.liveresults-sports-immersive__match-tile div[data-start-time]")

    # Get time in ISO 8601
    now_time = datetime.datetime.utcnow().isoformat()

    games = {}
    trs_counter = 0
    for tr in trs:
        is_filtered = False # Don't filter by default
        if len(INCLUDE_TEAMS):
            is_filtered = True # Filter if included teams present

        trs_counter += 1
        game_time = tr['data-start-time']

        # Time filtering
        if game_time < now_time:
            continue

        parsed_date = dateutil.parser.isoparse(game_time)

        time_filter_floor = LOCAL_TZ.localize(datetime.datetime(\
            year=parsed_date.year, month=parsed_date.month, day=parsed_date.day, \
            hour=GAME_AFTER['hour'], minute=GAME_AFTER['minute'], \
            second=0)).astimezone(UTC_TZ)

        time_filter_ceiling = LOCAL_TZ.localize(datetime.datetime(\
            year=parsed_date.year,month=parsed_date.month, day=parsed_date.day, \
            hour=GAME_BEFORE['hour'], minute=GAME_BEFORE['minute'], \
            second=0)).astimezone(UTC_TZ)

        if time_filter_floor > parsed_date or parsed_date > time_filter_ceiling:
            print("Game filtered out by time:", parsed_date)
            continue

        # Process the scrape results
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

        for team in teams:
            if team in INCLUDE_TEAMS:
                is_filtered = False
                break
            elif team in EXCLUDE_TEAMS:
                is_filtered = True


        if is_filtered: # Game got filtered out
            continue

        teams.sort()

        team_hash = game_time + teams[0] + teams[1]

        local_parsed_date = parsed_date.astimezone(LOCAL_TZ)

        if team_hash not in games:
            games[team_hash] = {'game_time': game_time, 'team_home': team_one, 'team_away': team_two}
            subject = team_one + " vs " + team_two
            start_date = f"{local_parsed_date.month}/{local_parsed_date.day}/{local_parsed_date.year}"
            start_time = f"{local_parsed_date.hour:02}:{local_parsed_date.minute:02}"
            end_date = f"{local_parsed_date.month}/{local_parsed_date.day}/{local_parsed_date.year}"
            end_time = f"{(local_parsed_date.hour + 1):02}:{local_parsed_date.minute:02}"
            result_str = f"{subject}, {start_date}, {start_time}, {end_date}, {end_time}\n"
            cal_file.write(result_str)
        else:
            # The games that are shown when you first load the search
            print("dupe found:", team_hash)



    for key in list(games.keys()):
        print(key)
    print("trs:", trs_counter, "games:", len(games))


driver.quit()
cal_file.close()
