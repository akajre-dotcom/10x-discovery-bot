import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_tag(stock):

    prompt = f"""
    Classify this stock based on data:

    {stock}

    Output only in this format:

    Profile: (Structural / Acceleration / Early Stage / Cyclical)
    Asymmetry: (Low / Medium / High)
    Risk: (One short line only)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
