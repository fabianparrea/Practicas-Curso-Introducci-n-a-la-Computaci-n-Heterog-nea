# lee tiempos.csv (lo genera medir.sh) y saca el grafico de hilos vs tiempo real
import csv
import matplotlib.pyplot as plt

hilos = []
naive = []
affinity = []

with open("tiempos.csv") as f:
    reader = csv.DictReader(f)
    for fila in reader:
        hilos.append(int(fila["hilos"]))
        naive.append(float(fila["naive"]))
        affinity.append(float(fila["affinity"]))

plt.plot(hilos, naive, marker="o", label="cpu-naive")
plt.plot(hilos, affinity, marker="s", label="cpu-affinity")

plt.xlabel("numero de hilos")
plt.ylabel("tiempo real (s)")
plt.title("cpu-naive vs cpu-affinity")
plt.xticks(hilos)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.savefig("tiempos.png", dpi=150, bbox_inches="tight")
print("listo, quedo guardado en tiempos.png")
