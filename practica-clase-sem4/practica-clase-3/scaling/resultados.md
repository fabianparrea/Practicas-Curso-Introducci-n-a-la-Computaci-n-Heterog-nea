# Ejercicio B - matmul_tiled_openmp y softmax_openmp

Fabián Parreaguirre Hidalgo

Hardware Info:

Processor: Intel Core i5-1135G7 (11va gen, 2.40GHz base)
Cores: 4 físicos
Threads: 8 lógicos (hyperthreading)
Compilador: gcc 15.2.0

Estos dos ya recibían el número de hilos por argumento. Corrí 1 a 8 hilos, subiendo un poco las repeticiones del default para que se notara el efecto (matmul: 512x512, tile 32, 20 rep; softmax: 200000 rep). Barrido en `medir.sh`/`tiempos.csv`.

| Hilos | matmul_tiled_openmp | softmax_openmp |
|---|---|---|
| 1 | 2.191364 | 1.707279 |
| 2 | 1.047927 | 1.292168 |
| 3 | 0.729133 | 1.196376 |
| 4 | 0.543329 | 1.270266 |
| 5 | 0.584214 | 1.504681 |
| 6 | 0.523592 | 1.712192 |
| 7 | 0.467993 | 1.741277 |
| 8 | 0.472101 | 1.884342 |

![tiempos](tiempos.png)

**matmul_tiled_openmp**
- Speedup con 8 hilos: 4.64x. Eficiencia: 58%.
- Amdahl con el punto de 8 hilos: fracción paralela ≈ 90%, el otro 10% es serial (llenado de matrices, checksum, reparto de tiles).
- Se aplana después de 4 hilos porque ahí entran los hyperthreads (4 cores físicos, 8 lógicos), que no ayudan mucho en cómputo de punto flotante.
- Con 4 hilos el speedup da 4.03x (por encima de 4): speedup superlineal, la matriz partida en tiles más chicos cabe mejor en cache L2.

**softmax_openmp**
- Mejora hasta 3 hilos (1.71s a 1.20s), después empeora, y con 8 hilos (1.88s) queda peor que con 1 solo.
- Causa: la función procesa solo 1000 elementos pero se llama 200000 veces, abriendo y cerrando 3 regiones `#pragma omp parallel for` cada vez. El overhead fijo de crear/sincronizar hilos le gana al trabajo real por hilo (125 elementos con 8 hilos).
- Amdahl no aplica bien acá porque el supuesto de "más hilos nunca empeora" se rompe.
