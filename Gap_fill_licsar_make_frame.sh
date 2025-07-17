#!/bin/bash

INPUT_FILE="listarslc.txt"
OUTPUT_FILE_1="run_gaps.sh"
OUTPUT_FILE_2="nla_request_lics.sh"

# 1. Eliminar archivos anteriores si existen
[ -f "$INPUT_FILE" ] && rm "$INPUT_FILE"
[ -f "$OUTPUT_FILE_1" ] && rm "$OUTPUT_FILE_1"
[ -f "$OUTPUT_FILE_2" ] && rm "$OUTPUT_FILE_2"

# 2. Crear la lista de fechas RSLC
ls RSLC -1 >> "$INPUT_FILE"

# 3. Leer fechas en array, y ordenarlas
dates=($(grep -Eo '[0-9]{8}' "$INPUT_FILE" | sort))

# 4. Agregar fecha inicial y final
START_DATE="20140801"
END_DATE=$(date +%Y%m%d)

dates=( "$START_DATE" "${dates[@]}" "$END_DATE" )

# 5. Función para convertir a formato YYYY-MM-DD
to_iso() {
    echo "$1" | sed 's/^\(....\)\(..\)\(..\)$/\1-\2-\3/'
}

# 6. Detectar brechas mayores a 60 días
for ((i=0; i<${#dates[@]}-1; i++)); do
    d1="${dates[$i]}"
    d2="${dates[$i+1]}"

    iso_d1=$(to_iso "$d1")
    iso_d2=$(to_iso "$d2")

    # Calcular diferencia en días
    days_diff=$(( ( $(date -d "$iso_d2" +%s) - $(date -d "$iso_d1" +%s) ) / 86400 ))

    if [ "$days_diff" -gt 60 ]; then
        # ---------------------------------------------
        # Archivo run_gaps.sh: dividir por años si es necesario
        start="$iso_d1"
        end="$iso_d2"

        while true; do
            next=$(date -d "$start +1 year" +%Y-%m-%d)
            if [ "$(date -d "$next" +%s)" -ge "$(date -d "$end" +%s)" ]; then
                echo "licsar_make_frame.sh -f -P \`cat sourceframe.txt\` 1 1 $start $end" >> "$OUTPUT_FILE_1"
                break
            else
                echo "licsar_make_frame.sh -f -P \`cat sourceframe.txt\` 1 1 $start $next" >> "$OUTPUT_FILE_1"
                start="$next"
            fi
        done

        # ---------------------------------------------
        # Archivo nla_request.sh: solo una línea por brecha
        echo "framebatch_update_frame.sh -k -P \`cat sourceframe.txt\` gapfill $d1 $d2" >> "$OUTPUT_FILE_2"
    fi
done

echo "✅ Archivos generados:"
echo " - $OUTPUT_FILE_1 (licsar_make_frame.sh)"
echo " - $OUTPUT_FILE_2 (framebatch_update_frame.sh)"

