#!/bin/bash

INPUT_FILE="Updated_list.txt"
OUTPUT_FILE="Update_combinations_IFS.txt"
Chilescase="n"

[[ ! -f $INPUT_FILE ]] && { echo "❌ $INPUT_FILE no encontrado"; exit 1; }
> "$OUTPUT_FILE"

# Leer fechas ordenadas
mapfile -t dates < <(sort "$INPUT_FILE")

month_diff() {
  local s=$1 e=$2
  local sy=${s:0:4} sm=${s:4:2} ey=${e:0:4} em=${e:4:2}
  echo $(((10#$ey - 10#$sy)*12 + (10#$em - 10#$sm)))
}

is_excluded() {
  local m=$((10#${1:4:2}))
  [[ $Chilescase == "y" && $m -ge 6 && $m -le 9 ]]
}

valid_diff() {
  local d=$1
  [[ $d == 6 || $d == 9 || $d == 12 || $d == 15 ]]
}

# Generar combinaciones para cada fecha
generate_combos() {
  local i=$1 sd=${dates[i]} count_intervals=([6]=0 [9]=0 [12]=0 [15]=0) next3=0

  for ((j=i+1; j<${#dates[@]}; j++)); do
    local ed=${dates[j]}
    local diff=$(month_diff "$sd" "$ed")

    # combos 6,9,12,15 meses
    if ! is_excluded "$sd" && ! is_excluded "$ed" && valid_diff "$diff" && (( count_intervals[$diff]<2 )); then
      echo "${sd}_${ed}" >> "$OUTPUT_FILE"
      ((count_intervals[$diff]++))
      continue
    fi

    # combos con siguientes 3 fechas, sin importar diff
    if (( next3 < 3 )); then
      # evitar duplicados
      if ! grep -q -E "^${sd}_${ed}$|^${ed}_${sd}$" "$OUTPUT_FILE"; then
        echo "${sd}_${ed}" >> "$OUTPUT_FILE"
        ((next3++))
      fi
    else
      break
    fi
  done
}

# Forzar conexiones entre años consecutivos (mínimo 2 combos)
force_between_years() {
  local y1=$1 y2=$2 count=0
  local y1_dates=() y2_dates=()

  for d in "${dates[@]}"; do
    [[ ${d:0:4} == $y1 ]] && y1_dates+=("$d")
    [[ ${d:0:4} == $y2 ]] && y2_dates+=("$d")
  done

  for d1 in "${y1_dates[@]}"; do
    [[ $(is_excluded "$d1") ]] && continue
    for d2 in "${y2_dates[@]}"; do
      [[ $(is_excluded "$d2") ]] && continue
      combo="${d1}_${d2}"
      revcombo="${d2}_${d1}"
      if ! grep -q -E "^$combo$|^$revcombo$" "$OUTPUT_FILE"; then
        echo "$combo" >> "$OUTPUT_FILE"
        ((count++))
        ((count>=2)) && return
      fi
    done
  done
}

# Verificar si existe combo entre años
exists_combo_years() {
  local y1=$1 y2=$2
  grep -qE "^${y1}[0-9]{4}_.{8}$|^.{8}_${y1}[0-9]{4}$" "$OUTPUT_FILE" &&
  grep -qE "${y2}" "$OUTPUT_FILE"
}

# Forzar mínimo 2 combos de cada fecha con fechas del siguiente año
force_min_connections() {
  local date=$1
  local y=${date:0:4}
  local ny=$((y+1))
  local count=0

  # Contar conexiones actuales con año siguiente
  local connected=()
  while IFS= read -r line; do
    [[ $line == ${date}_* ]] && connected+=("${line#*_}")
    [[ $line == *_${date} ]] && connected+=("${line%_*}")
  done < "$OUTPUT_FILE"

  for c in "${connected[@]}"; do
    (( ${c:0:4} == ny )) && ((count++))
  done

  [[ $count -ge 2 ]] && return

  # Agregar conexiones faltantes
  for d in "${dates[@]}"; do
    [[ ${d:0:4} == $ny ]] || continue
    is_excluded "$d" && continue
    if ! grep -q -E "^${date}_${d}$|^${d}_${date}$" "$OUTPUT_FILE"; then
      echo "${date}_${d}" >> "$OUTPUT_FILE"
      ((count++))
      ((count>=2)) && break
    fi
  done
}

# Generar todas las combinaciones
for i in "${!dates[@]}"; do
  generate_combos "$i"
done

years=($(cut -c1-4 "$INPUT_FILE" | sort -u))

# Forzar conexiones entre años consecutivos si faltan
for ((i=0; i<${#years[@]}-1; i++)); do
  y1=${years[i]}
  y2=${years[i+1]}
  if ! grep -qE "${y1}.*${y2}" "$OUTPUT_FILE"; then
    echo "⚠️ Forzando combos entre $y1 y $y2"
    force_between_years "$y1" "$y2"
  fi
done

# Forzar conexiones mínimas de cada fecha con fechas del siguiente año
for d in "${dates[@]}"; do
  force_min_connections "$d"
done

echo "Total combos generados: $(wc -l < "$OUTPUT_FILE")"
echo "✅ Script terminado."
