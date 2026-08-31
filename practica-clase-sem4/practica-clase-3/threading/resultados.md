# Ejercicio A - cpu-naive vs cpu-affinity

Fabián Parreaguirre Hidalgo

Le agregué un argumento a los dos programas (`./cpu-naive N`, `./cpu-affinity N`), antes el número de hilos estaba fijo en 8 y para probar con menos tocaba recompilar. El tope lo dejé en 8 porque es lo que tiene mi máquina (i5-1135G7, 4 cores / 8 hilos lógicos).

El barrido de 1 a 8 lo dejé en `medir.sh`. Un detalle: `time` me estaba devolviendo los decimales con coma en vez de punto y eso corría las columnas del csv, tuve que forzar `LC_NUMERIC=C` para que saliera bien.

| Hilos | cpu-naive (s) | cpu-affinity (s) |
|---|---|---|
| 1 | 4.242 | 3.960 |
| 2 | 4.281 | 4.116 |
| 3 | 4.221 | 4.068 |
| 4 | 4.301 | 3.986 |
| 5 | 4.524 | 4.054 |
| 6 | 4.613 | 3.823 |
| 7 | 4.704 | 3.899 |
| 8 | 4.645 | 3.950 |

![tiempos](tiempos.png)

Lo primero que sorprende es que la curva no baja, se queda casi plana. Es porque acá cada hilo hace SU propio trabajo completo (256MB, 10 iteraciones) sin importar cuántos hilos más haya, entonces pedir más hilos no reparte el trabajo, lo multiplica. Con 8 CPUs disponibles y nada compartido entre hilos, eso corre prácticamente 100% en paralelo, así que el tiempo se mantiene aunque suba la cantidad de hilos. Es al revés del caso típico de Amdahl donde el problema tiene tamaño fijo y uno espera que el tiempo baje al repartirlo.

Donde sí hay diferencia clara es entre las dos versiones: `cpu-affinity` se mantiene entre 3.8 y 4.1s, mientras `cpu-naive` va subiendo poco a poco de 4.24 hasta 4.7. Sin `pthread_setaffinity_np` el scheduler de Linux puede mover el hilo de un core a otro en cualquier momento, y cada migración tira la cache que ya tenía caliente. Con la afinidad el hilo se queda pegado a su core todo el rato, entonces no pierde ese trabajo. La diferencia se nota más con 6-8 hilos porque ya casi no quedan cores libres para que el scheduler mueva cosas gratis.
