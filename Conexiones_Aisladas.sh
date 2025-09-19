#!/bin/bash

parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")

output="IFSforLiCSBAS_${current_dir}_${parent_dir}_${subsetnumero}.txt"

if [ -n "$1" ]; then
    # Caso 1: argumento entregado → usarlo
    name=$(cat NameVolcano.txt 2>/dev/null)
    subsetnumero=$1
elif [ -s NameVolcano.txt ]; then
    # Caso 2: No hay $1, pero existe NameVolcano.txt
    name=$(cat NameVolcano.txt)
    
    if [ -s SubsetID.txt ]; then
        # Si también hay SubsetID.txt
        subsetnumero=$(cat SubsetID.txt)
    else
        # Si no hay SubsetID.txt → calcular con Python
        subsetnumero=$(python3 VER_Nombre_volcan_V2.py "$name" | tr -d '[]')
    fi
else
    # Caso 3: No hay $1 ni NameVolcano.txt válido
    echo "NameVolcano.txt is missing or empty"
    subsetnumero=$(python3 VER_Nombre_volcan_V2.py "$parent_dir" | tr -d '[]')
    exit 1
fi




echo "conexiones aisladas"
python conexiones_aisladas.py

line_count=$(wc -l < interferogramasnoaislados.txt)
echo "📄 Número total de combinaciones generadas: $line_count"

framebatch_gapfill.sh -l -N -I ${PWD}/interferogramasnoaislados.txt 5 200 7 2




cat interferogramasnoaislados.txt >> $output

# Sort the file in-place (overwrite)
sort -o "$output" "$output"


