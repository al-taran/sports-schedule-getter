# Sports schedule getter

## Overview
A basic Google results scraper that gets your favourite teams' games, filters them by your local timezone restrictions and generates a CSV file that you can import into your calendar(tested on Google calendar but might work with others.)

## Instructions
Install requirements:
```
pip3 install -r requirements.txt
```

In `main.py` edit the `calendar_requests` object to fit your needs. Then run `python3 main.py`, wait until the program exits and if all is well your CSV file will be in `calendar-output` folder called `sports-calendar.csv`.

To import the CSV file into your calendar follow your calendar's instructions, such as these for [Google calendar](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform=Desktop). It's recommended to create a dedicated "sports" calendar so you don't clutter your default one or if you need to re-upload the CSV.

## TODO

### Must do:
- [x] Filter past dates
- [x] Export as CSV
- [x] Investigate NBA not working
- [x] Investigate NHL not working
- [x] Investigate why spans come out empty
- [x] Investigate better way to wait for page load
- [x] Add filters for your teams
- [x] Add filters for your times
- [x] Figure out TZ issues
- [x] Turn request into JSON and implement iterating through different leagues and filtering your teams in one go
- [x] Put all configs into one spot and retrieve as env vars
- [x] Add keywords for common URLs, e.g. nba, elg, etc
- [x] Add requirements.txt
- [ ] If page crashes, save source as a file for debugging purposes
- [ ] Implement a better way of defining params for league calendars
- [ ] Add JSON option for TZ input/output
- [ ] Disable time filtering if kw not present
- [ ] Case insensitive team filter
- [ ] Add timeout and try-again when page doesn't load
- [ ] Investigate why selenium doesn't kill process?
- [ ] Deal with playoff mode and TBD dates
- [ ] Add async calls if need to boost up speed?

### Nice to have:
- [ ] Automatic calendar upload
- [ ] Calendar auto-update
- [ ] Web UI
- [ ] Reminders of highlights for overnight games
- [ ] Add option for derby matchups(two teams playing together that you wouldn't watch by themselves)