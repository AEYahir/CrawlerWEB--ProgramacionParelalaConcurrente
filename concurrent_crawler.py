import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
import queue
import time

LATENCIA = 0.5

CENTINELA = object()

visited_lock = threading.Lock()
results_lock = threading.Lock()

visited = set()
results = []


def fetch_page(url): # Función para obtener el contenido HTML de una página dada su URL
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        time.sleep(LATENCIA)  
        return response.text
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def extract_links(html, base_url): # Función para extraer los enlaces de una página HTML, recibe el contenido HTML y la URL base para resolver enlaces relativos
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links


def extract_title(html): # Función para extraer el título de una página HTML, recibe el contenido HTML
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    return title.text.strip() if title else "Sin título"


def worker(task_queue, seed_url, max_pages): # Función que repite cada hilo para procesar las URLs de la cola de tareas, recibe la cola de tareas, la URL semilla y el número máximo de páginas a visitar
    while True:
        url = task_queue.get()  

        if url is CENTINELA: # Si se recibe la señal de centinela, se marca la tarea como hecha y se rompe el ciclo para terminar el hilo   
            task_queue.task_done()
            break

        with visited_lock:
            if url in visited or len(visited) >= max_pages:
                task_queue.task_done()
                continue
            visited.add(url)

        print(f"[{threading.current_thread().name}] ({len(visited)}/{max_pages}) {url}")
        html = fetch_page(url)

        if html:
            title = extract_title(html)
            links = extract_links(html, url)

            with results_lock:
                results.append({"url": url, "title": title, "links_found": len(links)})

            with visited_lock:
                for link in links:
                    if link not in visited and len(visited) + task_queue.qsize() < max_pages:
                        task_queue.put(link)

        task_queue.task_done()


def crawl_concurrent(seed_url, max_pages=20, num_threads=8):
    global visited, results
    visited = set()
    results = []

    task_queue = queue.Queue()
    task_queue.put(seed_url)

    start = time.time()

    threads = []
    for i in range(num_threads):
        t = threading.Thread(
            target=worker,
            args=(task_queue, seed_url, max_pages),
            name=f"Hilo-{i+1}"
        )
        threads.append(t)
        t.start()

    task_queue.join()  

    
    for _ in range(num_threads):
        task_queue.put(CENTINELA)
    for t in threads:
        t.join()

    elapsed = time.time() - start
    print(f"\n{'='*50}")
    print(f"[CONCURRENTE] Hilos usados      : {num_threads}")
    print(f"[CONCURRENTE] Páginas visitadas : {len(visited)}")
    print(f"[CONCURRENTE] Tiempo total      : {elapsed:.2f}s")
    print(f"[CONCURRENTE] Tiempo por página : {elapsed / max(len(visited), 1):.2f}s")
    print(f"{'='*50}")
    return results, elapsed


if __name__ == "__main__":
    SEED = "https://books.toscrape.com"
    MAX_PAGES = 100
    NUM_THREADS = 8

    print(f"\nCrawler CONCURRENTE — {MAX_PAGES} páginas, {NUM_THREADS} hilos, {LATENCIA}s de latencia por request\n")
    res, t = crawl_concurrent(SEED, max_pages=MAX_PAGES, num_threads=NUM_THREADS)