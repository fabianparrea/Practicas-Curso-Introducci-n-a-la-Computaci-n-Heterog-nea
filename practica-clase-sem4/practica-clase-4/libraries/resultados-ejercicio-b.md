# Ejercicio B - bench-dynamic

Fabián Parreaguirre Hidalgo

Hardware Info:

Processor: Intel Core i5-1135G7 (11va gen, 2.40GHz base)
Cores: 4 físicos
Threads: 8 lógicos (hyperthreading)
Compilador: gcc 15.2.0

`./build/bin/bench-dynamic 1000000 1000 1.0 2.0`, mismos parámetros del ejercicio A.

| Corrida | fill A (us) | fill B (us) | add (us) | total (us) |
|---|---|---|---|---|
| 1 | 2074719.6 | 2079213.7 | 1909876.3 | 6063810.3 |
| 2 | 2061045.6 | 2052875.2 | 1937613.3 | 6051535.0 |
| 3 | 2071157.6 | 2052478.7 | 1927743.3 | 6051380.2 |

```
$ ls -lh build/lib/libvectorops.so
-rwxrwxr-x 1 fabian fabian 16K libvectorops.so
```

- 16K contra 1.8K de la `.a`: la `.so` carga además la tabla de símbolos dinámicos, `.plt`, `.got` y los headers de ELF para el cargador.
- Total ~6.05s contra ~2.79s de la estática, 2.2x más lento con el mismo algoritmo.
- Causa: con `-fPIC`, gcc no puede asumir que los símbolos exportados no serán reemplazados por otra librería (symbol interposition), así que hasta las llamadas internas de la `.so` pasan por PLT/GOT en vez de un `call` directo. Con ~mil millones de llamadas a `fill_vector`/`add_vectors` ahí se va el tiempo.
- La estática gana velocidad porque todo se resuelve en compilación; la dinámica gana en flexibilidad (se actualiza sin recompilar, varios programas comparten la misma copia en memoria) a cambio de ese costo por llamada.
