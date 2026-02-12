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

Identify ONE specific structural industry or capital cycle theme.

Rules:
- Must be tied to a specific sector (examples: Solar manufacturing, Defence exports, EV battery supply chain, Railway capex, Specialty chemicals, SaaS exports, Capital goods cycle).
- Avoid generic themes like "market volatility", "uncertainty", "global economy".
- Must involve capital allocation, supply-demand imbalance, or structural transformation.
- Avoid repeating recently covered themes:
{memory[-20:]}

Return ONLY the theme title.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_advanced_lesson(theme):

    prompt = f"""
Topic: {theme}

Write like a fund manager evaluating capital allocation asymmetry.

Avoid industry description.
Avoid surface-level explanations.

Focus on:

- Supply-demand imbalance in capital
- Pricing power cycles
- Combined ratio / ROCE sensitivity
- Where incremental capital earns > cost of capital
- Where capital floods destroy returns
- Float economics (if financial sector)
- Operating leverage thresholds
- Balance sheet optionality

Structure strictly:

Title:

1. Capital Structure of the Industry
2. Where Returns Are Actually Earned (math logic)
3. Current Capital Cycle Stage (with reasoning)
4. ROCE / ROE Sensitivity Drivers
5. When This Becomes a Hard Pricing Environment
6. Where Capital Gets Destroyed
7. What Structural Shift Could Create 5–10x Equity Outcome
8. Monitoring Variables That Matter (not generic KPIs)

Dense. Analytical. Think in terms of capital, not technology.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_weekly_thesis():
    prompt = """
Generate a deep institutional sector thesis for India.

Write like a portfolio manager memo.

Structure:

Title:

1. Why Now (capital flow + policy + demand)
2. Demand Drivers
3. Capital Cycle Stage
4. Competitive Structure
5. Margin Outlook & ROCE Trajectory
6. Risk of Capital Flood
7. What Would Break the Thesis
8. Monitoring Framework

Analytical. Not generic.
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
- Liquidity conditions
- Risk appetite shift
- Sector capital rotation
- Valuation expansion/compression
- Early signals of capital migration

Write like institutional strategy note.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_sector_heatmap():
    prompt = """
Generate a Quarterly Indian Sector Heatmap.

For each major sector:
- Capital Cycle Stage (Early/Mid/Late)
- Margin Trend (Expanding/Flat/Contracting)
- ROCE Direction
- Capital Inflow Risk
- Asymmetry Potential (Low/Medium/High)
- 2-line reasoning

Concise but analytical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_case_study():
    prompt = """
Provide a deep historical 100x stock case study (India or Global).

Structure:

Title:

1. Starting Industry Structure
2. Structural Tailwind
3. Capital Allocation Decisions
4. ROCE Inflection
5. Margin Expansion Phase
6. Periods of Severe Drawdown
7. Why Most Investors Missed It
8. Lessons for Identifying Future 100x

Analytical. No storytelling fluff.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_position_sizing():
    prompt = """
Generate an advanced institutional note on Position Sizing.

Include:
- Kelly intuition (not formula heavy)
- Risk of ruin
- Concentration vs diversification
- Volatility tolerance vs conviction
- How professionals size asymmetric bets
- Behavioral failure patterns

Analytical. Practical. No generic advice.
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

    # Quarterly Sector Heatmap
    if day == 1 and month in [1, 4, 7, 10]:
        content = generate_sector_heatmap()
        subject = "100X Quarterly — Sector Heatmap"
        send_email(content, subject)
        return

    # Monthly Regime Review
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
        subject = "100X — Position Sizing & Capital Allocation"
        send_email(content, subject)
        return

    # Mid-quarter Case Study
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
