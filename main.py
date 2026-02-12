from scraper import get_all_data
from ranking import select_structured
from ai_analysis import generate_tag
from emailer import send_email

data = get_all_data()

selected = select_structured(data)

report = "WEEKLY OPPORTUNITY DASHBOARD\n"
report += "="*60 + "\n"
report += f"Scanned: {len(data)} | Selected: {len(selected)}\n\n"

for _, row in selected.iterrows():

    tag = generate_tag(row.to_dict())

    report += f"Stock: {row['Name']}\n"
    report += f"Sales Growth: {row['SalesGrowth']}%\n"
    report += f"Profit Growth: {row['ProfitGrowth']}%\n"
    report += f"ROCE: {row['ROCE']}%\n"
    report += f"{tag}\n"
    report += "-"*50 + "\n"

send_email(report)
