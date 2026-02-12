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

TOPIC_MEMORY_FILE = "last_topics.txt"


def get_market_headlines():
    headlines = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            headlines.append(entry.title)

    return headlines


def pick_structural_theme(headlines):
    sampled = random.sample(headlines, min(5, len(headlines)))

    prompt = f"""
    Based on these current market headlines:

    {sampled}

    Identify ONE structural investing theme (not short-term news).
    Example: Capital cycle in defence, Renewable supply chain, EV battery economics, etc.

    Return only the theme title.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_deep_learning(theme):

    prompt = f"""
    Topic: {theme}

    Generate a deep structural investing lesson.

    Structure strictly:

    Title:
    1. First Principle
    2. Industry Mechanics
    3. Capital Intensity & Unit Economics
    4. Where Moat Forms
    5. Failure Mode
    6. Investor Edge
    7. Mental Model Summary

    Keep concise but deep.
    Avoid repetition of generic advice.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():

    headlines = get_market_headlines()
    theme = pick_structural_theme(headlines)

    content = generate_deep_learning(theme)

    subject = f"100X Daily — {theme}"

    send_email(content, subject)


if __name__ == "__main__":
    main()
