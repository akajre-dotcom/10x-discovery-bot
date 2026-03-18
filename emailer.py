import smtplib
import os
import logging
from email.message import EmailMessage

def send_email(content, subject):
    # Pull credentials from environment variables (GitHub Secrets)
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD") # MUST BE A 16-DIGIT APP PASSWORD
    receiver_email = os.getenv("EMAIL_RECEIVER", sender_email) # Sends to yourself by default

    if not sender_email or not sender_password:
        logging.error("CRITICAL: Email credentials missing. Check GitHub Secrets.")
        return

    # Construct the email
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        # Connect to Gmail's secure SSL port
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logging.info("Success: Email delivered!")
    except Exception as e:
        logging.error(f"Failed to send email. Error: {e}")
