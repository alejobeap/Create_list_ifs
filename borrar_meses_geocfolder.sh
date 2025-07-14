#!/bin/bash

archivo=listaGEOC.txt
> $archivo
#ls GEOC/2* >> $archivo
# Only list directories inside GEOC/ starting with '2'
find GEOC/ -mindepth 1 -maxdepth 1 -type d -name "2*" >> "$archivo"

archivo
# Leer línea por línea
while IFS= read -r linea; do
    # Extraer el mes de la primera fecha (YYYYMMDD)
    mes=${linea:9:2}
    echo $mes
    # Si el mes está entre 05 y 09, guardar en archivo_mayo_sep
    if [[ "$mes" =~ ^0[5-9]$ || "$mes" == 09 ]]; then
        rm -rf $linea
        #echo "CON $linea" #>> "$archivo_mayo_sep"
    else
        continue
        #echo "SIN $linea" #>> "$archivo_otros"
    fi
done < "$archivo"
