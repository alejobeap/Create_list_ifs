#!/bin/bash

# Script to create a 'log' directory and run the LiCSAR_03_mk_ifgs.py script with specified arguments
tracks=$(basename "$(pwd)")
name=$(basename "$(dirname "$(pwd)")")

# Create the 'log' directory
mkdir -p log
mv GEOC GEOC_shorts
mkdir -p GEOC


## Crear jobs
sbatch --qos=high --output=LONGS_MKIFS_${name}_${tracks}.out --error=LONGS_MKIFS_${name}_${tracks}.err --job-name=LONGS_MKIFS_${name}_${tracks} -n 8 --time=23:59:00 --mem=65536 -p comet --account=comet_lics --partition=standard --wrap="LiCSAR_03_mk_ifgs.py -d . -r 7 -a 2 -c 0 -i Longs_combination_longs.txt"

# Run the LiCSAR_03_mk_ifgs.py script with the given arguments
#LiCSAR_03_mk_ifgs.py -d . -r 7 -a 2 -c 0 -i filtered_date_pairs.txt

# Notify the user of completion
echo "Log directory created and LiCSAR_03_mk_ifgs.py executed successfully."



