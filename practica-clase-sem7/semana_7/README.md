# Práctica en Clase 6 — CUDA (Semana 7) 
# Fabián Parreaguirre Hidalgo

## ¿Qué es LeetGPU?
Es como un LeetCode pero para GPU, una web donde se puede poner código CUDA, lo corre en una GPU real en la nube y valida el resultado. Por lo que no requiere una GPU local, la práctica de esta semana se corrió enteramente en LeetGPU.

**Entorno usado:** LeetGPU, CUDA 11.7.

## Hardware: NVIDIA GTX Titan X (Maxwell, 2015)

| Característica | Valor |
|---|---|
| Arquitectura | Maxwell (GM200) |
| CUDA Cores | 3072 |
| SMs | 24 (128 cores c/u) |
| VRAM | 12 GB GDDR5 |
| Bus de memoria | 384 bits |
| Ancho de banda | ~336 GB/s |
| Compute Capability | 5.2 |

---

## Ejercicio A: suma de vectores (`vector-add/`)

Calcula `C[i] = A[i] + B[i]`, un elemento por hilo.

### Kernel completado (Lo faltante para que el código pudiese compilar)
```cpp
__global__ void vector_add_kernel(const float *a, const float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < n) {
        c[i] = a[i] + b[i];
    }
}
```

### Índice global del hilo

Cada hilo de la GPU necesita saber qué casilla del arreglo es el que necesita procesar y los hilos están organizados en bloques de tamaño fijo, en este caso 256. El índice global se calcula como i = blockIdx.x * blockDim.x + threadIdx.x, donde blockIdx.x indica qué bloque es, blockDim.x es el tamaño del bloque  (que es 256), y threadIdx.x es la posición del hilo dentro de ese bloque. Multiplicando el número de bloque por su tamaño se obtiene dónde empieza ese bloque dentro del arreglo completo y sumándole la posición interna se llega a la casilla exacta que le corresponde a cada hilo. Por ejemplo, el hilo número 10 del bloque número 3 calcula i = 3*256 + 10 = 778, por lo que procesa la casilla 778 del arreglo.


### Por qué hace falta `if (i < n)`

El if (i < n) es necesario porque el número de hilos lanzados no siempre coincide exactamente con el tamaño del arreglo, ya que los bloques tienen tamaño fijo. Cuando sobran hilos, si no existiese este chequeo intentarían leer o escribir fuera del arreglo, causando errores o resultados incorrectos.

### Resultado
```
Running in FUNCTIONAL mode...
Compiling...
Executing...
vector-add n=1048576: OK
Exit status: 0
```

### Preguntas
- **¿Cuántos bloques se lanzan cuando N=1048576 y cada bloque tiene 256 hilos?** Se lanzan 4096 bloques pues sería dividiendo la cantidad total de elementos del vector entre los hilos que tiene cada bloque: 1048576 / 256 = 4096

- **¿Qué ocurre si N no es múltiplo del tamaño del bloque?** El último bloque queda con hilos sobrantes (`i >= n`); sin el `if (i < n)` accederían a memoria fuera de rango.


- **¿Qué transferencias de memoria ocurren entre CPU y GPU?** Serían dos transferencias: Host→Device (para copiar A y B de CPU a GPU) y una transferencia Device→Host (para copiar el resultado C de GPU a CPU) al finalizar el kernel.

---

## Ejercicio B: producto punto (`dot-product/`)

Calcula un escalar `s = Σ A[i]*B[i]` mediante reducción por bloque en memoria compartida.

Reducción es cuando se combinam muchos valores en uno solo, en vez de que cada hilo guarde su propio resultado. Por ejemplo, en el producto punto de este ejercicio esto hace falta porque el resultado es un único número, cada hilo calcula su producto local, lo guarda en memoria compartida y los hilos del bloque lo van sumando hasta dejar un solo total por bloque, que luego se suma en la CPU para dar el resultado final.

### Producto local
```cpp
if (i < n) {
    value = a[i] * b[i];
}
```

### Reducción en el bloque
```cpp
for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
        cache[tid] += cache[tid + stride];
    }
    __syncthreads();
}
```
Combina por pares las mitades del arreglo compartido hasta dejar la suma total en `cache[0]`.

### Papel de `__syncthreads()`

__syncthreads() es una barrera que hace esperar a todos los hilos del bloque en ese punto antes de seguir, esto evita que alguno lea un dato que otro aún no escribió. En el producto punto se usa tras guardar cada producto en memoria compartida, y al final de cada ronda de la suma por pares, para que nadie use un valor desactualizado. Sin ella habría una condición de carrera y el resultado saldría erróneo.

### Resultados
```
dot-product n=1048576: gpu=-21.250000 cpu=-21.250000 error=0.000000 OK
dot-product n=4194304: gpu=-0.500000 cpu=-0.500000 error=0.000000 OK
```
(`n` quedó por defecto en `1 << 20`; para la segunda corrida se cambió temporalmente la línea 61 a `4194304`.)

### Preguntas
- **¿Por qué este ejercicio no puede resolverse solamente escribiendo un valor independiente por hilo?** Porque el resultado final del código es un escalar único y hace falta combinar los valores de todos los hilos por lo que no puede ser independiente de un hilo.

- **¿Cuántos valores parciales se copian de GPU a CPU** Se copia un valor parcial por cada bloque lanzado (no por hilo): 4096 con N=1048576, y 16384 con N=4194304, calculados como N / 256.

- **¿Qué pasaría si se elimina alguna sincronización dentro de la reducción?** Si se elimina alguna sincronización, algunos hilos podrían leer un valor de cache que otro hilo todavía no terminó de escribir o actualizar en esa ronda, generando una condición de carrera. Esto produciría una suma incorrecta e incluso el resultado podría variar entre distintas ejecuciones o distintas GPUs, ya que depende del orden en que los hilos terminan.

---

## Ejercicio C: softmax (`softmax/`)

Softmax convierte los números de una fila en porcentajes que suman 1, dándole más peso a los valores más grandes. Se resta el máximo de la fila antes de aplicar exp() para evitar que el cálculo se desborde, sin cambiar el resultado final. Cada fila se procesa en un bloque distinto, y sus hilos se reparten las columnas. Se necesitan dos reducciones seguidas porque primero hay que encontrar el máximo de la fila, y recién con ese valor se puede calcular y sumar las exponenciales de toda la fila.


### Cambios hechos en el código

**1. Reducción para encontrar el máximo de la fila**
```cpp
local_max = fmaxf(local_max, input[row * cols + col]);
...
cache[tid] = fmaxf(cache[tid], cache[tid + stride]);
```
Cada hilo calcula el máximo de sus columnas, y luego se combinan por pares hasta obtener el máximo de toda la fila.

**2. Exponenciales desplazadas por el máximo**
```cpp
output[idx] = expf(input[idx] - row_max);
local_sum += output[idx];
```
Se resta el máximo antes de exponenciar (evita overflow) y se acumula la suma parcial de cada hilo.

**3. Reducción para sumar las exponenciales**
```cpp
cache[tid] += cache[tid + stride];
```
Combina las sumas parciales de todos los hilos hasta dejar el total de la fila en una sola posición.

**4. Normalización de cada elemento**
```cpp
output[idx] /= row_sum;
```
Divide cada exponencial entre el total de la fila, dejando los valores finales de softmax.



### Resultados
```
softmax rows=128 cols=1024: OK
softmax rows=256 cols=2048: OK
```
(`rows`/`cols` quedaron por defecto en `128`/`1024`; la segunda corrida se probó cambiando temporalmente esas líneas a `256`/`2048`.)

### Preguntas
- **¿Por qué se calcula primero el máximo de cada fila?** Se calcula el máximo antes porque si se mete expf() a números grandes directamente, se puede desbordar y dar infinito o basura. Restando el máximo, el valor más grande queda en exp(0)=1 y el resto no pasa de 1, así no se trunca. Y el resultado no cambia, porque esa resta se cancela después al dividir entre la suma.


- **¿Qué partes del algoritmo requieren cooperación entre hilos del mismo bloque?** Las que requieren cooperación son las dos reducciones, la del máximo y la de la suma, porque ahí sí un hilo necesita el valor de otro para combinar resultados. En cambio, calcular expf() y normalizar cada elemento lo hace cada hilo por su cuenta, sin depender de los demás.

- **¿Qué limitación tiene usar un solo bloque por fila cuando cols crece mucho?** La limitación es que cada fila corre en un solo bloque. Si cols crece mucho, cada hilo tiene que procesar más columnas una tras otra en su bucle, así que se vuelve más lento sin sumar más paralelismo. Este diseño escala bien si se aumentan rows porque cada fila es un bloque independiente , pero no si se aumentan cols.
