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
    """Lädt die gespeicherten Hashes aus einer Datei."""
    if not os.path.exists(HASH_FILE):
        print(f"Hash-Datei {HASH_FILE} existiert nicht. Erstelle neue Hash-Datei.")
        return {}
    
    hashes = {}
    with open(HASH_FILE, 'r') as f:
        for line in f:
            site, hash_value = line.strip().split(',')
            hashes[site] = hash_value
    
    print(f"Geladene Hashes: {hashes}")
    return hashes

def save_hashes(hashes):
    """Speichert die aktuellen Hashes in einer Datei."""
    with open(HASH_FILE, 'w') as f:
        for site, hash_value in hashes.items():
            f.write(f"{site},{hash_value}\n")
    
    print("Hashes wurden erfolgreich gespeichert.")

def check_websites():
    # Lade gespeicherte Hashes der Webseiten
    old_hashes = load_hashes()
    new_hashes = {}

    for site, url in websites.items():
        # Hole den Inhalt der Webseite
        content = get_website_content(url)
        if content:
            # Erstelle einen neuen Hash aus dem aktuellen Webseiteninhalt
            new_hash = hash_content(content)
            new_hashes[site] = new_hash

            # Falls die Webseite vorher schon gehasht wurde, vergleiche
            if site in old_hashes:
                if old_hashes[site] != new_hash:
                    print(f"Änderung festgestellt auf {site}")
                    send_email(site)  # Sende E-Mail bei Änderung
                else:
                    print(f"Keine Änderung festgestellt auf {site}")
            else:
                # Falls es sich um eine neue Webseite handelt, setze den neuen Hash
                print(f"Neue Webseite entdeckt: {site}. Speichere den Hash.")
        else:
            print(f"Konnte den Inhalt der Webseite {site} nicht abrufen.")

    # Speichere die neuen Hashes
    save_hashes(new_hashes)
    print("Alle Hashes gespeichert.")

def send_email(site):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"Änderung festgestellt auf {site}"
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

if __name__ == "__main__":
    check_websites()
