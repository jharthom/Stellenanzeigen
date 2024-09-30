import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Liste der Webseiten zum Überprüfen
websites = {
    "example1": "https://www.hartung.net/jobs",
    "example2": "https://b2b.grafik-werkstatt.de/stellenanzeigen"
}

# Datei, in der Hashes der Webseiten gespeichert werden
HASH_FILE = "website_hashes.txt"

# E-Mail-Konfiguration

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

def send_test_email():
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "Test E-Mail"
    body = "Dies ist eine Test-E-Mail von GitHub Actions."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Für Gmail, ggf. anpassen
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        print("Test-E-Mail gesendet.")
    except Exception as e:
        print(f"Fehler beim Senden der Test-E-Mail: {e}")

if __name__ == "__main__":
    send_test_email()
