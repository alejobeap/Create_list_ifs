#!/bin/bash

# Obtener la carpeta actual (ej: /work/.../Merapi/076D)
CURRENT_DIR=$(pwd)

# La subcarpeta (Merapi) es el directorio padre
PROJECT=$(basename "$(dirname "$CURRENT_DIR")")

# Convertir a minúsculas
PROJECT_LOWER=$(echo "$PROJECT" | tr '[:upper:]' '[:lower:]')

# Leer el contenido del archivo sourceframe.txt
SOURCE=$(cat sourceframe.txt)

echo $SOURCE
echo ${PROJECT_LOWER}
# Crear nombre de salida
OUTPUT="${PROJECT_LOWER}_${SOURCE}.json"
OUTPUTFILT="${PROJECT_LOWER}_${SOURCE}_filt.json"


# Ejecutar el comando
python data_to_json.py TS_GEOCml2mask/cum.h5 "$OUTPUT"
python data_to_json.py TS_GEOCml2mask/cum_filt.h5 "$OUTPUTFILT"

# Si el primer argumento, ejecutar acción
if [ -n "$1" ]; then
	echo "Copiando"
	scp -r $OUTPUT /work/scratch-pw3/licsar/alejobea/batchdir/VolcNet/jasmin_clones/${1}/
	scp -r $OUTPUTFILT /work/scratch-pw3/licsar/alejobea/batchdir/VolcNet/jasmin_clones/${1}/
fi
