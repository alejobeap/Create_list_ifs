import os
import sys
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.windows import from_bounds
from pathlib import Path

# Archivos de entrada y salida
volcanoes_file = "Volcanes_Chiles.txt"
input_txt = "Longs_combination_longs.txt"
output_txt = "Longs_output_averages_from_cc_tifs.txt"
output_txt_std = "Longs_output_std_from_cc_tifs.txt"

# Función para obtener información de un volcán
def get_volcano_info(volcano_name, volcanoes_file):
    """Obtiene la información de un volcán específico del archivo."""
    try:
        with open(volcanoes_file, "r") as vf:
            for line in vf:
                nombre_volcan, lon, lat, distancia = line.split()
                if nombre_volcan.lower() == volcano_name.lower():
                    return nombre_volcan, float(lon), float(lat), float(distancia)
    except Exception as e:
        print(f"Error leyendo el archivo de volcanes: {e}")
    return None


def crop_and_calculate_average(file_path, min_lon, max_lon, min_lat, max_lat, save_image=False):
    """Procesa un archivo raster y calcula el promedio y desviación estándar en la ventana especificada."""
    try:
        with rasterio.open(file_path) as src:
            print(f"Procesando archivo: {file_path}")
            print(f"Extensión geográfica: {src.bounds}")

            # Calcular ventana en coordenadas del archivo
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)

            # Leer la ventana de datos
            data = src.read(1, window=window)

            # Mostrar valores básicos
            print(f"Datos cargados: min={np.nanmin(data)}, max={np.nanmax(data)}, nodata={src.nodata}")

           # Guardar imagen recortada si se solicita
            if save_image:
                plt.figure(figsize=(8, 6))
                plt.imshow(data / np.nanmax(data), cmap='viridis')
                plt.colorbar(label='Avg_Coh')
                plt.title(f"Clip Area {file_path.stem}")
                plt.savefig(f"recorte_{file_path.stem}.png",dpi=100)
                print(f"Imagen recortada guardada como recorte_{file_path.stem}.png")

            # Calcular promedio ignorando NaNs
            average = np.nanmean(data[data != src.nodata] / np.nanmax(data))
            standar = np.nanstd(data[data != src.nodata] / np.nanmax(data))


            plt.figure(figsize=(8, 6))
            plt.imshow(data / np.nanmax(data), cmap='viridis')
            plt.colorbar(label='Avg_Coh')
            plt.title(f"Clip Area {file_path.stem} Avg_Coh:{average}")
            plt.savefig(f"{file_path.parent}/recorte_{file_path.stem}.png",dpi=100)
            print(f"Imagen recortada guardada como recorte_{file_path.stem}.png")


            print("AVERAGE", average, standar)

            return average, standar
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None, None


def main():
    # Asegurarse de que se proporciona el nombre del volcán como argumento
    if len(sys.argv) < 2:
        print("Uso: python script.py <Nombre_volcan>")
        return

    volcano_name = sys.argv[1]

    # Obtener información del volcán
    volcano_info = get_volcano_info(volcano_name, volcanoes_file)
    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado en el archivo {volcanoes_file}.")
        return

    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"Procesando volcán: {nombre_volcan} en coordenadas ({lon}, {lat}) con distancia {distancia} km")

    # Dimensiones de corte en kilómetros
    cut_size_km = distancia

    # Convertir kilómetros a grados aproximadamente (1 grado = 111 km)
    cut_size_deg = cut_size_km / 111.0

    # Calcular límites de la ventana de corte
    min_lon = lon - cut_size_deg / 2
    max_lon = lon + cut_size_deg / 2
    min_lat = lat - cut_size_deg / 2
    max_lat = lat + cut_size_deg / 2

    # Leer lista de archivos raster
    with open(input_txt, "r") as f:
        date_paths = f.read().splitlines()

    results = []
    resultsstd = []

    for i, date_path in enumerate(date_paths):
        file_path = Path(f"GEOC/{date_path}/{date_path}.geo.cc.tif")

        if not file_path.exists():
            print(f"Archivo no encontrado: {file_path}")
            continue

        save_image = (i == 0)  # Guardar solo la primera imagen recortada
        average, standar = crop_and_calculate_average(file_path, min_lon, max_lon, min_lat, max_lat, save_image=save_image)

        if average is not None:
            results.append({"date": date_path, "average": average})
            resultsstd.append({"date": date_path, "standar": standar})

    # Guardar resultados en un archivo de texto
    with open(output_txt, "w") as f:
        for result in results:
            f.write(f"{result['date']} {result['average']:.4f}\n")

    with open(output_txt_std, "w") as f:
        for resultstd in resultsstd:
            f.write(f"{resultstd['date']} {resultstd['standar']:.4f}\n")


if __name__ == "__main__":
    main()
