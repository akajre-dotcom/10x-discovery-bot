from scraper import get_all_data
from ranking import select_structured
from ai_analysis import generate_tag
from emailer import send_email

# Step 1: Get all data
data = get_all_data()

# Step 2: Select structured opportunities
selected = select_structured(data)

# Step 3: Build email
report = "WEEKLY OPPORTUNITY DASHBOARD\n"
report += "=" * 50 + "\n\n"
report += f"Scanned: {len(data)} | Selected: {len(selected)}\n\n"

for _, row in selected.iterrows():

    tag = generate_tag({
        "Name": row["Name"],
        "Bucket": row["Bucket"]
    })

    report += f"{row['Name']}\n"
    report += f"{tag}\n"
    report += "-" * 40 + "\n"

# Step 4: Send email
send_email(report)
