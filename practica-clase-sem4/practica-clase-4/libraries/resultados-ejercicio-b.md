# Ejercicio B - bench-dynamic

Fabián Parreaguirre Hidalgo

`./build/bin/bench-dynamic 1000000 1000 1.0 2.0`, mismos parámetros del ejercicio A para poder comparar.

| Corrida | fill A (us) | fill B (us) | add (us) | total (us) |
|---|---|---|---|---|
| 1 | 2074719.6 | 2079213.7 | 1909876.3 | 6063810.3 |
| 2 | 2061045.6 | 2052875.2 | 1937613.3 | 6051535.0 |
| 3 | 2071157.6 | 2052478.7 | 1927743.3 | 6051380.2 |

```
$ ls -lh build/lib/libvectorops.so
-rwxrwxr-x 1 fabian fabian 16K libvectorops.so
```

16K contra 1.8K de la `.a`. La `.so` no lleva solo el código, también carga la tabla de símbolos dinámicos, `.plt`, `.got` y los headers de ELF que necesita el cargador para mapearla en tiempo de ejecución.

## Contra la versión estática

Lo interesante: la dinámica queda como 2.2x más lenta en total (6.05ms vs 2.79ms), corriendo exactamente el mismo algoritmo. La diferencia no está en el cálculo sino en cómo se resuelven las llamadas a `fill_vector`/`add_vectors` y a las funciones internas que estas usan por cada elemento.

Al compilar con `-fPIC`, gcc no puede asumir que los símbolos exportados no van a ser reemplazados por otra librería cargada antes (symbol interposition), entonces hasta las llamadas que quedan dentro de la misma `.so` pasan por la PLT/GOT en vez de ser un `call` directo. Con 1 millón de elementos y 1000 iteraciones son del orden de mil millones de llamadas extra pasando por esa indirección, y ahí se va el tiempo.

En resumen: la estática gana en velocidad porque todo se resuelve en compilación, pero el binario carga el código de la librería consigo mismo. La dinámica es más flexible (se puede actualizar sin recompilar, varios programas comparten la misma copia en memoria) a cambio de ese costo por llamada.
