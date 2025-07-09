#!/bin/bash

# Ruta base
base_dir="GEOC"

# Archivo de salida
output_file="listaunwpng.txt"

# Limpiar el archivo de salida si existe
: > "$output_file"

# Solo carpetas de primer nivel dentro de GEOC
for dir in "$base_dir"/*/; do
    # Verifica si es un directorio
    [ -d "$dir" ] || continue

    # Verifica si contiene archivos que terminan en geo.unw.png
    if ! ls "$dir"/*geo.unw.png 1>/dev/null 2>&1; then
        # Imprime solo el nombre de la carpeta (sin ruta GEOC/)
        basename "$dir" >> "$output_file"
    fi
done
