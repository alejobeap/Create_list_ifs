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

# Obtener el primer y último año del archivo
first_year=$(head -n 1 "$dates_longs_file" | cut -c1-4)
last_year=$(tail -n 1 "$dates_longs_file" | cut -c1-4)

# Calcular años totales (incluyendo ambos extremos)
total_years=$((last_year - first_year))


# Si el usuario pasa un argumento, usarlo como threshold
if [[ -n "$1" && "$1" =~ ^[0-9]+$ ]]; then
    threshold="$1"
else
    # Calcular threshold dinámicamente
    #if (( total_years <= 9 )); then
    #    threshold=$(( total_years * 90 / 100 ))
    #else
    #    threshold=$(( total_years * 70 / 100 ))
    #fi

    if (( total_years >= 10 )); then
        threshold=$(( total_years - 1 ))
    else
        threshold=$(( total_years - 3 ))
    fi
    
    # Asegurar que el umbral sea al menos 1
    if [ "$threshold" -lt 1 ]; then
        threshold=1
    fi
fi

echo "Rango de años: $first_year-$last_year ($total_years años)"
echo "Umbral mínimo de años por mes: $threshold"

# Usar threshold en lugar del 8 fijo
for month in "${!month_count[@]}"; do
    if [ "${month_count[$month]}" -ge "$threshold" ]; then
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
#grep -E "^....(${months_regex})" "$dates_longs_file" > "$dates_longs_filter_file"

# Filtrar dates_longs_file dejando solo líneas en formato YYYYMMDD cuyo mes esté en la lista
grep -E "^[0-9]{4}(${months_regex})[0-9]{2}$" "$dates_longs_file" > "$dates_longs_filter_file"

# Añadir las últimas 10 entradas del directorio RSLC al dates_longs_filter_file, sin duplicados
ls RSLC -1 | tail -n 6 >> "$dates_longs_filter_file"

# Eliminar duplicados y ordenar
sort -u "$dates_longs_filter_file" -o "$dates_longs_filter_file"
