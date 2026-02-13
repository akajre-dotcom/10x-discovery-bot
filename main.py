import os
import feedparser
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
# Get Latest Headlines
# ----------------------------

def get_headlines():
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:12]:
            headlines.append(entry.title)
    return headlines


# ----------------------------
# Topic Memory (avoid repeat)
# ----------------------------

def read_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return f.read().splitlines()
    except:
        return []


def write_memory(topic):
    with open(MEMORY_FILE, "a") as f:
        f.write(topic + "\n")


# ----------------------------
# Select Structural Industrial Theme
# ----------------------------

def pick_structural_theme(headlines, memory):

    prompt = f"""
From these recent headlines:

{headlines}

Identify ONE emerging or structurally important industrial system,
technology, manufacturing ecosystem, or infrastructure segment.

Rules:
- Must be product/system level (not macro like inflation).
- Must involve real assets, technology, supply chains, or industrial capability.
- Focus on NEW or evolving developments.
- Avoid repeating recently covered topics:
{memory[-15:]}

Return only the system name.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


# ----------------------------
# Generate Deep Research Paper
# ----------------------------

def generate_deep_research(system):

    prompt = f"""
System: {system}

Write a deep industrial research paper explaining this entire system.

This must feel like serious research, not a newsletter.

Explain thoroughly:

- What this system technically does
- How it physically works (engineering basics)
- Major components and process flow
- Global value chain structure
- India's role in this ecosystem
- Where value and margins concentrate
- Which layers are commoditized
- Capital intensity across layers
- Entry barriers and bottlenecks
- Substitution risks
- Policy and geopolitical exposure
- Historical evolution of this industry
- What changed recently to make it newsworthy
- 1–5 year structural outlook
- Where 10x–100x wealth could realistically be created
- Where capital will likely be destroyed

Write clearly and deeply.
No bullet-point frameworks unless necessary.
Avoid generic business language.
Assume reader wants true industrial mastery.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ----------------------------
# Main Execution
# ----------------------------

def main():

    headlines = get_headlines()
    memory = read_memory()

    system = pick_structural_theme(headlines, memory)
    research = generate_deep_research(system)

    write_memory(system)

    subject = f"Industrial Research — {system}"
    send_email(research, subject)


if __name__ == "__main__":
    main()
