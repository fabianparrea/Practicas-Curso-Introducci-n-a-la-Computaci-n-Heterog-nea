# mismo estilo que el grafico de threading, pero aca son dos programas
# con escalas de tiempo bastante distintas asi que van en subplots separados
import csv
import matplotlib.pyplot as plt

hilos = []
matmul = []
softmax = []

with open("tiempos.csv") as f:
    reader = csv.DictReader(f)
    for fila in reader:
        hilos.append(int(fila["hilos"]))
        matmul.append(float(fila["matmul"]))
        softmax.append(float(fila["softmax"]))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

ax1.plot(hilos, matmul, marker="o", color="tab:blue")
ax1.set_title("matmul_tiled_openmp")
ax1.set_xlabel("numero de hilos")
ax1.set_ylabel("tiempo (s)")
ax1.set_xticks(hilos)
ax1.grid(True, linestyle="--", alpha=0.5)

ax2.plot(hilos, softmax, marker="o", color="tab:orange")
ax2.set_title("softmax_openmp")
ax2.set_xlabel("numero de hilos")
ax2.set_ylabel("tiempo (s)")
ax2.set_xticks(hilos)
ax2.grid(True, linestyle="--", alpha=0.5)

fig.tight_layout()
fig.savefig("tiempos.png", dpi=150, bbox_inches="tight")
print("grafico guardado en tiempos.png")
