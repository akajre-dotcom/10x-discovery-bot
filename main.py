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

Write a deep industrial research paper explaining this system.

But this must end with capital allocation clarity.

Explain thoroughly:

- What the system technically does
- How it physically works
- Full value chain
- Where value and margins concentrate
- Which layers are commoditized
- Capital intensity by layer
- Entry barriers
- Bottlenecks and control points
- Substitution risks
- Historical industry evolution
- What changed recently to make this relevant
- 1–5 year structural outlook

Then answer decisively:

CAPITAL ALLOCATION VIEW

- Is this system structurally monetizable or utility-like?
- Where exactly does profit pool sit?
- Which layer has durable pricing power?
- Which layer will destroy capital?
- Who indirectly benefits most?
- Is this early-cycle, mid-cycle, or late-cycle?
- If you had to allocate serious capital, which layer would you focus on?
- What would invalidate the thesis?

Be decisive.
Do not stay neutral.
Do not hedge everything.
Write like someone allocating real capital.
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
