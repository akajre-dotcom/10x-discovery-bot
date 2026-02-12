import requests
from bs4 import BeautifulSoup

URL = "PASTE_YOUR_SCREENER_URL"

def get_screen_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    rows = table.find_all("tr")

    stocks = []
    for row in rows[1:6]:
        cols = [col.text.strip() for col in row.find_all("td")]
        stocks.append(cols)

    return stocks
