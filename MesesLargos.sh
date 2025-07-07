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

# Mapeo manual de nombres de meses a números
declare -A month_map=(
    [January]=1 [February]=2 [March]=3 [April]=4 [May]=5
    [June]=6 [July]=7 [August]=8 [September]=9 [October]=10
    [November]=11 [December]=12
)

# Analizar ambas fechas (inicio y fin) para detectar meses repetidos por año
declare -A month_years
while IFS='_' read -r start_date end_date; do
    for date in "$start_date" "$end_date"; do
        year=${date:0:4}
        month=${date:4:2}
        # Convertir mes con ceros a número normal (ej: 04 → 4)
        month_number=$((10#$month))
        # Obtener el nombre del mes en inglés
        month_name=$(date -d "2023-$month-01" +"%B" 2>/dev/null || echo "")
        
        if [ -n "$month_name" ] && [ -n "${month_map[$month_name]}" ]; then
            month_years[$month_name]+="$year "
        fi
    done
done < "$input_file"

# Identificar meses que aparecen en al menos 3 años únicos (puedes cambiar a 5 si quieres)
declare -A valid_months
for month_name in "${!month_years[@]}"; do
    years_present=(${month_years[$month_name]})
    unique_years=($(printf "%s\n" "${years_present[@]}" | sort -u))

    if [ ${#unique_years[@]} -ge 3 ]; then
        valid_months[$month_name]=${month_map[$month_name]}
    fi
done

# Crear el archivo de meses (mesecrear.txt)
echo "" > "$months_file"
for month_name in "${!valid_months[@]}"; do
    echo "$month_name ${valid_months[$month_name]}" >> "$months_file"
done

# Crear archivo de meses futuros (futuro.txt)
cp "$months_file" "$future_file"

echo "Archivos creados:"
echo "- $dates_longs_file (fechas de inicio)"
echo "- $months_file (meses frecuentes en al menos 3 años)"
echo "- $future_file (copia del archivo anterior)"
