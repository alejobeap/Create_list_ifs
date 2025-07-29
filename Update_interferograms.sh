#!/bin/bash

# File containing the list of dates (format: YYYYMMDD)
INPUT_FILE="Updated_list.txt"
OUTPUT_FILE="Update_combinations_IFS.txt"
Chilescase="n"  # Set to "y" to exclude June–September dates

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Input file $INPUT_FILE not found!"
    exit 1
fi

echo "🧹 Initializing output file..."
> "$OUTPUT_FILE"

# Leer fechas ordenadas
dates=($(sort "$INPUT_FILE"))

# Diferencia absoluta en días
day_diff() {
    local d1="$1"
    local d2="$2"
    local e1=$(date -d "${d1:0:4}-${d1:4:2}-${d1:6:2}" +%s)
    local e2=$(date -d "${d2:0:4}-${d2:4:2}-${d2:6:2}" +%s)
    local diff_sec=$((e2 - e1))
    echo $((diff_sec >= 0 ? diff_sec / 86400 : -diff_sec / 86400))
}

# Verificar si diferencia es aprox. 3, 6, 9 o 12 meses
is_approx_valid_month_diff() {
    local d1="$1"
    local d2="$2"
    local diff_days=$(day_diff "$d1" "$d2")
    local valid_ranges=(90 180 270 360)
    local tolerance=15

    for target in "${valid_ranges[@]}"; do
        if (( diff_days >= target - tolerance && diff_days <= target + tolerance )); then
            return 0
        fi
    done
    return 1
}

# Verificar si fecha cae en meses excluidos
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2}))

    if [[ "$Chilescase" != "y" && "$Chilescase" != "n" ]]; then
        Chilescase="n"
    fi

    if [[ "$Chilescase" == "y" ]]; then
        (( month >= 6 && month <= 9 )) && return 0 || return 1
    else
        return 1
    fi
}

# Generar combinaciones válidas para una fecha
generate_connections_for_date() {
    local start_date="$1"
    local index="$2"

    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        if ! is_excluded_month "$start_date" && ! is_excluded_month "$end_date"; then
            if is_approx_valid_month_diff "$start_date" "$end_date"; then
                echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"
            fi
        fi
    done
}

# Crear combinaciones por fecha
for ((i = 0; i < ${#dates[@]}; i++)); do
    generate_connections_for_date "${dates[i]}" "$i"
done

# Agregar combinaciones con las tres fechas siguientes (si cumplen)
for ((i = 0; i < ${#dates[@]} - 3; i++)); do
    d1="${dates[i]}"
    for offset in 1 2 3; do
        d2="${dates[i + offset]}"
        if ! is_excluded_month "$d1" && ! is_excluded_month "$d2"; then
            if is_approx_valid_month_diff "$d1" "$d2"; then
                echo "${d1}_${d2}" >> "$OUTPUT_FILE"
            fi
        fi
    done
done

# Quitar duplicados
sort -u "$OUTPUT_FILE" -o "$OUTPUT_FILE"

# Extraer años únicos
years=($(cut -c1-4 "$INPUT_FILE" | sort -u))

# Cargar combinaciones existentes
mapfile -t existing_combinations < <(cat "$OUTPUT_FILE")

exists_connection_between_years() {
    local year1=$1
    local year2=$2
    for combo in "${existing_combinations[@]}"; do
        local y1=${combo:0:4}
        local y2=${combo:9:4}
        if { [[ "$y1" == "$year1" && "$y2" == "$year2" ]] || [[ "$y1" == "$year2" && "$y2" == "$year1" ]]; }; then
            return 0
        fi
    done
    return 1
}

force_connections_between_years() {
    local year1=$1
    local year2=$2
    local count=0
    local dates_year1=()
    local dates_year2=()

    for d in "${dates[@]}"; do
        [[ "${d:0:4}" == "$year1" ]] && dates_year1+=("$d")
        [[ "${d:0:4}" == "$year2" ]] && dates_year2+=("$d")
    done

    for d1 in "${dates_year1[@]}"; do
        is_excluded_month "$d1" && continue
        for d2 in "${dates_year2[@]}"; do
            is_excluded_month "$d2" && continue
            if is_approx_valid_month_diff "$d1" "$d2"; then
                combo="${d1}_${d2}"
                combo_rev="${d2}_${d1}"
                if ! grep -q -e "^$combo$" -e "^$combo_rev$" "$OUTPUT_FILE"; then
                    echo "$combo" >> "$OUTPUT_FILE"
                    ((count++))
                    if [[ $count -ge 2 ]]; then return; fi
                fi
            fi
        done
    done
}

for ((i = 0; i < ${#years[@]} - 1; i++)); do
    y1=${years[i]}
    y2=${years[i + 1]}
    if ! exists_connection_between_years "$y1" "$y2"; then
        echo "⚠️ Forzando conexiones entre $y1 y $y2..."
        force_connections_between_years "$y1" "$y2"
    fi
done

# Refrescar combinaciones
mapfile -t existing_combinations < <(sort -u "$OUTPUT_FILE")

force_connections_per_date_to_next_year() {
    local date="$1"
    local year=${date:0:4}
    local next_year=$((year + 1))
    local connections_count=0
    declare -A connected_set

    for combo in "${existing_combinations[@]}"; do
        if [[ "$combo" == ${date}_* ]]; then
            connected_date=${combo#*_}
        elif [[ "$combo" == *_${date} ]]; then
            connected_date=${combo%_*}
        else
            continue
        fi
        [[ "${connected_date:0:4}" == "$next_year" ]] && ((connections_count++)) && connected_set["$connected_date"]=1
    done

    if (( connections_count < 2 )); then
        for d in "${dates[@]}"; do
            [[ "${d:0:4}" == "$next_year" ]] || continue
            is_excluded_month "$d" && continue
            [[ -z "${connected_set[$d]}" ]] || continue
            if is_approx_valid_month_diff "$date" "$d"; then
                echo "${date}_${d}" >> "$OUTPUT_FILE"
                ((connections_count++))
                connected_set["$d"]=1
                ((connections_count >= 2)) && break
            fi
        done
        if (( connections_count < 2 )); then
            echo "⚠️ No se lograron 2 conexiones para $date con $next_year."
        fi
    fi
}

for date in "${dates[@]}"; do
    force_connections_per_date_to_next_year "$date"
done

line_count=$(wc -l < "$OUTPUT_FILE")
echo "📄 Total combinaciones generadas: $line_count"
echo "✅ Script finalizado."
