#!/bin/bash

# File containing the list of dates (format: YYYYMMDD)
INPUT_FILE="dates_longs_filter.txt"
OUTPUT_FILE="Longs_combination_longs.txt"
Chilescase="n"


if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Input file $INPUT_FILE not found!"
    exit 1
fi

echo "🧹 Initializing output file..."
> "$OUTPUT_FILE"

# Leer fechas ordenadas
dates=($(sort "$INPUT_FILE"))

# Función para diferencia en meses
month_diff() {
    local start_date="$1"
    local end_date="$2"
    local start_year=${start_date:0:4}
    local start_month=$((10#${start_date:4:2}))
    local end_year=${end_date:0:4}
    local end_month=$((10#${end_date:4:2}))
    echo $(((end_year - start_year) * 12 + (end_month - start_month)))
}

is_valid_diff_months() {
    local diff="$1"
    [[ "$diff" -eq 6 || "$diff" -eq 9 || "$diff" -eq 12 || "$diff" -eq 15 ]]
}


# Meses adicionales para los dos últimos años
extra_months=(2 3 4 5 6)

# Obtener los dos últimos años ordenados
sorted_years=($(cut -c1-4 "$INPUT_FILE" | sort -u))
last_year=${sorted_years[-1]}
second_last_year=${sorted_years[-2]}

# Filtrar fechas de los dos últimos años
dates_last_two_years=()
for d in "${dates[@]}"; do
    y=${d:0:4}
    if [[ "$y" == "$last_year" || "$y" == "$second_last_year" ]]; then
        dates_last_two_years+=("$d")
    fi
done

# Función para generar combinaciones con los meses extra para los dos últimos años
generate_extra_month_combinations() {
    local dates_arr=("$@")
    declare -A combinations_added

    for ((i=0; i < ${#dates_arr[@]}; i++)); do
        local start_date="${dates_arr[i]}"
        for ((j = i + 1; j < ${#dates_arr[@]}; j++)); do
            local end_date="${dates_arr[j]}"
            local diff_months=$(month_diff "$start_date" "$end_date")

            for m in "${extra_months[@]}"; do
                if [[ "$diff_months" -eq "$m" ]]; then
                    local combo_key="${start_date}_${end_date}"
                    local combo_key_rev="${end_date}_${start_date}"
                    # Evitar duplicados
                    if [[ -z "${combinations_added[$combo_key]}" && -z "${combinations_added[$combo_key_rev]}" ]]; then
                        echo "$combo_key" >> "$OUTPUT_FILE"
                        combinations_added["$combo_key"]=1
                    fi
                fi
            done
        done
    done
}


# Function to check if a date falls in the excluded months (June to September)
# Only applies the check if Chilescase == "y"
# Defaults Chilescase to "n" if undefined or invalid
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2}))  # Extract the month from date

    # Default Chilescase to "n" if not "y" or "n"
    if [[ "$Chilescase" != "y" && "$Chilescase" != "n" ]]; then
        Chilescase="n"
    fi

    if [[ "$Chilescase" == "y" ]]; then
        if (( month >= 6 && month <= 9 )); then
            return 0  # Excluded
        else
            return 1  # Not excluded
        fi
    else
        return 1  # Not excluded
    fi
}

generate_connections_for_date() {
    local start_date="$1"
    local index="$2"
    local start_year="${start_date:0:4}"
    local start_month="${start_date:4:2}"

    declare -A already_connected_months
    local connection_count_same_month=0

    # Contadores para cada intervalo
    declare -A connections_per_interval=(
        ["6"]=0
        ["9"]=0
        ["12"]=0
        ["15"]=0
    )

    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        local diff_months=$(month_diff "$start_date" "$end_date")
        local end_month="${end_date:4:2}"
        local end_year="${end_date:0:4}"

        if ! is_excluded_month "$start_date" && ! is_excluded_month "$end_date"; then
            if is_valid_diff_months "$diff_months"; then
                # Limitar máximo 2 conexiones por intervalo
                if [[ ${connections_per_interval[$diff_months]} -lt 2 ]]; then
                    pair_key="${start_date}_${end_date}"
                    echo "$pair_key" >> "$OUTPUT_FILE"
                    ((connections_per_interval[$diff_months]++))
                fi
                continue
            fi

            if [[ "$start_month" == "$end_month" && "$start_year" -ne "$end_year" ]]; then
                if is_valid_diff_months "$diff_months"; then
                    combo_key="${start_date}_${end_date}"
                    reverse_key="${end_date}_${start_date}"

                    if [[ -z "${already_connected_months[$combo_key]}" && -z "${already_connected_months[$reverse_key]}" && $connection_count_same_month -lt 2 ]]; then
                        echo "$combo_key" >> "$OUTPUT_FILE"
                        already_connected_months["$combo_key"]=1
                        ((connection_count_same_month++))
                    fi
                fi
            fi
        fi
    done
}

# Generar conexiones normales
for ((i = 0; i < ${#dates[@]}; i++)); do
    generate_connections_for_date "${dates[i]}" "$i"
done

# Extraer años únicos
years=($(cut -c1-4 "$INPUT_FILE" | sort -u))

# Leer combinaciones ya generadas para búsqueda rápida
mapfile -t existing_combinations < <(sort -u "$OUTPUT_FILE")

exists_connection_between_years() {
    local year1=$1
    local year2=$2
    for combo in "${existing_combinations[@]}"; do
        local start_year=${combo:0:4}
        local end_year=${combo:9:4}
        if { [[ "$start_year" == "$year1" && "$end_year" == "$year2" ]] || [[ "$start_year" == "$year2" && "$end_year" == "$year1" ]]; }; then
            return 0
        fi
    done
    return 1
}

# Función para calcular diferencia en días absoluta
day_diff() {
    local d1="$1"
    local d2="$2"
    local e1=$(date -d "${d1:0:4}-${d1:4:2}-${d1:6:2}" +%s)
    local e2=$(date -d "${d2:0:4}-${d2:4:2}-${d2:6:2}" +%s)
    local diff_sec=$((e2 - e1))
    echo $((diff_sec >= 0 ? diff_sec / 86400 : -diff_sec / 86400))
}

force_connections_between_years() {
    local year1=$1
    local year2=$2
    local count=0

    local dates_year1=()
    local dates_year2=()
    for d in "${dates[@]}"; do
        local y=${d:0:4}
        if [[ "$y" == "$year1" ]]; then
            dates_year1+=("$d")
        elif [[ "$y" == "$year2" ]]; then
            dates_year2+=("$d")
        fi
    done

    # Sin filtro estricto, conectar máximo 2 combos
    for d1 in "${dates_year1[@]}"; do
        if is_excluded_month "$d1"; then
            continue
        fi
        for d2 in "${dates_year2[@]}"; do
            if is_excluded_month "$d2"; then
                continue
            fi

            local combo="${d1}_${d2}"
            local combo_rev="${d2}_${d1}"
            if ! grep -q -e "^$combo$" -e "^$combo_rev$" "$OUTPUT_FILE"; then
                echo "$combo" >> "$OUTPUT_FILE"
                ((count++))
                if [[ $count -ge 2 ]]; then
                    return
                fi
            fi
        done
    done
}

# Verificar y forzar conexiones entre años consecutivos
for ((i = 0; i < ${#years[@]} - 1; i++)); do
    y1=${years[i]}
    y2=${years[i+1]}
    if ! exists_connection_between_years "$y1" "$y2"; then
        echo "⚠️ No existe conexión entre $y1 y $y2, forzando combinaciones..."
        force_connections_between_years "$y1" "$y2"
    fi
done

# Recargar combinaciones después de generar conexiones normales
mapfile -t existing_combinations < <(sort -u "$OUTPUT_FILE")

# Forzar mínimo 2 conexiones de cada fecha con fechas del siguiente año
force_connections_per_date_to_next_year() {
    local date="$1"
    local year=${date:0:4}
    local next_year=$((year + 1))
    local connections_count=0

    # Contar conexiones actuales hacia fechas del siguiente año
    for combo in "${existing_combinations[@]}"; do
        if [[ "$combo" == ${date}_* ]]; then
            local connected_date=${combo#*_}
            if [[ "${connected_date:0:4}" == "$next_year" ]]; then
                ((connections_count++))
            fi
        elif [[ "$combo" == *_${date} ]]; then
            local connected_date=${combo%_*}
            if [[ "${connected_date:0:4}" == "$next_year" ]]; then
                ((connections_count++))
            fi
        fi
    done

    if (( connections_count < 2 )); then
        local candidates=()
        # Filtrar fechas del siguiente año que no están en meses excluidos
        for d in "${dates[@]}"; do
            if [[ "${d:0:4}" == "$next_year" ]] && ! is_excluded_month "$d"; then
                candidates+=("$d")
            fi
        done

        # Para no repetir, armar un set de conexiones actuales a ese siguiente año
        declare -A connected_set
        for combo in "${existing_combinations[@]}"; do
            if [[ "$combo" == ${date}_* ]]; then
                local connected_date=${combo#*_}
                if [[ "${connected_date:0:4}" == "$next_year" ]]; then
                    connected_set["$connected_date"]=1
                fi
            elif [[ "$combo" == *_${date} ]]; then
                local connected_date=${combo%_*}
                if [[ "${connected_date:0:4}" == "$next_year" ]]; then
                    connected_set["$connected_date"]=1
                fi
            fi
        done

        # Agregar nuevas conexiones hasta completar 2
        for candidate in "${candidates[@]}"; do
            if [[ -z "${connected_set[$candidate]}" ]]; then
                local combo="${date}_${candidate}"
                local combo_rev="${candidate}_${date}"
                if ! grep -q -e "^$combo$" -e "^$combo_rev$" "$OUTPUT_FILE"; then
                    echo "$combo" >> "$OUTPUT_FILE"
                    ((connections_count++))
                    connected_set["$candidate"]=1
                    #echo "🔗 Agregado forzado: $combo"
                    if (( connections_count >= 2 )); then
                        break
                    fi
                fi
            fi
        done

        if (( connections_count < 2 )); then
            echo "⚠️ No se pudo completar 2 conexiones para $date, sólo se agregaron $connections_count."
        fi
    fi
}

for date in "${dates[@]}"; do
    force_connections_per_date_to_next_year "$date"
done


# Llamar la función para los dos últimos años
generate_extra_month_combinations "${dates_last_two_years[@]}"

line_count=$(wc -l < "$OUTPUT_FILE")
echo "📄 Número total de combinaciones generadas: $line_count"

echo "✅ Script finalizado."
