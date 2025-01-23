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