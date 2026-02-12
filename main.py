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
- Must be a specific sector (e.g., Solar manufacturing, Defence exports, EV battery supply chain, Railway capex, Specialty chemicals, SaaS exports).
- Avoid generic themes like "market volatility" or "global uncertainty".
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

Write like a portfolio manager thinking in capital allocation math.

No industry overview.
No definitions.
No generic explanation.

Think in equations and capital flows.

Answer through reasoning:

- Where does free cash flow inflect?
- What operating margin threshold changes equity returns?
- What capital intensity assumption drives ROCE?
- What valuation multiple compression/expansion changes asymmetry?
- What funding environment shift alters survival probability?

Structure strictly:

Title:

1. Capital Deployed vs Capital Returned (cash flow logic)
2. Unit Economics Thresholds That Change Equity Outcomes
3. Capital Cycle Funding Conditions (easy vs tight money)
4. Operating Leverage Inflection Point
5. ROCE / FCF Expansion Pathway
6. How Capital Flood Destroys Returns
7. What Precise Metrics Must Improve For 5–10x
8. Early Warning Indicators of Thesis Breakdown

Be precise. Analytical. Think like allocator, not operator.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_weekly_thesis():

    prompt = """
Generate an institutional-grade sector thesis for India.

Structure:

Title:

1. Why Capital Is Moving Here
2. Supply-Demand Imbalance
3. Capital Cycle Stage
4. ROCE Trajectory Logic
5. Margin Expansion / Compression Risk
6. Capital Flood Risk
7. Monitoring Variables
8. What Would Break the Thesis

Dense. Analytical. No generic macro commentary.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_monthly_regime():

    prompt = """
Generate a Capital Market Regime Review for India.

Focus on:

- Liquidity cycle
- Risk appetite shift
- Sector capital rotation
- Valuation compression vs expansion
- Where capital is withdrawing
- Where capital is concentrating

Write like institutional strategy memo.
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
- Margin Direction
- ROCE Trend
- Capital Inflow Risk
- Asymmetry Potential (Low/Medium/High)
- Brief reasoning

Concise but analytical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_case_study():

    prompt = """
Provide a deep historical 100x stock case study.

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
Generate an institutional note on Position Sizing.

Include:

- Risk of ruin
- Concentration vs diversification math
- Asymmetric payoff sizing
- Volatility tolerance vs conviction
- Capital preservation logic
- Behavioral traps in sizing

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

    # Quarterly Heatmap
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

    # Sunday Thesis
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
