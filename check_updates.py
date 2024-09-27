import requests
import hashlib
import os
import json
import time
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

# Datei, in der die Hashes der Webseiten gespeichert werden
HASHES_FILE = 'hashes.json'

# E-Mail-Konfiguration
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT')

def load_hashes():
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASHES_FILE, 'w') as f:
        json.dump(hashes, f)

def get_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def send_email(updated_websites):
    subject = 'Stellenanzeigen von Mittbewerbern'
    body = f'Die Stellenanzeigen auf den folgenden Webseiten wurden aktualisiert:\n\n' + '\n'.join(updated_websites)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Aktiviere TLS
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print('E-Mail gesendet!')
    except Exception as e:
        print(f'Fehler beim Senden der E-Mail: {e}')

def check_websites():
    hashes = load_hashes()
    updates = []

    for website in WEBSITES:
        try:
            response = requests.get(website)
            response.raise_for_status()
            content = response.text
            current_hash = get_hash(content)

            if website in hashes:
                if hashes[website] != current_hash:
                    updates.append(website)
            hashes[website] = current_hash

        except requests.RequestException as e:
            print(f'Fehler beim Abrufen von {website}: {e}')

    save_hashes(hashes)
    return updates

if __name__ == "__main__":
    while True:
        updated_websites = check_websites()
        if updated_websites:
            print(f'Folgende Webseiten wurden aktualisiert: {", ".join(updated_websites)}')
            send_email(updated_websites)  # Sende E-Mail-Benachrichtigung
        else:
            print('Keine Änderungen an den Webseiten.')
        
        # Wartezeit von 60 Minuten
        time.sleep(60)
