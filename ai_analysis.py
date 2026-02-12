import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_thesis(stock_data):
    prompt = f"""
    Analyze this stock for 1-3 year potential.

    Data:
    {stock_data}

    Provide:
    - 3 Positives
    - 3 Risks
    - Expected Return Type (1-2x / 2-3x / 5-10x)
    - What must go right
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
