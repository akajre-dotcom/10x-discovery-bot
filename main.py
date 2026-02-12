import os
import random
import feedparser
from datetime import datetime
from openai import OpenAI
from emailer import send_email

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RSS_FEEDS = [
    "https://www.moneycontrol.com/rss/business.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.livemint.com/rss/markets"
]

MEMORY_FILE = "topic_memory.txt"


def get_market_headlines():
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            headlines.append(entry.title)
    return headlines


def read_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return f.read().splitlines()
    except:
        return []


def write_memory(theme):
    with open(MEMORY_FILE, "a") as f:
        f.write(theme + "\n")


def pick_theme(headlines, memory):
    sampled = random.sample(headlines, min(5, len(headlines)))

    prompt = f"""
    Based on these current Indian market headlines:

    {sampled}

    Identify ONE structural capital cycle or industry transformation theme.
    Avoid repeating recently covered themes:
    {memory[-15:]}

    Return only the theme title.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_advanced_lesson(theme):

    prompt = f"""
    Topic: {theme}

    You are training a professional long-term capital allocator.

    Generate an ADVANCED institutional-grade structural investing note.

    Structure strictly:

    Title:

    1. Structural Context (macro + capital flow positioning)
    2. Industry Value Chain Breakdown
    3. Unit Economics & Operating Leverage
    4. Capital Cycle Positioning (early/mid/late)
    5. Competitive Advantage Formation
    6. Margin Expansion / Compression Drivers
    7. Failure & Regime Shift Scenarios
    8. Investor Edge Framework (what differentiates alpha here)
    9. What Must Be True For 5–10x Outcome

    Keep dense, analytical, non-generic.
    Avoid motivational language.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():

    headlines = get_market_headlines()
    memory = read_memory()

    theme = pick_theme(headlines, memory)
    lesson = generate_advanced_lesson(theme)

    write_memory(theme)

    subject = f"100X Advanced — {theme}"

    send_email(lesson, subject)


if __name__ == "__main__":
    main()
