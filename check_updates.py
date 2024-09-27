import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Liste der zu überwachenden Webseiten
WEBSITES = [
    'https://www.hartung.net/jobs', 
    'https://b2b.grafik-werkstatt.de/stellenanzeigen', 
    'https://www.kunstundbild.de/#jobs', 
    'https://www.goldbek.de/pages/team#stellenangebote', 
    'https://avancarte.de/unternehmen/karriere/'
]

# E-Mail-Konfiguration
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT')

# Funktion zur Überprüfung von Änderungen
def check_websites():
    for website in WEBSITES:
        response = requests.get(website)
        current_hash = hashlib.md5(response.content).hexdigest()

        # Überprüfen, ob der Hash der Website gespeichert ist
        try:
            with open(f"{website.replace('https://', '').replace('http://', '').replace('/', '_')}.hash", 'r') as file:
                saved_hash = file.read()
                if saved_hash != current_hash:
                    send_email(website)
        except FileNotFoundError:
            # Datei existiert nicht, also speichern wir den Hash
            with open(f"{website.replace('https://', '').replace('http://', '').replace('/', '_')}.hash", 'w') as file:
                file.write(current_hash)

# Funktion zur Sendung einer E-Mail
def send_email(website):
    subject = 'Stellenanzeigen von Mittbewerbern'
    body = f'Die Stellenanzeigen auf den folgenden Webseiten wurden aktualisiert:\n\n' + '\n'.join(updated_websites)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Aktiviere TLS
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    check_websites()
