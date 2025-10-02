#!/bin/bash

# --- Archivos ---
input_file="filtered_IFS_average_cc_value.txt"
months_file="mesecrear.txt"
dates_longs_file="dates_longs.txt"
dates_longs_filter_file="dates_longs_filter.txt"
output_file="Longs_combination_longs.txt"

# --- Limpieza previa ---
[ -f "$months_file" ] && rm "$months_file"
[ -f "$dates_longs_filter_file" ] && rm "$dates_longs_filter_file"
> "$output_file"

# --- Crear lista de fechas base ---
awk -F'_' '{print $1}' "$input_file" | sort -u > "$dates_longs_file"

# --- Calcular meses por año ---
declare -A month_years month_count
while read -r line; do
    year="${line:0:4}"
    month="${line:4:2}"
    key="$month:$year"
    month_years["$key"]=1
done < "$dates_longs_file"

for key in "${!month_years[@]}"; do
    month="${key%%:*}"
    month_count["$month"]=$(( ${month_count["$month"]:-0} + 1 ))
done

first_year=$(head -n 1 "$dates_longs_file" | cut -c1-4)
last_year=$(tail -n 1 "$dates_longs_file" | cut -c1-4)
total_years=$((last_year - first_year + 1))

# --- Threshold inicial ---
threshold=$(( total_years >= 10 ? total_years - 1 : total_years - 3 ))
(( threshold < 1 )) && threshold=1

echo "Rango de años: $first_year-$last_year ($total_years años)"
echo "Threshold inicial: $threshold"

# --- Funciones ---
month_diff() {
    local start="$1" end="$2"
    local sy=${start:0:4} sm=$((10#${start:4:2}))
    local ey=${end:0:4} em=$((10#${end:4:2}))
    echo $(((ey - sy) * 12 + (em - sm)))
}

is_valid_diff() {
    case "$1" in
        6|9|12|15) return 0 ;;
        *) return 1 ;;
    esac
}

generate_combinations() {
    local threshold="$1"
    > "$months_file"
    > "$dates_longs_filter_file"
    > "$output_file"

    # --- Filtrar meses ---
    for month in "${!month_count[@]}"; do
        if [ "${month_count[$month]}" -ge "$threshold" ]; then
            echo "$month"
        fi
    done | sort > "$months_file"

    mapfile -t valid_months < "$months_file"
    months_regex=$(IFS='|'; echo "${valid_months[*]}")

    grep -E "^[0-9]{4}(${months_regex})[0-9]{2}$" "$dates_longs_file" > "$dates_longs_filter_file"

    # Añadir últimos RSLC si existen
    if [ -d RSLC ]; then
        ls RSLC -1 | grep -E "^[0-9]{8}$" | tail -n 6 >> "$dates_longs_filter_file"
    fi

    sort -u "$dates_longs_filter_file" -o "$dates_longs_filter_file"
    dates=($(sort "$dates_longs_filter_file"))

    # --- Generar combinaciones válidas ---
    for ((i=0; i<${#dates[@]}; i++)); do
        d1=${dates[i]}
        for ((j=i+1; j<${#dates[@]}; j++)); do
            d2=${dates[j]}
            diff=$(month_diff "$d1" "$d2")
            if is_valid_diff "$diff"; then
                echo "${d1}_${d2}" >> "$output_file"
            fi
        done
    done

    sort -u "$output_file" -o "$output_file"
    wc -l < "$output_file"
}

# --- Bucle de ajuste automático ---
min_threshold=1
max_threshold=$total_years
line_count=$(generate_combinations "$threshold")

echo "Combinaciones iniciales: $line_count"

while true; do
    if (( line_count > 500 )); then
        ((threshold++))
        (( threshold > max_threshold )) && break
        echo "Demasiadas combinaciones ($line_count), subiendo threshold a $threshold..."
        line_count=$(generate_combinations "$threshold")

    elif (( line_count < 100 )); then
        ((threshold--))
        (( threshold < min_threshold )) && break
        echo "Muy pocas combinaciones ($line_count), bajando threshold a $threshold..."
        line_count=$(generate_combinations "$threshold")

    else
        echo " Número óptimo de combinaciones: $line_count (Threshold=$threshold)"
        break
    fi

    # Caso especial: 0 combinaciones → sigue bajando hasta encontrar algo
    if (( line_count == 0 && threshold > min_threshold )); then
        ((threshold--))
        echo " Cero combinaciones, probando con threshold=$threshold..."
        line_count=$(generate_combinations "$threshold")
    fi
done

echo "Archivo final: $output_file con $line_count combinaciones"
