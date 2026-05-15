import time
import os
from sequential_crawler import crawl_sequential
from concurrent_crawler import crawl_concurrent
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

SEED        = os.getenv("SEED_URL", "https://books.toscrape.com")
MAX_PAGES   = int(os.getenv("MAX_PAGES", 50))
NUM_THREADS = [int(x.strip()) for x in os.getenv("NUM_THREADS", "1,2,4,8").split(",")]

print("=" * 55)
print("   BENCHMARK — CRAWLER WEB CONCURRENTE")
print("=" * 55)

tiempos = {}
for i, n in enumerate(NUM_THREADS, start=2):
    print(f"\n[{i}/{len(NUM_THREADS)+1}] Corriendo versión CONCURRENTE con {n} hilo(s)...")
    _, t = crawl_concurrent(SEED, max_pages=MAX_PAGES, num_threads=n)
    tiempos[n] = t

print(f"\n[1/{len(NUM_THREADS)+1}] Corriendo versión SECUENCIAL...")
_, t_seq = crawl_sequential(SEED, max_pages=MAX_PAGES)



print("\n")
print("=" * 55)
print(f"  {'Versión':<25} {'Tiempo (s)':>10} {'Speedup':>10}")
print("=" * 55)
print(f"  {'Secuencial':<25} {t_seq:>10.2f} {'1.00x':>10}")
for n, t in tiempos.items():
    speedup = t_seq / t
    print(f"  {f'Paralela ({n} hilos)':<25} {t:>10.2f} {speedup:>9.2f}x")
print("=" * 55)
print("\n✅ Benchmark terminado.")



# --- Datos ---
etiquetas = ["Secuencial"] + [f"{n} hilos" for n in tiempos.keys()]
tiempos_vals = [t_seq] + list(tiempos.values())
speedups = [1.0] + [t_seq / t for t in tiempos.values()]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor("#0a0a0f")

for ax in (ax1, ax2):
    ax.set_facecolor("#12121a")
    ax.tick_params(colors="#94a3b8")
    ax.xaxis.label.set_color("#94a3b8")
    ax.yaxis.label.set_color("#94a3b8")
    ax.title.set_color("#e2e8f0")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1e293b")

colores = ["#475569"] + ["#00ff88"] * len(tiempos)

# --- Gráfica 1: Tiempo de ejecución ---
bars1 = ax1.bar(etiquetas, tiempos_vals, color=colores, edgecolor="#1e293b", width=0.5)
ax1.set_title("Tiempo de Ejecución", fontweight="bold", pad=12)
ax1.set_ylabel("Segundos (s)")
ax1.set_xlabel("Versión")
for bar, val in zip(bars1, tiempos_vals):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
             f"{val:.2f}s", ha="center", va="bottom", color="#e2e8f0", fontsize=9)

# --- Gráfica 2: Speedup ---
bars2 = ax2.bar(etiquetas, speedups, color=colores, edgecolor="#1e293b", width=0.5)
ax2.set_title("Speedup vs Secuencial", fontweight="bold", pad=12)
ax2.set_ylabel("Speedup (x)")
ax2.set_xlabel("Versión")
ax2.axhline(y=1, color="#475569", linestyle="--", linewidth=0.8)
for bar, val in zip(bars2, speedups):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
             f"{val:.2f}x", ha="center", va="bottom", color="#e2e8f0", fontsize=9)

plt.suptitle("Benchmark — Web Crawler Concurrente", color="#e2e8f0",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("benchmark_results.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.show()
print("📊 Gráfica guardada como benchmark_results.png")