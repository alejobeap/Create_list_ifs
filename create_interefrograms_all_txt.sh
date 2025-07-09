#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="listarslc.txt"
OUTPUT_FILE="combination_all.txt"
OUTPUT_FILE_1="combination_longs.txt"
OUTPUT_FILE_2="combination_shorts.txt"

# Step 3: Remove listarslc.txt if it exists
[ -f listarslc.txt ] && rm listarslc.txt

# Step 4: List files in RSLC directory and save to listarslc.txt
ls RSLC -1 >> listarslc.txt

# Ensure the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file $INPUT_FILE not found!"
    exit 1
fi

# Clear the output file
if [ -f "$OUTPUT_FILE" ]; then
    echo "Output file $OUTPUT_FILE found. Erasing!"
    > "$OUTPUT_FILE"
else
    > "$OUTPUT_FILE"
fi


# Clear the output file
if [ -f "$OUTPUT_FILE_1" ]; then
    echo "Output file $OUTPUT_FILE_1 found. Erasing!"
    > "$OUTPUT_FILE_1"
else
    > "$OUTPUT_FILE_1"
fi

# Clear the output file
if [ -f "$OUTPUT_FILE_2" ]; then
    echo "Output file $OUTPUT_FILE_2 found. Erasing!"
    > "$OUTPUT_FILE_2"
else
    > "$OUTPUT_FILE_2"
fi


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

# Function to check if a date falls in the excluded months (May to September)
is_excluded_month() {
    local date="$1"
    local month=$((10#${date:4:2})) # Strip leading zero
    if ((month >= 5 && month <= 9)); then
        return 0 # Excluded
    else
        return 1 # Not excluded
    fi
}

# Generate connections for a specific start date
generate_connections_for_date() {
    local start_date="$1"
    local index="$2"

    # Generate day-based connections
    for ((j = index + 1; j < ${#dates[@]}; j++)); do
        local end_date="${dates[j]}"
        local diff_days=$(day_diff "$start_date" "$end_date")
        local diff_months=$(month_diff "$start_date" "$end_date")
        if ((diff_days > 6 && diff_days <= 40)); then
            echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"
            #echo "${start_date}_${end_date}" >> "$OUTPUT_FILE_2"
        fi
    done

    # Generate month-based connections
    for interval in 12 9 6 3; do
        for ((j = index + 1; j < ${#dates[@]}; j++)); do
            local end_date="${dates[j]}"
            local diff_months=$(month_diff "$start_date" "$end_date")
            if is_excluded_month "$start_date" || is_excluded_month "$end_date"; then
                continue
            fi
            if ((diff_months == interval)); then
                echo "${start_date}_${end_date}" >> "$OUTPUT_FILE"
                echo "${start_date}_${end_date}" >> "$OUTPUT_FILE_1"

            elif ((diff_months > interval)); then
                break
            fi
        done
    done
}



# Iterate over each date and generate connections
for ((i = 0; i < ${#dates[@]}; i++)); do
    generate_connections_for_date "${dates[i]}" "$i"
done

echo "Combinations written to $OUTPUT_FILE. Please check for a maximum of 12 months difference."


# Read all lines into an array
mapfile -t lines < "$INPUT_FILE"

# Loop over lines and create combinations (up to next 4 lines)
for ((i=0; i<${#lines[@]}; i++)); do
    for ((j=i+1; j<i+3 && j<${#lines[@]}; j++)); do
        echo "${lines[i]}_${lines[j]}" >> "$OUTPUT_FILE_2"
    done
done

echo "Short combinations written to $OUTPUT_FILE_2"
