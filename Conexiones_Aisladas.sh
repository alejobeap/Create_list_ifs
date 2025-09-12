#!/bin/bash


echo "conexiones aisladas"
python conexiones_aisladas.py

line_count=$(wc -l < interferogramasnoaislados.txt)
echo "📄 Número total de combinaciones generadas: $line_count"

framebatch_gapfill.sh -l -N -I ${PWD}/interferogramasnoaislados.txt 5 200 7 2
