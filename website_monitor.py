import requests
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
import os

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Liste der zu überwachenden Webseiten
urls = [
    "https://www.hartung.net/jobs", 
    "https://b2b.grafik-werkstatt.de/stellenanzeigen", 
    "https://www.kunstundbild.de/#jobs", 
    "https://www.goldbek.de/pages/team#stellenangebote", 
    "https://avancarte.de/unternehmen/karriere/"
]

# E-Mail Konfigurationen aus Umgebungsvariablen laden
sender_email = os.getenv('SENDER_EMAIL')
receiver_email = os.getenv('RECEIVER_EMAIL')
email_password = os.getenv('EMAIL_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')

# Funktion zum Abrufen der Webseite und Erstellen eines Hashwerts für den Inhalt
def get_website_content_hash(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        else:
            print(f"Fehler beim Abrufen der Website {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fehler beim Abrufen der Website {url}: {e}")
        return None

# Funktion zum Senden einer E-Mail-Benachrichtigung
def send_email_notification(url):
    subject = "Stellenanzeigen von Mittbewerbern"
    body = f"Die Stellenanzeigen auf der Website {url} wurden geändert."

    # E-Mail Nachricht erstellen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Mit dem SMTP-Server verbinden und die E-Mail senden
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, email_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"E-Mail-Benachrichtigung für {url} gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail für {url}: {e}")

# Endlos-Schleife, um die Webseiten regelmäßig zu überprüfen
if __name__ == "__main__":
    # Initiale Hashwerte für alle URLs
    last_hashes = {url: get_website_content_hash(url) for url in urls}

    print("Überwachung der Webseiten gestartet...")
    
    while True:
        time.sleep(60)  # 1 Woche warten, bevor erneut überprüft wird
        
        for url in urls:
            current_hash = get_website_content_hash(url)
            if current_hash and current_hash != last_hashes[url]:
                print(f"Änderungen festgestellt auf {url}!")
                send_email_notification(url)
                last_hashes[url] = current_hash  # Aktualisieren des gespeicherten Hashes
            else:
                print(f"Keine Änderungen auf {url} erkannt.")
