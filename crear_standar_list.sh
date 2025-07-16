#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="listarslc.txt"
OUTPUT_FILE_2="standar_list.txt"
Chilescase = "y"

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


# Function to check if a date falls in the excluded months (June to September)
# Only applies the check if Chilescase == "y"
# Returns 0 if excluded, 1 if not excluded
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2}))  # Extract month, force base 10 to avoid leading zeros issues

    if [[ "$Chilescase" == "y" ]]; then
        if (( month >= 6 && month <= 9 )); then
            return 0  # Excluded
        else
            return 1  # Not excluded
        fi
    else
        return 1  # Not excluded if Chilescase != "y"
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
        

        echo "${date1}_${date2}" >> "$OUTPUT_FILE_2"
    
    done
done

line_count=$(wc -l < "$OUTPUT_FILE_2")
echo "📄 Número total de combinaciones generadas: $line_count"
