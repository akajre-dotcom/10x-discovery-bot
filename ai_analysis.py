def generate_tag(stock):

    prompt = f"""
    A stock has been shortlisted from the '{stock['Bucket']}' category.

    Classify it.

    Output strictly:

    Profile: (Structural / Acceleration / Early Stage / Cyclical)
    Asymmetry: (Low / Medium / High)
    Risk: (One sharp sentence only)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
