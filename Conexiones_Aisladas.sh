#!/bin/bash

parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")

output="IFSforLiCSBAS_${current_dir}_${parent_dir}_${subsetnumero}.txt"


echo "conexiones aisladas"
python conexiones_aisladas.py

line_count=$(wc -l < interferogramasnoaislados.txt)
echo "📄 Número total de combinaciones generadas: $line_count"

framebatch_gapfill.sh -l -N -I ${PWD}/interferogramasnoaislados.txt 5 200 7 2




cat interferogramasnoaislados.txt >> $output

# Sort the file in-place (overwrite)
sort -o "$output" "$output"


