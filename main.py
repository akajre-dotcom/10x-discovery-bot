from scraper import get_all_data
from ranking import select_structured
from ai_analysis import generate_tag
from emailer import send_email

data = get_all_data()

# Ensure numeric
data["MarketCap"] = data.get("MarketCap", 0)

selected = select_structured(data)

report = "WEEKLY OPPORTUNITY DASHBOARD\n\n"

report += f"Scanned: {len(data)} | Selected: {len(selected)}\n\n"

report += "Stock | Sales% | Profit% | ROCE% | Tag\n"
report += "-"*60 + "\n"

for _, row in selected.iterrows():

    tag = generate_tag(row.to_dict())

    report += f"{row['Name']} | "
    report += f"{row['SalesGrowth']} | "
    report += f"{row['ProfitGrowth']} | "
    report += f"{row['ROCE']} | "
    report += f"{tag}\n"

send_email(report)
