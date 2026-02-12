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

DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]


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
    Based on these current market headlines:

    {sampled}

    Identify ONE structural investing theme (not short-term news).
    Avoid these recently covered themes:
    {memory[-10:]}

    Return only the theme title.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_daily_lesson(theme, difficulty):

    prompt = f"""
    Topic: {theme}
    Difficulty Level: {difficulty}

    Generate a structural investing lesson.

    Structure strictly:

    Title:
    1. First Principle
    2. Industry Mechanics
    3. Capital Intensity & Unit Economics
    4. Where Moat Forms
    5. Failure Mode
    6. Investor Edge
    7. Mental Model Summary

    Depth should match difficulty level.
    Keep concise but insightful.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_weekly_thesis():

    prompt = """
    Generate a deep institutional-grade structural sector thesis for India.

    Structure strictly:

    Title:
    1. Why Now
    2. Demand Drivers
    3. Policy Impact
    4. Capital Cycle Stage
    5. Margin Drivers
    6. Competitive Landscape
    7. Where Value May Accrue
    8. What Would Break the Thesis
    9. Monitoring Checklist

    Provide advanced level depth.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():

    today = datetime.today()
    weekday = today.weekday()

    if weekday == 6:  # Sunday
        content = generate_weekly_thesis()
        subject = "100X Weekly — Institutional Sector Thesis"
        send_email(content, subject)
        return

    headlines = get_market_headlines()
    memory = read_memory()

    theme = pick_theme(headlines, memory)

    difficulty = DIFFICULTY_LEVELS[weekday % 3]

    lesson = generate_daily_lesson(theme, difficulty)

    write_memory(theme)

    subject = f"100X Daily ({difficulty}) — {theme}"

    send_email(lesson, subject)


if __name__ == "__main__":
    main()
