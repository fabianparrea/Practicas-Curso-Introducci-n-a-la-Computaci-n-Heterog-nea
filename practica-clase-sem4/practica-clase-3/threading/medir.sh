#!/bin/bash
# corre cpu-naive y cpu-affinity de 1 a 8 hilos y guarda el tiempo real
# ojo: cada corrida tarda varios segundos, paciencia

export LC_NUMERIC=C  # si no, bash mete coma como separador decimal y rompe el csv
TIMEFORMAT='%R'

echo "hilos,naive,affinity" > tiempos.csv

for h in 1 2 3 4 5 6 7 8; do
  t_naive=$( { time ./cpu-naive $h > /dev/null; } 2>&1 )
  t_affinity=$( { time ./cpu-affinity $h > /dev/null; } 2>&1 )
  echo "$h,$t_naive,$t_affinity" >> tiempos.csv
  echo "hilos=$h  naive=${t_naive}s  affinity=${t_affinity}s"
done
