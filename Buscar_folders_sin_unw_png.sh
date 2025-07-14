#!/bin/bash

# Ruta base
base_dir="GEOC"

# Archivo de salida
output_file="listaunwpng.txt"

# Limpiar el archivo de salida si existe
: > "$output_file"

# Solo carpetas de primer nivel dentro de GEOC que empiezan con '2'
for dir in "$base_dir"/2*/; do
    # Verifica si es un directorio
    [ -d "$dir" ] || continue

    # Verifica si contiene archivos que terminan en geo.unw.png
    if ! ls "$dir"/*geo.unw.png 1>/dev/null 2>&1; then
        # Imprime solo el nombre de la carpeta (sin ruta GEOC/)
        basename "$dir" >> "$output_file"
    fi
done


#!/bin/bash

# Archivo de entrada
archivo="listaunwpng.txt"

# Archivos temporales
archivo_otros="tmp_otros.txt"
archivo_mayo_sep="tmp_mayo_sep.txt"

# Limpiar archivos temporales previos
> "$archivo_otros"
> "$archivo_mayo_sep"

# Leer línea por línea
while IFS= read -r linea; do
    # Extraer el mes de la primera fecha (YYYYMMDD)
    mes=${linea:4:2}

    # Si el mes está entre 05 y 09, guardar en archivo_mayo_sep
    if [[ "$mes" =~ ^0[5-9]$ ]]; then
        echo "$linea" >> "$archivo_mayo_sep"
    else
        echo "$linea" >> "$archivo_otros"
    fi
done < "$archivo"

# Concatenar las líneas: primero las que NO son de mayo a septiembre, luego las otras
cat "$archivo_otros" "$archivo_mayo_sep" > "$archivo"

# Limpiar archivos temporales
rm "$archivo_otros" "$archivo_mayo_sep"


line_count=$(wc -l < "$archivo")
echo "📄 Número total de combinaciones generadas: $line_count"
