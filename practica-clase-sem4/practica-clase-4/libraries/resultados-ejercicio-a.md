# Ejercicio A - bench-static

Fabián Parreaguirre Hidalgo

`./build/bin/bench-static 1000000 1000 1.0 2.0`. Corrí 3 veces para no confiarme de un solo dato, los números salen bastante parecidos.

| Corrida | fill A (us) | fill B (us) | add (us) | total (us) |
|---|---|---|---|---|
| 1 | 738366.4 | 690555.2 | 1360781.5 | 2789703.8 |
| 2 | 720857.1 | 684043.4 | 1388773.8 | 2793675.0 |
| 3 | 705113.9 | 679622.4 | 1322008.3 | 2706745.2 |

```
$ ls -lh build/lib/libvectorops.a
-rw-rw-r-- 1 fabian fabian 1.8K libvectorops.a
```

1.8K porque ahí adentro solo va el `.o` de `vector_ops.c` metido en un `ar`, sin ninguna otra dependencia ni info extra.

Con la librería estática el linker mete el código de `fill_vector` y `add_vectors` directo en el ejecutable en tiempo de compilación, así que las llamadas quedan resueltas de una vez, sin ninguna indirección de por medio. Por eso da los tiempos más bajos de las tres versiones del laboratorio (comparo contra la dinámica en el ejercicio B).
