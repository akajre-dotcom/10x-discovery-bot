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
    Based on these Indian market headlines:

    {sampled}

    Identify ONE structural capital cycle or transformation theme.
    Avoid repeating recently covered themes:
    {memory[-20:]}

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

    Generate an ADVANCED institutional-grade structural investing note.

    Structure:

    1. Structural Context
    2. Industry Value Chain
    3. Unit Economics & Operating Leverage
    4. Capital Cycle Positioning
    5. Competitive Advantage Formation
    6. Margin Drivers
    7. Failure & Regime Shift Scenarios
    8. Investor Edge Framework
    9. Conditions for 5–10x Outcome
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_weekly_thesis():
    prompt = """
    Generate a deep institutional sector thesis for India.

    Structure:

    1. Why Now
    2. Demand Drivers
    3. Policy Impact
    4. Capital Cycle Stage
    5. Competitive Structure
    6. Margin Outlook
    7. Risks
    8. Monitoring Checklist
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_monthly_regime():
    prompt = """
    Generate a Capital Market Regime Review for India.

    Include:
    - Liquidity Conditions
    - Sector Rotation
    - Risk Appetite
    - Valuation Compression/Expansion
    - Early Signals of Capital Shift
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_sector_heatmap():
    prompt = """
    Generate a Quarterly Sector Heatmap for Indian equities.

    For each major sector:
    - Capital Cycle Stage (Early/Mid/Late)
    - Margin Trend (Expanding/Flat/Contracting)
    - Risk Level (Low/Moderate/High)
    - Asymmetry Potential (Low/Medium/High)
    - Brief 2-line explanation
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_case_study():
    prompt = """
    Provide a deep historical 100x case study (Indian or Global).

    Structure:
    - Company Background
    - Structural Tailwind
    - Capital Allocation Decisions
    - Inflection Point
    - Margin Expansion Path
    - Key Risk Periods
    - Lessons for Identifying Future 100x
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_position_sizing():
    prompt = """
    Generate an advanced lesson on Position Sizing Psychology.

    Include:
    - Kelly Criterion intuition
    - Asymmetry vs conviction
    - Risk of ruin
    - Concentration vs diversification
    - Handling volatility without overreaction
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():

    today = datetime.today()
    weekday = today.weekday()
    day = today.day
    month = today.month

    # Quarterly Sector Heatmap (Jan/Apr/Jul/Oct on 1st)
    if day == 1 and month in [1, 4, 7, 10]:
        content = generate_sector_heatmap()
        subject = "100X Quarterly — Sector Heatmap"
        send_email(content, subject)
        return

    # Monthly Capital Regime
    if day == 1:
        content = generate_monthly_regime()
        subject = "100X Monthly — Capital Regime Review"
        send_email(content, subject)
        return

    # Sunday Weekly Thesis
    if weekday == 6:
        content = generate_weekly_thesis()
        subject = "100X Weekly — Institutional Sector Thesis"
        send_email(content, subject)
        return

    # Friday Position Sizing
    if weekday == 4:
        content = generate_position_sizing()
        subject = "100X — Position Sizing & Psychology"
        send_email(content, subject)
        return

    # Mid-quarter Case Study (15th of quarter months)
    if day == 15 and month in [1, 4, 7, 10]:
        content = generate_case_study()
        subject = "100X Case Study — Historical 100x Dissection"
        send_email(content, subject)
        return

    # Default Daily Advanced
    headlines = get_market_headlines()
    memory = read_memory()
    theme = pick_theme(headlines, memory)
    lesson = generate_advanced_lesson(theme)
    write_memory(theme)
    subject = f"100X Advanced — {theme}"
    send_email(lesson, subject)


if __name__ == "__main__":
    main()
