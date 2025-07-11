#!/bin/bash

# File containing the list of dates (one date per line in YYYYMMDD format)
INPUT_FILE="listarslc.txt"
OUTPUT_FILE_2="standar_list.txt"


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

# Loop over lines and create combinations (up to next 4 lines)
for ((i=0; i<${#lines[@]}; i++)); do
    for ((j=i+2; j<i+4 && j<${#lines[@]}; j++)); do
        echo "${lines[i]}_${lines[j]}" >> "$OUTPUT_FILE_2"
    done
done


line_count=$(wc -l < "$OUTPUT_FILE_2")
echo "📄 Número total de combinaciones generadas: $line_count"
