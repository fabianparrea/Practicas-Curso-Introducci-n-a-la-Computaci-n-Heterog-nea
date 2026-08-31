#!/bin/bash
# barrido de hilos de 1 a 8 para matmul_tiled_openmp y softmax_openmp
# usa repeticiones mas altas que el default para que el tiempo no sea ruido

echo "hilos,matmul,softmax" > tiempos.csv

for h in 1 2 3 4 5 6 7 8; do
  t_matmul=$(./matmul_tiled_openmp $h 512 32 20 | grep Tiempo | awk '{print $2}')
  t_softmax=$(./softmax_openmp $h 200000 | grep Tiempo | awk '{print $2}')
  echo "$h,$t_matmul,$t_softmax" >> tiempos.csv
  echo "hilos=$h  matmul=${t_matmul}s  softmax=${t_softmax}s"
done
