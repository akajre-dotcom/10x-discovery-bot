import requests
import pandas as pd
from bs4 import BeautifulSoup

SCREENS = {
    "Growth": "https://www.screener.in/screens/3490938/growth-leaders-stable-accelerators/",
    "Acceleration": "https://www.screener.in/screens/3490944/acceleration-plays-23x-candidates/",
    "Moonshot": "https://www.screener.in/screens/3490945/moonshots-1015-allocation/"
}

def fetch_screen(screen_name, base_url):
    all_data = []
    page = 1

    while True:
        url = f"{base_url}?page={page}"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")

        if table is None:
            break

        rows = table.find_all("tr")[1:]
        if not rows:
            break

        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if len(cols) > 5:
                all_data.append({
                    "Name": cols[0],
                    "SalesGrowth": extract_number(cols[2]),
                    "ProfitGrowth": extract_number(cols[3]),
                    "ROCE": extract_number(cols[4]),
                    "Bucket": screen_name
                    "MarketCap": extract_number(cols[1]),
                })

        page += 1

    return pd.DataFrame(all_data)


def extract_number(value):
    try:
        return float(value.replace('%','').replace(',',''))
    except:
        return 0


def get_all_data():
    dfs = []
    for name, url in SCREENS.items():
        df = fetch_screen(name, url)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined
