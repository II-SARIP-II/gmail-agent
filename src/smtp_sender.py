import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

GMAIL_SENDER = os.environ["GMAIL_ADDR"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]


def sendEmail(body, recipient):
    msg = MIMEText(body)
    msg['Subject'] = "TEST"
    msg['From'] = GMAIL_SENDER
    msg['To'] = recipient
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        smtp_server.sendmail(GMAIL_SENDER, recipient, msg.as_string())
    print("Message sent!\n", recipient, " -> ", body)
