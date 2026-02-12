from scraper import get_all_data
from ranking import rank_stocks
from ai_analysis import generate_thesis
from emailer import send_email

data = get_all_data()
top_stocks = rank_stocks(data)

report = "WEEKLY STOCK DISCOVERY REPORT\n\n"

for _, row in top_stocks.iterrows():
    report += f"\nBucket: {row['Bucket']}\n"
    report += f"Stock: {row['Name']}\n"
    report += f"Sales Growth: {row['SalesGrowth']}%\n"
    report += f"ROCE: {row['ROCE']}%\n"
    report += f"Score: {round(row['Score'],2)}\n"

    thesis = generate_thesis(row.to_dict())
    report += thesis
    report += "\n-----------------------------\n"

send_email(report)
