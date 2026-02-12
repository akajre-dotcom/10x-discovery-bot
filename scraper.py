import requests
import pandas as pd
from bs4 import BeautifulSoup

SCREENS = {
    "Growth": "https://www.screener.in/screens/3490938/growth-leaders-stable-accelerators/",
    "Acceleration": "https://www.screener.in/screens/3490944/acceleration-plays-23x-candidates/",
    "Moonshot": "https://www.screener.in/screens/3490945/moonshots-1015-allocation/"
}

def extract_number(value):
    try:
        return float(
            value.replace('%','')
                 .replace(',','')
                 .replace('Cr.','')
                 .strip()
        )
    except:
        return 0.0


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

        headers_row = [th.text.strip() for th in table.find("thead").find_all("th")]
        rows = table.find("tbody").find_all("tr")

        if not rows:
            break

        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            row_dict = dict(zip(headers_row, cols))

            all_data.append({
                "Name": row_dict.get("Name", ""),
                "MarketCap": extract_number(row_dict.get("Mar Cap Rs.Cr.", "0")),
                "SalesGrowth": extract_number(row_dict.get("Sales growth %", "0")),
                "ProfitGrowth": extract_number(row_dict.get("Profit growth %", "0")),
                "ROCE": extract_number(row_dict.get("ROCE %", "0")),
                "Debt": extract_number(row_dict.get("Debt / Eq", "0")),
                "OneYearReturn": extract_number(row_dict.get("1Yr return %", "0")),
                "Bucket": screen_name
            })

        page += 1

    return pd.DataFrame(all_data)


def get_all_data():
    dfs = []
    for name, url in SCREENS.items():
        df = fetch_screen(name, url)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.drop_duplicates(subset="Name")

    return combined
