import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urljoin


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   
    database="webcrawler"
)
cursor = db.cursor()

visited = set()
base_url = "http://localhost:8000/"

def dfs(url):
    if url in visited:
        return
    visited.add(url)

    try:
        res = requests.get(url)
        # Cek kalau status 200, baru diproses
        if res.status_code != 200:
            print(f"Skipping {url}, status: {res.status_code}")
            return
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')

   
    title = soup.find('h1').text if soup.find('h1') else 'No Title'
    paragraf = soup.find('p').text if soup.find('p') else 'No Paragraph'

    if "404" not in paragraf and "Error" not in paragraf:
        
        cursor.execute("INSERT INTO artikel (url, judul, paragraf) VALUES (%s, %s, %s)", (url, title, paragraf))
        db.commit()
        print(f"Saved: {url}")
    else:
        print(f"Detected error content at {url}, skipping save.")

    
    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        dfs(next_url)


dfs(base_url + "index.html")

print("Selesai! Data sudah masuk ke database.")
