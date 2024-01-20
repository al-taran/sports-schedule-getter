import requests
from bs4 import BeautifulSoup

from selenium import webdriver

ELG_URL = "https://www.google.com/search?hl=en&q=euroleague%20schedule#sie=lg;/g/11kk5tfhf5;3;/m/0b740cl;mt;fp;1;;;"
NBA_URL = "https://www.google.com/search?hl=en&q=nba%20schedule#sie=lg;/g/11snv1vp6v;3;/m/05jvx;mt;fp;1;;;"

driver = webdriver.Firefox()

driver.get("https://www.google.com/404error")
driver.add_cookie({"name": "CONSENT", "value": "YES+cb.20240114-08-p0.cs+FX+111"})
driver.get(ELG_URL)
page_html = driver.page_source




"""
# URL = "https://www.google.com/search?hl=en&q=euroleague%20schedule"
URL = "https://www.google.com/search?q=euroleague+schedule&amp;sca_esv=599926585&amp;hl=en&amp;gbv=1&amp;sei=CAqrZd-ZBqnWhbIP5daG4Ag"
cookies = {"CONSENT": "YES+cb.20240114-08-p0.cs+FX+111"}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
}
page = requests.get(URL, cookies=cookies, headers=headers)
print(page.url)
"""

soup = BeautifulSoup(page_html, "html.parser")
trs = soup.find_all(attrs={'data-start-time': True})

for tr in trs:
    print(tr['data-start-time'])
    tds = tr.find_all("td")
    print(tds[13].find("span").decode_contents())
    print(tds[16].find("span").decode_contents())

#for td in tds[13:]:
#    print(td.prettify())
