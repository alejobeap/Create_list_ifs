#!/bin/bash

OLD_FILE="Updated_list_old.txt"
NEW_FILE="Updated_list_new.txt"
OUTPUT_FILE="Update_combinations_IFS.txt"
Chilescase="n"  # Cambiar a "y" para excluir meses 6 a 9

# Validar archivos
[[ ! -f $OLD_FILE ]] && { echo "❌ $OLD_FILE no encontrado"; exit 1; }
[[ ! -f $NEW_FILE ]] && { echo "❌ $NEW_FILE no encontrado"; exit 1; }

> "$OUTPUT_FILE"

# Leer fechas ordenadas
mapfile -t old_dates < <(sort "$OLD_FILE")
mapfile -t new_dates < <(sort "$NEW_FILE")

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

combo_exists() {
  local c1="$1"
  local c2="$2"
  grep -q -E "^${c1}$|^${c2}$" "$OUTPUT_FILE"
}

# Generar combinaciones entre old y new
for old_date in "${old_dates[@]}"; do
  count_intervals=([6]=0 [9]=0 [12]=0 [15]=0)
  next3=0

  for new_date in "${new_dates[@]}"; do
    if is_excluded "$old_date" || is_excluded "$new_date"; then
      continue
    fi

    diff=$(month_diff "$old_date" "$new_date")

    if valid_diff "$diff" && (( count_intervals[$diff] < 2 )); then
      if ! combo_exists "${old_date}_${new_date}" "${new_date}_${old_date}"; then
        echo "${old_date}_${new_date}" >> "$OUTPUT_FILE"
        ((count_intervals[$diff]++))
        continue
      fi
    fi

    if (( next3 < 3 )); then
      if ! combo_exists "${old_date}_${new_date}" "${new_date}_${old_date}"; then
        echo "${old_date}_${new_date}" >> "$OUTPUT_FILE"
        ((next3++))
      fi
    else
      break
    fi
  done
done

echo "Total combinaciones generadas: $(wc -l < "$OUTPUT_FILE")"
echo "✅ Script terminado."
