import requests # Se importa la libreria para hacer peticiones HTTP
from bs4 import BeautifulSoup # Se importa la libreria para parsear el HTML
from urllib.parse import urljoin, urlparse # Se importan funciones para manejar las URLs, convierte URLs relativas a absolutas y para analizar las partes de una URL
from collections import deque # Se importa deque para manejar la cola de URLs pendientes de visitar, es una cola doble
import time # Se importa la libreria para manejar los tiempos de ejecución y para simular latencia de red

# Latencia simulada de red
LATENCIA = 0.5


def fetch_page(url): # Función para obtener el contenido HTML de una página dada su URL
    try:
        response = requests.get(url, timeout=5) # Se hace una petición GET a la URL con un timeout de 5 segundos 
        response.raise_for_status() # Si la respuesta tiene un código de estado de error, se lanza una excepción
        time.sleep(LATENCIA)  # simula red lenta
        return response.text # Si la petición es exitosa, se devuelve el contenido HTML de la página
    except Exception as e:
        print(f"[ERROR] {url}: {e}") # Si ocurre un error durante la petición, se imprime un mensaje de error con la URL y la excepción
        return None # Y retornamos None


def extract_links(html, base_url): # Función para extraer los enlaces de una página HTML, recibe el contenido HTML y la URL base para resolver enlaces relativos
    soup = BeautifulSoup(html, "html.parser") # Parseamos el HTML con BeautifulSoup
    links = set() # Se crea un conjunto para almacenar los enlaces únicos
    for tag in soup.find_all("a", href=True): # Se buscan todas las etiquetas <a> que tengan un atributo href
        full_url = urljoin(base_url, tag["href"]) # Se convierte el enlace relativo a absoluto usando la URL base
        if urlparse(full_url).netloc == urlparse(base_url).netloc: 
            links.add(full_url) # Si el enlace pertenece al mismo dominio que la URL base, se agrega al conjunto de enlaces
    return links # Se devuelve el conjunto de enlaces que se encontraron


def extract_title(html): # Función para extraer el título de una página HTML, recibe el contenido HTML
    soup = BeautifulSoup(html, "html.parser") # Se parea el HTML con BeautifulSoup
    title = soup.find("title") # Se busca la etiqueta <title> en el HTML
    return title.text.strip() if title else "Sin título" # Si se encuentra la etiqueta <title>, se devuelve su texto sin espacios, de lo contrario se devuelve "Sin título"


def crawl_sequential(seed_url, max_pages=20): # Funcion para realizar el crawler de manera secuencial, recibe la URL semilla y el número máximo de páginas a visitar
    visited = set() # Se crea un conjunto para almacenar las URLs visitadas y evitar ciclos
    pending = deque([seed_url]) # Se crea una cola doble para manejar las URLs pendientes por visitar, se inicializa con la URL semilla
    results = [] # Se crea una lista para almacenar los resultados de cada página visitada, como la URL, el título y el número de enlaces encontrados

    start = time.time() # Se registra el tiempo de inicio para medir el tiempo total de ejecución del crawler

    while pending and len(visited) < max_pages: # Mientras haya URLs pendientes por visitar y no se haya alcanzado el número máximo de páginas visitadas
        url = pending.popleft() # Se obtiene la siguiente URL de la cola de pendientes
        if url in visited: # Si la url ya se visitó, se omite y continua con el siguiente ciclo
            continue

        print(f"[SEQ] ({len(visited)+1}/{max_pages}) {url}") # Se imprime un mensaje indicando la URL que se está visitando y el progreso actual (número de páginas visitadas sobre el máximo)
        html = fetch_page(url) # Se obtiene el contenido HTML de la página usando la función fetch_page
        visited.add(url) # Se agrega la pagina al conjunto de visitados para evitar volver a visitarla

        if html: # Si se obtuvo el contenido HTML de la página, se procede a extraer el título y los enlaces
            title = extract_title(html)
            links = extract_links(html, url)
            results.append({"url": url, "title": title, "links_found": len(links)}) # Se inyecta el resultado de la página visitada en la lista de resultados, incluyendo la URL, el título y el número de enlaces encontrados
            for link in links:
                if link not in visited:
                    pending.append(link) # Se agregan los enlaces encontrados a la cola de pendientes, siempre y cuando no hayan sido visitados previamente

    elapsed = time.time() - start # Se calcula el tiempo total de ejecución del crawler restando el tiempo de inicio al tiempo actual
    print(f"\n{'='*50}")
    print(f"[SECUENCIAL] Páginas visitadas : {len(visited)}")
    print(f"[SECUENCIAL] Tiempo total      : {elapsed:.2f}s")
    print(f"[SECUENCIAL] Tiempo por página : {elapsed / max(len(visited), 1):.2f}s")
    print(f"{'='*50}")
    return results, elapsed


if __name__ == "__main__": # Si este archivo se ejecuta directamente, se ejecutará el siguiente bloque de código
    SEED = "https://books.toscrape.com"
    MAX_PAGES = 100

    print(f"\nCrawler SECUENCIAL — {MAX_PAGES} páginas con {LATENCIA}s de latencia por request\n")
    resultados, tiempo = crawl_sequential(SEED, max_pages=MAX_PAGES)
    print(f"\nTiempo esperado con 8 hilos: ~{tiempo / 8:.1f}s  (8x speedup teórico)")