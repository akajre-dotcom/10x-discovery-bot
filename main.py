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


# ---------------------------
# Utility Functions
# ---------------------------

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


# ---------------------------
# Theme Selection
# ---------------------------

def pick_theme(headlines, memory):
    sampled = random.sample(headlines, min(5, len(headlines)))

    prompt = f"""
Based on these Indian market headlines:

{sampled}

Identify ONE specific structural capital cycle theme.

Rules:
- Must be tied to a specific industry (e.g., Solar manufacturing, Life insurance EV growth, Defence exports, AI data center infra, Railway capex, Specialty chemicals).
- Must involve capital allocation, supply-demand imbalance, pricing cycle, or structural transformation.
- Avoid generic macro themes.
- Avoid repeating recently covered themes:
{memory[-20:]}

Return ONLY the theme title.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


# ---------------------------
# Advanced Allocator Lesson
# ---------------------------

def generate_allocator_lesson(theme):

    prompt = f"""
Topic: {theme}

You are training a serious long-term capital allocator.

Do NOT write generic industry commentary.
Do NOT write symbolic equations.
Focus on equity return mechanics and mispricing.

Structure strictly:

Title:

1. Capital Base & Return Engine
   - How capital deployed converts into equity compounding.

2. Structural Thesis
   - Why returns could structurally expand.
   - Where ROE / ROCE could inflect.

3. Counter-Thesis
   - What could structurally impair returns.
   - Where capital could be destroyed.

4. Valuation Anchor
   - How this segment is typically valued (P/E, P/B, EV/EBITDA, P/EV etc.).
   - What growth is implicitly priced in.

5. IRR Pathway
   - If ROE sustains at X% for 5 years, what book value compounding implies.
   - Where multiple expansion or compression alters outcomes.

6. Mispricing Test
   - What conditions would make current pricing irrationally pessimistic?
   - What would make it euphorically overvalued?

7. Apply This Lens To:
   - Name 3 Indian listed companies in this theme.
   - Compare them qualitatively on capital efficiency and valuation posture.

8. Self-Test Question
   - One question the reader must answer to test conviction.

Think in equity IRR, valuation asymmetry, and capital cycle logic.
Institutional tone.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------------------------
# Weekly Sector Stress Memo
# ---------------------------

def generate_weekly_allocator_memo():

    prompt = """
Generate a Weekly Capital Allocator Memo for Indian equities.

Structure:

Title:

1. Sector Showing Capital Inflow
2. Sector Showing Capital Exit
3. Which Sector Is Early Cycle?
4. Which Sector Is Late Cycle?
5. Valuation Extremes
6. Where Asymmetry Is Building
7. Biggest Mispricing Risk
8. One Sector To Study Deeply This Week

Institutional and analytical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------------------------
# Monthly Regime Review
# ---------------------------

def generate_monthly_regime():

    prompt = """
Generate a Capital Market Regime Review for India.

Include:

- Liquidity cycle direction
- Risk appetite shift
- Sector capital rotation
- Valuation compression vs expansion
- Retail vs institutional positioning
- Early signs of regime shift
- What type of strategy should dominate in this regime

Allocator-level tone.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------------------------
# Position Sizing Module
# ---------------------------

def generate_position_sizing():

    prompt = """
Generate an institutional note on Position Sizing & Risk.

Include:

- Risk of ruin logic
- Concentration vs diversification tradeoff
- When to size up aggressively
- When to cut exposure early
- Handling 40–60% drawdowns psychologically
- Sizing asymmetric 10x candidates

Practical. Analytical. No generic advice.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------------------------
# Main Execution Logic
# ---------------------------

def main():

    today = datetime.today()
    weekday = today.weekday()
    day = today.day
    month = today.month

    # Monthly Regime (1st of month)
    if day == 1:
        content = generate_monthly_regime()
        subject = "100X Monthly — Capital Regime Review"
        send_email(content, subject)
        return

    # Sunday Weekly Memo
    if weekday == 6:
        content = generate_weekly_allocator_memo()
        subject = "100X Weekly — Allocator Stress Memo"
        send_email(content, subject)
        return

    # Friday Position Sizing
    if weekday == 4:
        content = generate_position_sizing()
        subject = "100X — Position Sizing & Risk Discipline"
        send_email(content, subject)
        return

    # Default Daily Allocator Lesson
    headlines = get_market_headlines()
    memory = read_memory()
    theme = pick_theme(headlines, memory)
    lesson = generate_allocator_lesson(theme)
    write_memory(theme)
    subject = f"100X Allocator — {theme}"
    send_email(lesson, subject)


if __name__ == "__main__":
    main()
