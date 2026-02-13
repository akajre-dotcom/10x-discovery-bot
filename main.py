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


# ----------------------------
# Utility
# ----------------------------

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


# ----------------------------
# Theme Selector
# ----------------------------

def pick_theme(headlines, memory):
    sampled = random.sample(headlines, min(5, len(headlines)))

    prompt = f"""
From these Indian market headlines:

{sampled}

Choose ONE very specific sub-segment.

Examples:
- Indian life insurance EV growth
- Defence electronics exports
- Solar module manufacturing (not renewables broadly)
- IT services margin cycle
- Railway EPC order cycle
- AI data center capex in India

Rules:
- No broad sectors.
- Must relate to capital cycle or structural return shift.
- Avoid recently used:
{memory[-20:]}

Return only the sub-segment title.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


# ----------------------------
# Core Allocator Engine
# ----------------------------

def generate_allocator_note(theme):

    prompt = f"""
Sub-segment: {theme}

Write like a concentrated equity fund manager deciding whether to allocate 20% of portfolio capital here.

No textbook language.
No general sector overview.
No symbolic math.

Force specificity and judgment.

Structure:

TITLE

1. What Is The Real Return Engine?
   - How does equity compound here?
   - What variable actually drives sustained ROE?

2. Where Is This In The Capital Cycle?
   - Early / Mid / Late?
   - What evidence supports this?
   - Is capital entering or exiting?

3. What Is The Market Pricing In?
   - Typical valuation multiple in India
   - What growth rate seems implied
   - Is that assumption aggressive or conservative?

4. 5-Year IRR Scenarios
   - Base case
   - Bull case
   - Bear case
   - What breaks in each?

5. Where Capital Gets Destroyed
   - Specific mechanism
   - Historical pattern if relevant

6. 3-Company Comparison (India)
   Name three listed companies.
   For each:
   - Capital efficiency quality (High / Medium / Low)
   - Valuation risk (High / Medium / Low)
   - Asymmetry (High / Medium / Low)
   - One-line allocator view

7. Decision Pressure
   - Would you allocate 20% today? Yes or No.
   - What must you believe to do so?
   - What would make you walk away?

Tone:
Direct.
Judgmental.
Allocator mindset.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Weekly Memo
# ----------------------------

def generate_weekly_memo():

    prompt = """
Write a weekly Indian equity allocator memo.

Include:

1. One sector in early capital cycle
2. One sector in late cycle
3. One valuation extreme
4. One mispricing risk
5. One area worth deep research

Be decisive.
No macro fluff.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Monthly Regime
# ----------------------------

def generate_monthly_regime():

    prompt = """
Write a capital market regime assessment for India.

Cover:

- Liquidity direction
- Risk appetite
- Where capital is concentrating
- Where capital is exiting
- What style is likely to outperform next 6 months

Allocator tone.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Position Sizing Discipline
# ----------------------------

def generate_position_sizing():

    prompt = """
Write a note on concentrated portfolio construction.

Assume 8–12 stock portfolio.

Cover:

1. Core compounders vs cyclicals vs moonshots
2. When 20–30% allocation is justified
3. Handling 50% drawdowns in structural winners
4. When to average down vs exit
5. Why most investors under-size 5–10x outcomes
6. Biggest psychological mistake in concentration

No stop-loss discussion.
No trading language.
Allocator discipline only.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Execution Logic
# ----------------------------

def main():

    today = datetime.today()
    weekday = today.weekday()
    day = today.day

    # Monthly
    if day == 1:
        content = generate_monthly_regime()
        subject = "100X — Capital Regime Review"
        send_email(content, subject)
        return

    # Sunday weekly
    if weekday == 6:
        content = generate_weekly_memo()
        subject = "100X — Weekly Allocator Memo"
        send_email(content, subject)
        return

    # Friday sizing
    if weekday == 4:
        content = generate_position_sizing()
        subject = "100X — Portfolio Construction Discipline"
        send_email(content, subject)
        return

    # Daily allocator deep dive
    headlines = get_market_headlines()
    memory = read_memory()
    theme = pick_theme(headlines, memory)
    note = generate_allocator_note(theme)
    write_memory(theme)
    subject = f"100X — {theme}"
    send_email(note, subject)


if __name__ == "__main__":
    main()
