import os
import feedparser
import logging
from openai import OpenAI
from emailer import send_email

# Set up logging for GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Expanded Brands & Trends
# ----------------------------
BRANDS_INDIA = ["Titan", "Tanishq", "CaratLane", "Mia", "Zoya", "Kalyan Jewellers", "Malabar Gold", "PNG Jewellers", "Senco", "Joyalukkas", "BlueStone", "Giva", "Melorra", "Kisna"]
BRANDS_GLOBAL = ["Cartier", "Tiffany & Co.", "Bvlgari", "Van Cleef & Arpels", "Pandora", "Swarovski", "Harry Winston", "Chopard", "De Beers", "Messika"]
ALL_BRANDS = BRANDS_INDIA + BRANDS_GLOBAL

# ----------------------------
# Merchandiser's Keyword Filter
# ----------------------------
LAUNCH_KEYWORDS = [
    "launch", "unveils", "introduces", "collection", "campaign", "ad campaign", 
    "ambassador", "face of the brand", "store launch", "flagship", "expansion", 
    "lab-grown", "LGD", "bridal", "festive", "Gudi Padwa", "Akshaya Tritiya", 
    "karigari", "craftsmanship", "new range", "limited edition"
]

# ----------------------------
# Professional Industry Feeds
# ----------------------------
BASE_FEEDS = [
    "https://www.indianjeweller.in/rss/news",
    "https://www.retailjewellerindia.com/feed/",
    "https://www.professionaljeweller.com/feed/",
    "https://nationaljeweler.com/rss",
    "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "https://www.moneycontrol.com/rss/business.xml"
]

# ----------------------------
# Memory Management (FIXED: Added back the missing functions)
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
def generate_google_news_feeds():
    feeds = []
    special_queries = ["jewelry+ad+campaign+india", "jewellery+retail+expansion+india", "new+jewellery+store+opening"]
    for brand in ALL_BRANDS:
        feeds.append(f"https://news.google.com/rss/search?q={brand.replace(' ', '+')}+jewellery+campaign+OR+launch")
    for q in special_queries:
        feeds.append(f"https://news.google.com/rss/search?q={q}")
    return feeds

def fetch_all_articles():
    feeds = BASE_FEEDS + generate_google_news_feeds()
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
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
        mentions_brand = any(b.lower() in combined for b in ALL_BRANDS)
        is_launch = is_launch_related(combined)
        if mentions_brand and is_launch:
            filtered.append(a)
    return list({v['link']:v for v in filtered}.values())

# ----------------------------
# GPT: Merchandiser's Intelligence Brief
# ----------------------------
def extract_launch_intel(articles):
    if not articles:
        return "No new merchandising momentum or campaigns detected today."

    articles_text = "\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nLink: {a['link']}\n" for a in articles])

    prompt = f"""
    You are an elite Chief Merchandising Officer and Sourcing Expert in the global jewelry sector.
    Review the news and curate a high-level "Merchandiser’s Morning Brief".

    Structure exactly like this:
    
    ### 🌐 Macro Momentum
    [Summarize today's dominant industry shift in 2 sentences. e.g., 'Heavy focus on regional festive campaigns and Tier-2 retail expansions.']

    ### 💎 Product & Craft Intelligence
    * **[Brand Name] - [Collection Name]**
      * **Design Craft:** [Detail the techniques/materials used. Focus on stones, metal purity, and design language.]
      * **Merchandising Angle:** [Analyze the target audience and strategic positioning.] [Source](ACTUAL_LINK)

    ### 🚀 Campaigns & Retail Footprint
    * **[Brand Name]:** [Summarize new campaigns, ambassadors, or store openings.] **Strategic Impact:** [How does this shift market share?] [Source](ACTUAL_LINK)

    Rules:
    - NEVER use raw URLs. Always use [Source](link).
    - Use the ACTUAL links provided.
    - Omit sections if no relevant data is found.

    Articles to analyze:
    {articles_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Merchandising Officer delivering analytical briefings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return f"Error connecting to AI: {e}"

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

    subject = "💎 Merchandiser’s Morning Brief: Global & Indian Jewellery Trends"
    
    try:
        send_email(report, subject)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()
