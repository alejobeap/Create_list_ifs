#!/bin/bash

parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")

if [ -n "$1" ]; then
    # If an argument was provided
    name=$(cat NameVolcano.txt)
    subsetnumero=$1
else
    if [ -s NameVolcano.txt ]; then
        # If NameVolcano.txt exists and is not empty
        name=$(cat NameVolcano.txt)
        subsetnumero=$(python3 VER_Nombre_volcan_V2.py "$name" | tr -d '[]')
    else
        echo "NameVolcano.txt is missing or empty"
        subsetnumero=$(python3 VER_Nombre_volcan_V2.py "$parent_dir" | tr -d '[]')
        exit 1
    fi
fi





scp -r GEOC/geo/* GEOC/
# Define file names
file1="standar_list.txt"
file2="Longs_combination_longs.txt"
output="IFSforLiCSBAS_${current_dir}_${parent_dir}_${subsetnumero}.txt"
Chilescase=0

# Check if both input files exist
if [[ ! -f $file1 || ! -f $file2 ]]; then
    echo "One or both input files do not exist."
    exit 1
fi

# Clear the output file
> "$output"

# Combine the files and sort the result
cat "$file1" "$file2" | sort > "$output"

# Archivo de entrada
archivo="IFSforLiCSBAS.txt"

# Archivos temporales
archivo_otros="tmp_otros.txt"
archivo_mayo_sep="tmp_mayo_sep.txt"

# Limpiar archivos temporales previos
> "$archivo_otros"
> "$archivo_mayo_sep"


# Default Chilescase to "n" 0 if not "y"1 or "n" 0
if [[ "$Chilescase" != 1 && "$Chilescase" != 0 ]]; then
        Chilescase=0
fi

if [[ "$Chilescase" == 1 ]]; then
# Leer línea por línea
  while IFS= read -r linea; do
    # Extraer el mes de la primera fecha (YYYYMMDD)
      mes=${linea:4:2}

    # Si el mes está entre 05 y 09, guardar en archivo_mayo_sep
      if [[ "$mes" =~ ^0[5-9]$ ]]; then
          echo "$linea" >> "$archivo_mayo_sep"
      else
          echo "$linea" >> "$archivo_otros"
      fi
  done < "$archivo"

# Concatenar las líneas: primero las que NO son de mayo a septiembre, luego las otras
  cat "$archivo_otros" "$archivo_mayo_sep" > "$archivo"

# Limpiar archivos temporales
  rm "$archivo_otros" "$archivo_mayo_sep"
fi

# Check if the output file was created
if [[ -f $output ]]; then
    echo "Files have been successfully combined and sorted into $output."
else
    echo "Failed to create the output file."
fi

if [[  "$Chilescase" == 1 ]]; then
    echo "Delete remaining months for Chile area for avoid unwrapping time"
    rm -rf GEOC/20*06*_* GEOC/20*08*_* GEOC/20*08*_* GEOC/20*09*_* GEOC/20*10*_*
fi

echo "Delete empty folders in GEOC"
./deletefolder_GEOC.sh

line_count=$(wc -l < "$output")
echo "Número total de combinaciones generadas: $line_count"


parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")


echo "framebatch_gapfill.sh -l -N -I ${PWD}/IFSforLiCSBAS_${current_dir}_${parent_dir}_${subsetnumero}.txt 5 200 7 2"

framebatch_gapfill.sh -l -N -I ${PWD}/IFSforLiCSBAS_${current_dir}_${parent_dir}_${subsetnumero}.txt 5 200 7 2


#echo "Baseline"
#mk_bperp_file.sh
#mv GEOC/baselines GEOC/baselines_web
#scp -r baselines GEOC/

