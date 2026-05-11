import time
from sequential_crawler import crawl_sequential
from concurrent_crawler import crawl_concurrent

SEED = "https://books.toscrape.com"
MAX_PAGES = 10
NUM_THREADS = 2

print("=" * 55)
print("   BENCHMARK — CRAWLER WEB CONCURRENTE")
print("=" * 55)

print("\n[1/5] Corriendo versión SECUENCIAL...")
_, t_seq = crawl_sequential(SEED, max_pages=MAX_PAGES)

tiempos = {}

'''for n in [1, 2, 4, 8]:
    print(f"\n[{list([1,2,4,8]).index(n)+2}/5] Corriendo versión CONCURRENTE con {n} hilo(s)...")
    _, t = crawl_concurrent(SEED, max_pages=MAX_PAGES, num_threads=n)
    tiempos[n] = t
'''

print(f"\n[2/2] Corriendo versión CONCURRENTE con {NUM_THREADS} hilo(s)...")
_, t = crawl_concurrent(SEED, max_pages=MAX_PAGES, num_threads=NUM_THREADS)
tiempo = t


print("\n")
print("=" * 55)
print(f"  {'Versión':<25} {'Tiempo (s)':>10} {'Speedup':>10}")
print("=" * 55)
print(f"  {'Secuencial':<25} {t_seq:>10.2f} {'1.00x':>10}")
'''for n, t in tiempos.items():
    speedup = t_seq / t
    print(f"  {f'Paralela ({n} hilos)':<25} {t:>10.2f} {speedup:>9.2f}x")
'''
print(f"  {f'Paralela ({NUM_THREADS} hilos)':<25} {tiempo:>10.2f} {t_seq/tiempo:>9.2f}x")
print("=" * 55)
print("\n✅ Benchmark terminado.")
