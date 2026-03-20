#!/bin/bash
#P.Espin2025
# --- Generar lista de archivos ---
ls -1 RSLC > listRSLC.txt

INPUT_FILE="listRSLC.txt"
OUTPUT_FILE="combinations_12m.txt"

# Función para calcular la diferencia en meses entre dos fechas YYYYMMDD
month_diff() {
    local start_date="$1"
    local end_date="$2"
    local start_year=${start_date:0:4}
    local start_month=$((10#${start_date:4:2}))
    local end_year=${end_date:0:4}
    local end_month=$((10#${end_date:4:2}))
    echo $(((end_year - start_year) * 12 + (end_month - start_month)))
}

# Verificar que el archivo exista
if [ ! -f "$INPUT_FILE" ]; then
    echo "Archivo $INPUT_FILE no encontrado!"
    exit 1
fi

# Limpiar archivo de salida
> "$OUTPUT_FILE"

# Leer todas las líneas en un array
mapfile -t lines < "$INPUT_FILE"

# Generar combinaciones
for ((i=0; i<${#lines[@]}; i++)); do
    date1="${lines[i]}"
    
    for ((j=i+1; j<${#lines[@]}; j++)); do
        date2="${lines[j]}"
        diff=$(month_diff "$date1" "$date2")
        
        # Si la diferencia es aproximadamente 12 meses (11-13)
        if (( diff >= 11 && diff <= 13 )); then
            echo "${date1}_${date2}" >> "$OUTPUT_FILE"
        fi
    done
done

# Mostrar resumen
echo "Número total de combinaciones generadas: $(wc -l < "$OUTPUT_FILE")"
