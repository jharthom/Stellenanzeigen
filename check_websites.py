import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Liste von Websites
websites = {
    'Website1': 'https://www.hartung.net/jobs', 
    'Website2': 'https://b2b.grafik-werkstatt.de/stellenanzeigen', 
    'Website3': 'https://www.kunstundbild.de/#jobs'
}

# Speicherort für Hash-Werte
hash_file = "website_hashes.txt"

# E-Mail-Einstellungen
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')  # z.B. 'deine.email@gmail.com'
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # Dein App-Passwort oder reguläres Passwort
EMAIL_RECEIVER = os.environ.get('EMAIL_RECE')  # Empfänger

# Funktion zum Laden der gespeicherten Hash-Werte
def load_hashes():
    if not os.path.exists(hash_file):
        return {}
    
    with open(hash_file, 'r') as f:
        return {line.split()[0]: line.split()[1] for line in f.readlines()}

# Funktion zum Speichern der aktuellen Hash-Werte
def save_hashes(hashes):
    with open(hash_file, 'w') as f:
        for website, hash_value in hashes.items():
            f.write(f'{website} {hash_value}\n')

# Funktion zum Senden einer E-Mail
def send_email(website):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f'Website Changed: {website}'

    body = f'The content of {website} has changed!'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)
        server.quit()
        print(f'Email sent for {website}')
    except Exception as e:
        print(f'Failed to send email: {str(e)}')

# Hauptfunktion zur Überprüfung der Websites
def check_websites():
    current_hashes = {}
    previous_hashes = load_hashes()

    for name, url in websites.items():
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Erstellen des Hash-Werts des Inhalts
            current_hash = hashlib.sha256(response.content).hexdigest()
            current_hashes[name] = current_hash

            # Überprüfen, ob der Hash-Wert sich geändert hat
            if name in previous_hashes and current_hash != previous_hashes[name]:
                print(f'{name} has changed!')
                send_email(name)

        except requests.RequestException as e:
            print(f'Error fetching {url}: {e}')

    # Speichern der neuen Hash-Werte
    save_hashes(current_hashes)

if __name__ == "__main__":
    check_websites()
