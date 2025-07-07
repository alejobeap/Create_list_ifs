#!/bin/bash

# Paso 1: Verificar si listarslc.txt existe y eliminarlo si es necesario
if [ -f "listarslc.txt" ]; then
  echo "Eliminando archivo existente: listarslc.txt"
  rm listarslc.txt
fi


# Step 1: Create the list of RSLC files
ls RSLC -1 > listarslc.txt


# Read each RSLC date from the list
while IFS= read -r date; do
    # Trim whitespace or hidden characters from the date
    date=$(echo "$date" | tr -d '\r' | xargs)

    echo "Processing date: $date"

    # Check if both required files exist
    if [[ -f "RSLC/${date}/${date}.rslc.mli" && -f "RSLC/${date}/${date}.rslc.mli.par" ]]; then
        echo "Files for $date already exist. Skipping..."
    else
        echo "Files for $date are missing. Generating with multilookRSLC..."
        multilookRSLC "$date" 7 2 1
    fi
done < listarslc.txt

echo "Processing complete."
