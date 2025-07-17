#!/bin/bash

echo "Run shorters connections (2 for each epoch)"
./create_interefrograms_all_txt.sh

echo "Create wrap and cc for shorters connections (2 for each epoch)"
./Create_filter_IFS.sh

# Ejecutar el resto tras 2 horas sin bloquear la terminal
(
  sleep 9200
  echo "Estimated the average coherence"
  python Estimate_Coherence_Average_from_DEM.py
  python plot_histogram_average_coherence.py
  ./filtered_average.sh
  python matriz_coherencia.py
  ./MesesLargos.sh
  ./Longs_create_interefrograms_all_txt.sh
  ./crear_standar_list.sh
  ./crear_final_list.sh
) &

echo "La segunda parte del script se ejecutará en 2 horas, mientras puedes seguir usando la terminal."
