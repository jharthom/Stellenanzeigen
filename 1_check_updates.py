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

def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der Webseite {url}: {e}")
        return None

def hash_content(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE, 'r') as f:
        return {line.split(',')[0]: line.split(',')[1].strip() for line in f}

def save_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        for site, hash_value in hashes.items():
            f.write(f"{site},{hash_value}\n")

def send_test_email():
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "Website {site} wurde geändert!"
    body = "Die Webseite {site} hat sich geändert. Bitte überprüfen Sie sie unter {websites[site]}."
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

def check_websites():
    old_hashes = load_hashes()
    new_hashes = {}

    for site, url in websites.items():
        content = get_website_content(url)
        if content:
            new_hash = hash_content(content)
            new_hashes[site] = new_hash

            if site in old_hashes and old_hashes[site] != new_hash:
                print(f"Änderung festgestellt auf {site}")
                send_email(site)

    save_hashes(new_hashes)

    send_email(site)

if __name__ == "__main__":
    check_websites()
