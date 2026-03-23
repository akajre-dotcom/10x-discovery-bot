import os
import feedparser
import logging
from openai import OpenAI
from emailer import send_email

# Optional markdown import (safe fallback)
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Brands & Trends
# ----------------------------
BRANDS_INDIA = [
    "Titan", "Tanishq", "CaratLane", "Mia", "Zoya",
    "Kalyan Jewellers", "Malabar Gold", "PNG Jewellers",
    "Senco", "Joyalukkas", "BlueStone", "Giva",
    "Melorra", "Kisna"
]

BRANDS_GLOBAL = [
    "Cartier", "Tiffany & Co.", "Bvlgari",
    "Van Cleef & Arpels", "Pandora", "Swarovski",
    "Harry Winston", "Chopard", "De Beers", "Messika"
]

ALL_BRANDS = BRANDS_INDIA + BRANDS_GLOBAL

# ----------------------------
# Keywords
# ----------------------------
LAUNCH_KEYWORDS = [
    "launch", "unveils", "introduces", "collection",
    "campaign", "ambassador", "store launch",
    "flagship", "expansion", "lab-grown", "bridal",
    "festive", "limited edition"
]

# ----------------------------
# RSS Feeds
# ----------------------------
BASE_FEEDS = [
    "https://www.indianjeweller.in/rss/news",
    "https://www.retailjewellerindia.com/feed/",
    "https://www.professionaljeweller.com/feed/",
    "https://nationaljeweler.com/rss"
]

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
    if not links:
        return
    with open(MEMORY_FILE, "a") as f:
        for link in links:
            f.write(link + "\n")

# ----------------------------
# Feed Logic
# ----------------------------
def generate_google_news_feeds():
    feeds = []
    for brand in ALL_BRANDS:
        feeds.append(
            f"https://news.google.com/rss/search?q={brand.replace(' ', '+')}+jewellery+launch"
        )
    return feeds

def fetch_all_articles():
    feeds = BASE_FEEDS + generate_google_news_feeds()
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": getattr(entry, "summary", "")
                })
        except Exception as e:
            logging.error(f"Feed error: {e}")

    return articles

def is_launch_related(text):
    text = text.lower()
    return any(k in text for k in LAUNCH_KEYWORDS)

def filter_articles(articles, seen_links):
    filtered = []

    for a in articles:
        if a["link"] in seen_links:
            continue

        combined = (a["title"] + " " + a["summary"]).lower()

        if any(b.lower() in combined for b in ALL_BRANDS) and is_launch_related(combined):
            filtered.append(a)

    # deduplicate
    return list({a["link"]: a for a in filtered}.values())

# ----------------------------
# GPT Processing
# ----------------------------
def extract_launch_intel(articles):
    if not articles:
        return "No significant jewellery launches today."

    text = "\n".join([
        f"{a['title']} - {a['summary']} ({a['link']})"
        for a in articles
    ])

    prompt = f"""
    Create a concise merchandising intelligence brief.

    Articles:
    {text}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return res.choices[0].message.content

    except Exception as e:
        return f"AI error: {e}"

# ----------------------------
# Main
# ----------------------------
def main():
    logging.info("Starting...")

    seen_links = read_memory()
    articles = fetch_all_articles()

    new_articles = filter_articles(articles, seen_links)

    logging.info(f"New articles: {len(new_articles)}")

    report_md = extract_launch_intel(new_articles)

    if new_articles:
        write_memory([a["link"] for a in new_articles])

    # Markdown → HTML if available
    if MARKDOWN_AVAILABLE:
        report_html = markdown.markdown(report_md)
    else:
        report_html = f"<pre>{report_md}</pre>"

    send_email(report_html, "Jewellery Market Brief")

    logging.info("Done.")

# Entry
if __name__ == "__main__":
    main()
