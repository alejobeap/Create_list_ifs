#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="dates_longs_filter.txt"
OUTPUT_FILE="Longs_combination_all.txt"
OUTPUT_FILE_1="Longs_combination_longs.txt"

# Ensure the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file $INPUT_FILE not found!"
    exit 1
fi

# Clear the output file
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
    local start_month=$((10#${start_date:4:2})) # Strip leading zero
    local end_year=${end_date:0:4}
    local end_month=$((10#${end_date:4:2}))   # Strip leading zero
    echo $(((end_year - start_year) * 12 + (end_month - start_month)))
}

# Function to check if a date falls in the excluded months (June to September)
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2})) # Strip leading zero
    if ((month >= 6 && month <= 9)); then
        return 0 # Excluded
    else
        return 1 # Not excluded
    fi
}

# Generate connections for a specific start date
generate_connections_for_date() {
    local start_date="$1"
    local index="$2"

    # Generate day-based connections (6 to 40 days apart)
    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        local diff_days=$(day_diff "$start_date" "$end_date")
        if ((diff_days > 6 && diff_days <= 40)); then
            echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"
        fi
    done

    # Generate month-based connections for intervals: 3, 6, 9, 12, 15
    for interval in 3 6 9 12 15; do
        for ((j = index + 1; j < ${#dates[@]}; j++)); do
            local end_date="${dates[j]}"
            local diff_months=$(month_diff "$start_date" "$end_date")

            if ((diff_months == interval)); then
                echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"

                # Only include in longs file if neither date is in an excluded month
                if ! is_excluded_month "$start_date" && ! is_excluded_month "$end_date"; then
                    echo "${start_date}_${end_date}" >> "$OUTPUT_FILE_1"
                fi
            fi
        done
    done
}

# Iterate over each date and generate connections
for ((i = 0; i < ${#dates[@]}; i++)); do
    generate_connections_for_date "${dates[i]}" "$i"
done

echo "✅ Todas las combinaciones escritas en $OUTPUT_FILE"
echo "✅ Combinaciones válidas de 3, 6, 9, 12, 15 meses (sin junio-septiembre) en $OUTPUT_FILE_1"
