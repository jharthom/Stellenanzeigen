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

def hash_content(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def load_hashes():
    try:
        with open("website_hashes.txt", "r") as f:
            return {line.split(": ")[0]: line.split(": ")[1].strip() for line in f}
    except FileNotFoundError:
        return {}

def save_hashes(hashes):
    with open("website_hashes.txt", "w") as f:
        for site, hash_value in hashes.items():
            f.write(f"{site}: {hash_value}\n")
            print(f"Saved hash for {site}: {hash_value}")  # Debugging-Ausgabe
    print("Hashes saved to website_hashes.txt")  # Debugging-Ausgabe

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
            elif site not in old_hashes:
                print(f"Erster Hash für {site} erstellt.")

    save_hashes(new_hashes)

if __name__ == "__main__":
    check_websites()
