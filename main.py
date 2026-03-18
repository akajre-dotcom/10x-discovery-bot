import os
import feedparser
import logging
from openai import OpenAI
from emailer import send_email

# Set up logging for GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Brands & Trends (Expanded for Global + India)
# ----------------------------

BRANDS_INDIA = [
    "Titan", "Tanishq", "CaratLane", "Kalyan Jewellers", 
    "Malabar Gold", "PNG Jewellers", "PC Jeweller", 
    "Kisna", "Bluestone", "Giva", "Senco", "Joyalukkas"
]

BRANDS_GLOBAL = [
    "Cartier", "Tiffany & Co.", "Bvlgari", "Van Cleef & Arpels", 
    "Pandora", "Swarovski", "Harry Winston", "Chopard", "De Beers"
]

ALL_BRANDS = BRANDS_INDIA + BRANDS_GLOBAL

# ----------------------------
# Launch & Trend Keywords
# ----------------------------

LAUNCH_KEYWORDS = [
    "launch", "introduces", "unveils", "new collection",
    "new range", "campaign", "ad campaign", "drops", "release",
    "festive collection", "bridal collection", "high jewelry",
    "haute joaillerie", "lab-grown", "sustainable jewelry"
]

# ----------------------------
# RSS Sources (Upgraded with Global Industry News)
# ----------------------------

BASE_FEEDS = [
    # Indian Business
    "https://www.moneycontrol.com/rss/business.xml",
    "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    # Global Jewellery & Luxury
    "https://www.professionaljeweller.com/feed/",
    "https://nationaljeweler.com/rss",
]

def generate_google_news_feeds():
    feeds = []
    # Search for broader trend keywords to catch non-brand specific launches
    trend_queries = ["lab+grown+diamond+launch", "high+jewelry+collection+unveiled"]
    
    for brand in ALL_BRANDS:
        query = brand.replace(" ", "+") + "+jewellery+launch"
        feeds.append(f"https://news.google.com/rss/search?q={query}")
        
    for query in trend_queries:
        feeds.append(f"https://news.google.com/rss/search?q={query}")
        
    return feeds

# ----------------------------
# Memory Management
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
# Fetch & Filter Logic
# ----------------------------

def fetch_all_articles():
    feeds = BASE_FEEDS + generate_google_news_feeds()
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]: # Limit to top 10 per feed to speed up processing
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": getattr(entry, "summary", "")
                })
        except Exception as e:
            logging.error(f"Failed to parse feed {url}: {e}")

    return articles

def is_launch_related(text):
    text = text.lower()
    return any(keyword in text for keyword in LAUNCH_KEYWORDS)

def filter_articles(articles, seen_links):
    filtered = []
    for a in articles:
        if a["link"] in seen_links:
            continue

        combined = (a["title"] + " " + a["summary"]).lower()

        # Check if it mentions a brand OR a major industry keyword, AND is a launch
        mentions_brand = any(b.lower() in combined for b in ALL_BRANDS)
        is_launch = is_launch_related(combined)
        
        if mentions_brand and is_launch:
            filtered.append(a)

    # Deduplicate by link before returning
    return list({v['link']:v for v in filtered}.values())

# ----------------------------
# GPT: Extract Launch Intelligence
# ----------------------------

def extract_launch_intel(articles):
    if not articles:
        return "No new jewellery product launches or major trends detected today."

    # Convert articles to a clean string format to save tokens
    articles_text = "\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nLink: {a['link']}\n" for a in articles])

    prompt = f"""
    You are an elite Market Intelligence Analyst for the global jewellery industry.
    Review the following news articles and extract actual product launches, new collections, or major design trends. 
    
    Categorize them into 'Indian Market' and 'Global Market'.
    
    For each valid launch, provide:
    - **Brand**: 
    - **Collection/Product**:
    - **Category**: (e.g., Bridal, High Jewelry, Lab-Grown, Daily Wear)
    - **Market Intel**: What makes this launch unique? (e.g., pricing, target audience, materials, sustainability)
    - **Link**: 

    Ignore generic financial news, stock updates, or executive changes unless accompanied by a product launch.

    Articles to analyze:
    {articles_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise, highly analytical market intelligence bot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return f"Error connecting to AI for analysis: {e}"

# ----------------------------
# Main Execution
# ----------------------------

def main():
    logging.info("Starting Jewellery Market Intel Fetcher...")
    
    seen_links = read_memory()
    articles = fetch_all_articles()
    
    launch_articles = filter_articles(articles, seen_links)
    logging.info(f"Found {len(launch_articles)} new potential launch articles.")

    report = extract_launch_intel(launch_articles)
    
    if launch_articles:
        new_links = [a["link"] for a in launch_articles]
        write_memory(new_links)

    subject = "💎 Global & Indian Jewellery Launch Tracker — Daily Intel"
    
    try:
        send_email(report, subject)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()
