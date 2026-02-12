from scraper import get_screen_data
from ai_analysis import generate_thesis
from emailer import send_email

stocks = get_screen_data()

report = "WEEKLY 10X DISCOVERY REPORT\n\n"

for stock in stocks:
    thesis = generate_thesis(stock)
    report += "\n----------------------\n"
    report += thesis

send_email(report)
