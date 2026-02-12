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
- Must be a specific sector (examples: Solar manufacturing, Defence exports, EV battery supply chain, Railway capex, Specialty chemicals, SaaS exports, Data center infrastructure, Capital goods cycle).
- Avoid generic themes like "market volatility", "global uncertainty", or "economic slowdown".
- Must involve capital allocation, supply-demand imbalance, pricing cycle, or structural transformation.
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

Write like a capital allocator evaluating equity compounding potential.

Avoid descriptive industry commentary.
Focus on equity return mechanics.

Force yourself to analyze:

- How capital (float or fixed assets) generates incremental return
- What combined ratio / pricing threshold changes ROE structurally
- What capital impairment triggers a hard pricing cycle
- How book value compounds over 5–10 years
- Where downside is protected (balance sheet logic)
- Where capital exits could create pricing power
- What shifts could expand valuation multiples

Structure strictly:

Title:

1. Capital Base & Return Engine (how equity actually compounds)
2. Pricing Power Threshold That Changes ROE
3. Soft vs Hard Market Cycle Transition Logic
4. Book Value Compounding Pathway
5. Where Equity IRR Inflects
6. How Capital Flood Creates Long Downcycles
7. Convexity Setup: Why 5–10x Is Possible (or Not)
8. Leading Indicators of Cycle Turn

Be specific. Think in terms of equity IRR, not industry growth.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_weekly_thesis():

    prompt = """
Generate an institutional-grade Indian sector thesis.

Focus on:

- Why capital is flowing into this sector
- Supply-demand imbalance
- Capital cycle stage
- ROCE trajectory potential
- Margin expansion vs compression risk
- Capital flood risk
- Monitoring variables
- What would structurally break the thesis

Write like a portfolio manager memo.
Avoid generic macro commentary.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_monthly_regime():

    prompt = """
Generate a Capital Market Regime Review for India.

Cover:

- Liquidity cycle direction
- Risk appetite shift
- Sector capital rotation
- Valuation compression vs expansion
- Where capital is withdrawing
- Where capital is concentrating
- Early regime shift indicators

Institutional tone. Analytical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_sector_heatmap():

    prompt = """
Generate a Quarterly Indian Equity Sector Heatmap.

For each major sector:
- Capital Cycle Stage (Early / Mid / Late)
- Margin Direction
- ROCE Trend
- Capital Inflow Risk
- Asymmetry Potential (Low / Medium / High)
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

1. Initial Industry Structure
2. Structural Tailwind
3. Capital Allocation Decisions
4. ROCE Inflection
5. Margin Expansion Phase
6. Severe Drawdown Periods
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
Generate an institutional note on Position Sizing & Capital Allocation.

Include:

- Risk of ruin
- Concentration vs diversification trade-off
- Asymmetric payoff sizing logic
- Volatility tolerance vs conviction
- Capital preservation principles
- Behavioral traps in sizing decisions

Practical. Analytical. No generic advice.
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

    # Quarterly Heatmap (Jan, Apr, Jul, Oct 1st)
    if day == 1 and month in [1, 4, 7, 10]:
        content = generate_sector_heatmap()
        subject = "100X Quarterly — Sector Heatmap"
        send_email(content, subject)
        return

    # Monthly Regime Review (1st of every month)
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

    # Quarterly Case Study (15th of quarter months)
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
