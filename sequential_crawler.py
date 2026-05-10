import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

# Latencia alta para que el speedup del concurrente sea obvio
LATENCIA = 0.5


def fetch_page(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        time.sleep(LATENCIA)  # simula red lenta
        return response.text
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links


def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    return title.text.strip() if title else "Sin título"


def crawl_sequential(seed_url, max_pages=20):
    visited = set()
    pending = deque([seed_url])
    results = []

    start = time.time()

    while pending and len(visited) < max_pages:
        url = pending.popleft()
        if url in visited:
            continue

        print(f"[SEQ] ({len(visited)+1}/{max_pages}) {url}")
        html = fetch_page(url)
        visited.add(url)

        if html:
            title = extract_title(html)
            links = extract_links(html, url)
            results.append({"url": url, "title": title, "links_found": len(links)})
            for link in links:
                if link not in visited:
                    pending.append(link)

    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"[SECUENCIAL] Páginas visitadas : {len(visited)}")
    print(f"[SECUENCIAL] Tiempo total      : {elapsed:.2f}s")
    print(f"[SECUENCIAL] Tiempo por página : {elapsed / max(len(visited), 1):.2f}s")
    print(f"{'='*50}")
    return results, elapsed


if __name__ == "__main__":
    SEED = "https://books.toscrape.com"
    MAX_PAGES = 100

    print(f"\nCrawler SECUENCIAL — {MAX_PAGES} páginas con {LATENCIA}s de latencia por request\n")
    resultados, tiempo = crawl_sequential(SEED, max_pages=MAX_PAGES)
    print(f"\nTiempo esperado con 8 hilos: ~{tiempo / 8:.1f}s  (8x speedup teórico)")