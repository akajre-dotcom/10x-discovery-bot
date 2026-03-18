import os
import feedparser
import logging
from openai import OpenAI
from emailer import send_email

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Expanded Brands & Trends
# ----------------------------
BRANDS_INDIA = ["Titan", "Tanishq", "CaratLane", "Mia", "Zoya", "Kalyan Jewellers", "Malabar Gold", "PNG Jewellers", "Senco", "Joyalukkas", "BlueStone", "Giva", "Melorra"]
BRANDS_GLOBAL = ["Cartier", "Tiffany & Co.", "Bvlgari", "Van Cleef & Arpels", "Pandora", "Swarovski", "De Beers", "Messika"]
ALL_BRANDS = BRANDS_INDIA + BRANDS_GLOBAL

# ----------------------------
# Aggressive Sourcing Keywords
# ----------------------------
LAUNCH_KEYWORDS = [
    "launch", "unveils", "collection", "campaign", "ambassador", "face of the brand",
    "store launch", "flagship", "expansion", "lab-grown", "LGD", "bridal", "festive",
    "Gudi Padwa", "Akshaya Tritiya", "design language", "karigari", "craftsmanship"
]

# ----------------------------
# Professional Industry Feeds (CRITICAL ADDITIONS)
# ----------------------------
BASE_FEEDS = [
    "https://www.indianjeweller.in/rss/news", # Essential for Indian retail trade
    "https://www.retailjewellerindia.com/feed/", # Strategic retail moves
    "https://www.professionaljeweller.com/feed/", # Global industry trends
    "https://nationaljeweler.com/rss", # Diamond and gemstone market intel
    "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms"
]

def generate_google_news_feeds():
    feeds = []
    # Targeted queries for campaigns and store openings
    special_queries = ["jewelry+ad+campaign+india", "jewellery+retail+expansion+india", "new+jewellery+store+opening"]
    for brand in ALL_BRANDS:
        feeds.append(f"https://news.google.com/rss/search?q={brand.replace(' ', '+')}+jewellery+campaign+OR+launch")
    for q in special_queries:
        feeds.append(f"https://news.google.com/rss/search?q={q}")
    return feeds

# --- (Memory functions: read_memory/write_memory remain the same) ---

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
        except: continue
    return articles

def filter_articles(articles, seen_links):
    filtered = []
    for a in articles:
        if a["link"] in seen_links: continue
        combined = (a["title"] + " " + a["summary"]).lower()
        if any(k in combined for k in LAUNCH_KEYWORDS) or any(b.lower() in combined for b in ALL_BRANDS):
            filtered.append(a)
    return list({v['link']:v for v in filtered}.values())

# ----------------------------
# The Merchandiser's Prompt
# ----------------------------
def extract_launch_intel(articles):
    if not articles: return "No new momentum detected today."
    articles_text = "\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nLink: {a['link']}" for a in articles])

    prompt = f"""
    You are a Chief Merchandising Officer. Analyze these jewellery industry updates.
    
    Format the email as a "Merchandiser’s Morning Brief":

    ### 🌐 Macro Momentum
    [Summarize today's dominant industry shift in 2 sentences. e.g., 'A major pivot toward regional festive campaigns (Gudi Padwa) and rapid Tier-2 retail expansion.']

    ### 💎 Product & Craft Intelligence
    * **[Brand] - [Collection/Product]**
      * **Design Craft:** [Detail the technique/materials: e.g., 14kt rose gold, lightweight polki, sculptural minimalism].
      * **Merchandising Angle:** [Why now? Who is the target? Strategic positioning?] [Source](link)

    ### 🚀 Campaigns & Retail Footprint
    * **[Brand]:** [Detail new ad campaigns, celebrity ambassadors, or store openings]. **Strategic Impact:** [How does this affect market share or brand perception?] [Source](link)

    Articles:
    {articles_text}
    """


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Chief Merchandising Officer delivering a dense, professional daily briefing to a sourcing and design team."},
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
