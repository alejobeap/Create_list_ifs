#!/bin/bash

# Archivos de entrada y salida
input_file="filtered_IFS_average_cc_value.txt"
months_file="mesecrear.txt"
future_file="futuro.txt"
dates_longs_file="dates_longs.txt"

# Verificar si los archivos existen y borrarlos si es necesario
[ -f "$months_file" ] && rm "$months_file"
[ -f "$future_file" ] && rm "$future_file"
# Nota: dates_longs.txt no se borra porque puede ser útil conservarlo

# Crear dates_longs.txt con solo la fecha antes del '_'
awk -F'_' '{print $1}' "$input_file" | sort -u > "$dates_longs_file"

# Procesar dates_longs.txt para encontrar los meses que se repiten en al menos 5 años
declare -A month_years

while read -r line; do
    year="${line:0:4}"
    month="${line:4:2}"
    key="$month:$year"
    month_years["$key"]=1
done < "$dates_longs_file"

# Contar cuántos años únicos tiene cada mes
declare -A month_count

for key in "${!month_years[@]}"; do
    month="${key%%:*}"
    month_count["$month"]=$((month_count["$month"] + 1))
done

# Escribir a mesecrear.txt los meses que aparecen en al menos 5 años
for month in "${!month_count[@]}"; do
    if [ "${month_count[$month]}" -ge 8 ]; then
       echo "$month"
    fi
done | sort > "$months_file"


# Filtrar dates_longs.txt para conservar solo los meses presentes en mesecrear.txt
dates_longs_filter_file="dates_longs_filter.txt"
[ -f "$dates_longs_filter_file" ] && rm "$dates_longs_filter_file"

# Leer meses válidos en un array
mapfile -t valid_months < "$months_file"

# Crear expresión regular para grep (por ejemplo: 01|02|03)
months_regex=$(IFS='|'; echo "${valid_months[*]}")

# Filtrar fechas cuyo mes esté en los meses válidos
grep -E "^....(${months_regex})" "$dates_longs_file" > "$dates_longs_filter_file"

# Añadir las últimas 10 entradas del directorio RSLC al dates_longs_filter_file, sin duplicados
ls RSLC -1 | tail -n 10 >> "$dates_longs_filter_file"

# Eliminar duplicados y ordenar
sort -u "$dates_longs_filter_file" -o "$dates_longs_filter_file"
