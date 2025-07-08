#!/bin/bash

# Check if the GEOC directory exists
if [ ! -d "GEOC" ]; then
  echo "Error: Directory 'GEOC' does not exist."
  exit 1
fi



# Step 3: Iterate over the files listed in listaifs.txt
while IFS= read -r file; do
  echo "Processing file: $file"
      sbatch --qos=high --output=sbatch_logs/$file.out --error=sbatch_logs/$file.err --job-name=$file -n 8 --time=23:59:00 --mem=65536 -p comet --account=comet_lics --partition=standard --wrap="unwrap_geo.sh `cat sourceframe.txt` $file"
  
done < listaunwpng.txt

echo "Processing completed."
