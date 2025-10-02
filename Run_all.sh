#!/bin/bash

gapfill=$1

# Si gapfill no es 1 ni 0, o está vacío, lo asignamos a 0
if [[ "$gapfill" != "1" && "$gapfill" != "0" ]]; then
    gapfill=0
fi


if [[ "$gapfill" == 1 ]]; then
       ./Gap_fill_licsar_make_frame.sh
       ./nla_request_lics.sh
fi
    
echo "Run shorters connections (2 for each epoch)"
./create_interefrograms_all_txt.sh

echo "Create wrap and cc for shorters connections (2 for each epoch)"
./Create_filter_IFS.sh

# Guardar la segunda parte como un pequeño script temporal
cat << 'EOF' > run_later.sh
#!/bin/bash
sleep 2000  # Esperar 2 horas

echo "Estimated the average coherence"
python Estimate_Coherence_Average_from_DEM.py
python plot_histogram_average_coherence.py
./filtered_average.sh
python matriz_coherencia.py
./Largas_combinaciones_filtradas.sh
./crear_standar_list.sh
./crear_final_list.sh

sleep 2000  # Esperar 2 horas
./Buscar_folders_sin_unw_png.sh
./unwrap_run.sh

sleep 4000  # Esperar 2 horas
./deletefolder_GEOC.sh
./Buscar_folders_sin_unw_png.sh
python Buscar_empty_tifs_2_delete.py
./Buscar_folders_sin_unw_png.sh
./Conexiones_Aisladas.sh
./Buscar_folders_sin_unw_png.sh

sleep 1000  # Esperar 2 horas
./unwrap_run.sh
python Buscar_empty_tifs_2_delete.py

sleep 1000  # Esperar 2 horas
./jasmin_run_cmd.sh

EOF

# Hacerlo ejecutable
chmod +x run_later.sh

# Ejecutarlo con nohup para que continúe aunque cierres la terminal
nohup ./run_later.sh > run_later.log 2>&1 &

echo "✅ La segunda parte del script se ejecutará automáticamente en 2 horas."
echo "✔️ Puedes cerrar esta terminal si quieres. Todo quedará registrado en run_later.log"



