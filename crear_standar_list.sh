#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="listarslc.txt"
OUTPUT_FILE_2="standar_list.txt"

# Function to calculate difference in months
month_diff() {
    local start_date="$1"
    local end_date="$2"
    local start_year=${start_date:0:4}
    local start_month=$((10#${start_date:4:2}))
    local end_year=${end_date:0:4}
    local end_month=$((10#${end_date:4:2}))
    echo $(((end_year - start_year) * 12 + (end_month - start_month)))
}

# Function to check if the month difference is valid
is_valid_diff_months() {
    local diff="$1"
    [[ "$diff" -eq 6 || "$diff" -eq 9 || "$diff" -eq 12 || "$diff" -eq 15 ]]
}

# Function to exclude dates in June through September
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2}))
    if ((month >= 6 && month <= 9)); then
        return 0  # Exclude
    else
        return 1  # Allow
    fi
}

# Ensure the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file $INPUT_FILE not found!"
    exit 1
fi

# Clear the output file
if [ -f "$OUTPUT_FILE_2" ]; then
    echo "Output file $OUTPUT_FILE_2 found. Erasing!"
    > "$OUTPUT_FILE_2"
else
    > "$OUTPUT_FILE_2"
fi

# Read all lines into an array
mapfile -t lines < "$INPUT_FILE"

# Loop over lines and create valid combinations
for ((i=0; i<${#lines[@]}; i++)); do
    for ((j=i+1; j<i+4 && j<${#lines[@]}; j++)); do
        date1="${lines[i]}"
        date2="${lines[j]}"
        
        # Skip if either date is in excluded months
        if is_excluded_month "$date1" || is_excluded_month "$date2"; then
            continue
        fi
        
        # Calculate month difference and validate it
        diff=$(month_diff "$date1" "$date2")
        if is_valid_diff_months "$diff"; then
            echo "${date1}_${date2}" >> "$OUTPUT_FILE_2"
        fi
    done
done

line_count=$(wc -l < "$OUTPUT_FILE_2")
echo "📄 Número total de combinaciones generadas: $line_count"
