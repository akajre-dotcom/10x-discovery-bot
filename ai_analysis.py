import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_thesis(stock):
    prompt = f"""
    Analyze this stock for 2-3 year 10x potential:

    {stock}

    Provide:
    - 4 Positives
    - 4 Risks
    - 10x Feasibility (Low/Medium/High)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
