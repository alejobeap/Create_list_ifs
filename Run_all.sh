#!/bin/bash

echo "Run shorters connections (2 for each epoch)"
./create_interefrograms_all_txt.sh

echo "Create wrap and cc for shorters connections (2 for each epoch)"
./Create_filter_IFS.sh

# Guardar la segunda parte como un pequeño script temporal
cat << 'EOF' > run_later.sh
#!/bin/bash
sleep 7200  # Esperar 2 horas

echo "Estimated the average coherence"
python Estimate_Coherence_Average_from_DEM.py
./filtered_average.sh
python matriz_coherencia.py
./MesesLargos.sh
./Longs_create_interefrograms_all_txt.sh
./crear_standar_list.sh
./crear_final_list.sh
EOF

# Hacerlo ejecutable
chmod +x run_later.sh

# Ejecutarlo con nohup para que continúe aunque cierres la terminal
nohup ./run_later.sh > run_later.log 2>&1 &

echo "✅ La segunda parte del script se ejecutará automáticamente en 2 horas."
echo "✔️ Puedes cerrar esta terminal si quieres. Todo quedará registrado en run_later.log"
