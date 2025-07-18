#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="dates_longs_filter.txt"
OUTPUT_FILE="Longs_combination_all.txt"
OUTPUT_FILE_1="Longs_combination_longs.txt"
Chilescase=1

# Ensure the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file $INPUT_FILE not found!"
    exit 1
fi

line_count=$(wc -l < "$INPUT_FILE")
if [ "$line_count" -lt 100 ]; then
    INPUT_FILE="dates_longs.txt"
fi

# Ensure the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file $INPUT_FILE not found!"
    exit 1
fi

# Clear the output files
echo "Initializing output files..."
> "$OUTPUT_FILE"
> "$OUTPUT_FILE_1"

# Read dates into an array
dates=($(cat "$INPUT_FILE"))

# Function to calculate the difference in days between two dates
day_diff() {
    local start_date="$1"
    local end_date="$2"
    local start_epoch=$(date -d "${start_date:0:4}-${start_date:4:2}-${start_date:6:2}" +%s)
    local end_epoch=$(date -d "${end_date:0:4}-${end_date:4:2}-${end_date:6:2}" +%s)
    echo $(( (end_epoch - start_epoch) / 86400 ))
}

# Function to calculate month difference
month_diff() {
    local start_date="$1"
    local end_date="$2"
    local start_year=${start_date:0:4}
    local start_month=$((10#${start_date:4:2}))
    local end_year=${end_date:0:4}
    local end_month=$((10#${end_date:4:2}))
    echo $(((end_year - start_year) * 12 + (end_month - start_month)))
}

# Function to check if a date falls in the excluded months (June to September)
# Only applies the check if Chilescase == "y"
# Defaults Chilescase to "n" if undefined or invalid
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2}))  # Extract the month from date

    # Default Chilescase to "n" 0 if not "y"1 or "n" 0
    if [[ "$Chilescase" != 1 && "$Chilescase" != 0 ]]; then
        Chilescase=0
    fi

    if [[ "$Chilescase" == 1 ]]; then
        if (( month >= 6 && month <= 9 )); then
            return 0  # Excluded
        else
            return 1  # Not excluded
        fi
    else
        return 1  # Not excluded
    fi
}


# Generate connections for a specific start date
generate_connections_for_date() {
    local start_date="$1"
    local index="$2"
    local start_year="${start_date:0:4}"
    local start_month="${start_date:4:2}"

    declare -A already_connected_months
    local connection_count_same_month=0

    # Generate day-based connections (6 to 40 days apart)
    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        local diff_days=$(day_diff "$start_date" "$end_date")
        if ((diff_days > 6 && diff_days <= 40)); then
            echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"
        fi
    done

    # Generate month-based connections (3, 6, 9, 12, 15) and guarantee same-month-year-diff combos
    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        local diff_months=$(month_diff "$start_date" "$end_date")
        local end_month="${end_date:4:2}"
        local end_year="${end_date:0:4}"

        # Valid interval?
        if [[ "$diff_months" =~ ^(3|6|9|12|15)$ ]]; then
            pair_key="${start_date}_${end_date}"
            echo "$pair_key" >> "$OUTPUT_FILE"
            if ! is_excluded_month "$start_date" && ! is_excluded_month "$end_date"; then
                echo "$pair_key" >> "$OUTPUT_FILE_1"
            fi
        fi

        # Garantizar 2 conexiones entre mismos meses de distintos años
        if [[ "$start_month" == "$end_month" && "$start_year" -ne "$end_year" ]]; then
            combo_key="${start_date}_${end_date}"
            reverse_key="${end_date}_${start_date}"

            if [[ -z "${already_connected_months[$combo_key]}" && -z "${already_connected_months[$reverse_key]}" && $connection_count_same_month -lt 2 ]]; then
                echo "$combo_key" >> "$OUTPUT_FILE"
                if ! is_excluded_month "$start_date" && ! is_excluded_month "$end_date"; then
                    echo "$combo_key" >> "$OUTPUT_FILE_1"
                fi
                already_connected_months["$combo_key"]=1
                ((connection_count_same_month++))
            fi
        fi
    done
}

# Iterate over each date and generate connections
for ((i = 0; i < ${#dates[@]}; i++)); do
    generate_connections_for_date "${dates[i]}" "$i"
done

echo "✅ Todas las combinaciones escritas en $OUTPUT_FILE"
echo "✅ Combinaciones válidas de 3, 6, 9, 12, 15 meses (sin junio-septiembre) en $OUTPUT_FILE_1"
