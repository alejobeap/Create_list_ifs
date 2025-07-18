#!/bin/bash

for dir in GEOCml2/*; do
    if [ -d "$dir" ]; then
        basename=$(basename "$dir")
        if [[ "$basename" == 2* ]]; then
            echo "$basename" >> listGEOC.txt
        fi
    fi
done

#!/bin/bash

# 1. Extraer y ordenar fechas únicas
cut -d'_' -f1,2 listGEOC.txt | tr '_' '\n' | sort -u > fechas_ordenadas.txt

# 2. Leer fechas en array
mapfile -t fechas < fechas_ordenadas.txt

# 3. Buscar primer gap mayor a 60 días
gap_start=-1
for ((i=0; i<${#fechas[@]}-1; i++)); do
    f1=${fechas[$i]}
    f2=${fechas[$i+1]}
    ts1=$(date -d "$f1" +%s)
    ts2=$(date -d "$f2" +%s)
    diff=$(( (ts2 - ts1) / 86400 ))
    if [ $diff -gt 60 ]; then
        echo "Gap detectado entre $f1 y $f2 ($diff días)"
        gap_start=$i
        break
    fi
done

# 4. Si no se encuentra gap, terminar
if [ $gap_start -eq -1 ]; then
    echo "No se encontró ningún gap mayor a 60 días."
    exit 1
fi
# 5. Tomar 10 fechas antes y 10 después
start_index=$((gap_start - 9))
end_index=$((gap_start + 11))

[ $start_index -lt 0 ] && start_index=0
[ $end_index -gt ${#fechas[@]} ] && end_index=${#fechas[@]}

selected=("${fechas[@]:$start_index:$((end_index - start_index))}")

# 6. Guardar fechas alrededor del gap
printf "%s\n" "${selected[@]}" > fechas_gap.txt

# 7. Generar combinaciones de 2 y 3 fechas
> combinaciones_gaps.txt

for ((i=0; i<${#selected[@]}-1; i++)); do
    year_i=${selected[$i]:0:4}
    count=0
    for ((j=i+1; j<${#selected[@]} && count<3; j++)); do
        year_j=${selected[$j]:0:4}
        if [ "$year_i" != "$year_j" ]; then
            echo "${selected[$i]}_${selected[$j]}" >> combinaciones_gaps.txt
            ((count++))
        fi
    done
done
line_count=$(wc -l < combinaciones_gaps.txt)
echo "📄 Número total de combinaciones generadas: $line_count"
echo "✔ Combinaciones guardadas en combinaciones_gaps.txt"

if [ "$line_count" -gt 1 ]; then
    parent_dir=$(basename "$(dirname "$(pwd)")")
    current_dir=$(basename "$(pwd)")
    echo "framebatch_gapfill.sh -l -I /work/scratch-pw3/licsar/alejobea/batchdir/${parent_dir}/${current_dir}/combinaciones_gaps.txt 5 200 7 2"
    framebatch_gapfill.sh -l -I /work/scratch-pw3/licsar/alejobea/batchdir/${parent_dir}/${current_dir}/combinaciones_gaps.txt 5 200 7 2
fi

