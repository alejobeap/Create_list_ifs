#!/bin/bash

#if [ -d "GEOC" ]; then
#    mv GEOC GEOC_longs
#else
#    mkdir GEOC
#fi
scp -r GEOC/geo/* GEOC/
# Define file names
file1="standar_list.txt"
file2="Longs_combination_longs.txt"
output="IFSforLiCSBAS.txt"

# Check if both input files exist
if [[ ! -f $file1 || ! -f $file2 ]]; then
    echo "One or both input files do not exist."
    exit 1
fi

# Clear the output file
> "$output"

# Combine the files and sort the result
cat "$file1" "$file2" | sort > "$output"

# Check if the output file was created
if [[ -f $output ]]; then
    echo "Files have been successfully combined and sorted into $output."
else
    echo "Failed to create the output file."
fi

parent_dir=$(basename "$(dirname "$(pwd)")")
current_dir=$(basename "$(pwd)")


echo "framebatch_gapfill.sh -l -I /work/scratch-pw3/licsar/alejobea/batchdir/${parent_dir}/${current_dir}/IFSforLiCSBAS.txt 5 480 7 2"

framebatch_gapfill.sh -l -I /work/scratch-pw3/licsar/alejobea/batchdir/${parent_dir}/${current_dir}/IFSforLiCSBAS.txt 5 480 7 2
