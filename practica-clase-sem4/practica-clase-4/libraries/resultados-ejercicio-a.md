# Ejercicio A - bench-static

Fabián Parreaguirre Hidalgo

Hardware Info:

Processor: Intel Core i5-1135G7 (11va gen, 2.40GHz base)
Cores: 4 físicos
Threads: 8 lógicos (hyperthreading)
Compilador: gcc 15.2.0

`./build/bin/bench-static 1000000 1000 1.0 2.0`, 3 corridas.

| Corrida | fill A (us) | fill B (us) | add (us) | total (us) |
|---|---|---|---|---|
| 1 | 738366.4 | 690555.2 | 1360781.5 | 2789703.8 |
| 2 | 720857.1 | 684043.4 | 1388773.8 | 2793675.0 |
| 3 | 705113.9 | 679622.4 | 1322008.3 | 2706745.2 |

```
$ ls -lh build/lib/libvectorops.a
-rw-rw-r-- 1 fabian fabian 1.8K libvectorops.a
```

- 1.8K: es solo el `.o` de `vector_ops.c` metido en un `ar`, sin nada más.
- El linker mete `fill_vector`/`add_vectors` directo en el ejecutable en tiempo de compilación, las llamadas quedan resueltas sin indirección. Por eso es la más rápida de las tres versiones (comparo contra dinámica en el ejercicio B).
