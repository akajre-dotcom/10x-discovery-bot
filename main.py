import os
import feedparser
from openai import OpenAI
from emailer import send_email

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Brands (Expanded)
# ----------------------------

BRANDS = [
    "Titan", "Tanishq", "CaratLane",
    "Kalyan Jewellers", "Malabar Gold",
    "PNG Jewellers", "PC Jeweller",
    "Kisna", "Bluestone", "Giva"
]

# ----------------------------
# Launch Keywords (STRICT FILTER)
# ----------------------------

LAUNCH_KEYWORDS = [
    "launch", "introduces", "unveils", "new collection",
    "new range", "campaign", "ad campaign",
    "festive collection", "bridal collection",
    "diamond collection", "gold collection",
    "limited edition", "drops", "release"
]

# ----------------------------
# RSS Sources
# ----------------------------

BASE_FEEDS = [
    "https://www.moneycontrol.com/rss/business.xml",
    "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "https://www.livemint.com/rss/companies",
]

# ----------------------------
# Google News Feeds (CRITICAL)
# ----------------------------

def generate_google_news_feeds():
    feeds = []
    for brand in BRANDS:
        query = brand.replace(" ", "+") + "+jewellery+launch"
        url = f"https://news.google.com/rss/search?q={query}"
        feeds.append(url)
    return feeds


# ----------------------------
# Memory
# ----------------------------

MEMORY_FILE = "seen_links.txt"

def read_memory():
    if not os.path.exists(MEMORY_FILE):
        return set()
    with open(MEMORY_FILE, "r") as f:
        return set(f.read().splitlines())


def write_memory(links):
    with open(MEMORY_FILE, "a") as f:
        for link in links:
            f.write(link + "\n")


# ----------------------------
# Fetch News
# ----------------------------

def fetch_all_articles():
    feeds = BASE_FEEDS + generate_google_news_feeds()
    articles = []

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries[:20]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, "summary", "")
            })

    return articles


# ----------------------------
# Filter: Brand + Launch Intent
# ----------------------------

def is_launch_related(text):
    text = text.lower()
    return any(keyword in text for keyword in LAUNCH_KEYWORDS)


def filter_articles(articles, seen_links):
    filtered = []

    for a in articles:
        if a["link"] in seen_links:
            continue

        combined = (a["title"] + " " + a["summary"]).lower()

        if any(b.lower() in combined for b in BRANDS) and is_launch_related(combined):
            filtered.append(a)

    return filtered


# ----------------------------
# GPT: Extract Launch Intelligence
# ----------------------------

def extract_launch_intel(articles):

    if not articles:
        return "No jewellery product launches detected today."

    prompt = f"""
You are tracking product launches in the jewellery market.

For each item:
- Identify the PRODUCT or COLLECTION launched
- Brand name
- Type (bridal, diamond, daily wear, premium, etc.)
- What makes it different (design, pricing, positioning)
- Whether it is part of a campaign or seasonal push
- Keep link

Articles:
{articles}

Output format:

Brand:
Launch:
Category:
Details:
Strategic Intent:
Link:

Only include REAL launches or collections.
Ignore generic business news.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Main
# ----------------------------

def main():

    articles = fetch_all_articles()
    seen_links = read_memory()

    launch_articles = filter_articles(articles, seen_links)

    report = extract_launch_intel(launch_articles)

    new_links = [a["link"] for a in launch_articles]
    write_memory(new_links)

    subject = "Jewellery Product Launch Tracker — Daily"
    send_email(report, subject)


if __name__ == "__main__":
    main()
