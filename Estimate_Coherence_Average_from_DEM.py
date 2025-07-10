import sys
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.windows import from_bounds
from pathlib import Path
import glob

# Archivos de entrada y salida
volcanoes_file = "Volcanes_Chiles.txt"
input_txt = "combination_shorts.txt"
output_txt = "output_averages_from_cc_tifs.txt"
output_txt_std = "output_std_from_cc_tifs.txt"

def get_volcano_info(volcano_name, volcanoes_file):
    """Obtiene la información de un volcán específico del archivo."""
    try:
        with open(volcanoes_file, "r") as vf:
            for line in vf:
                if line.strip() == "" or line.startswith("#"):
                    continue
                nombre_volcan, lon, lat, distancia = line.split()
                if nombre_volcan.lower() == volcano_name.lower():
                    return nombre_volcan, float(lon), float(lat), float(distancia)
    except Exception as e:
        print(f"Error leyendo el archivo de volcanes: {e}")
    return None

def find_hgt_file():
    """Busca el archivo .geo.hgt.tif en GEOC o GEOC/geo."""
    paths = glob.glob("GEOC/*.geo.hgt.tif") + glob.glob("GEOC/geo/*.geo.hgt.tif")
    if not paths:
        print("No se encontró ningún archivo .geo.hgt.tif.")
        return None
    return Path(paths[0])  # Suponemos que solo hay uno por volcán

def crop_and_calculate_average(file_path_cc, file_path_hgt, volcano_lon, volcano_lat, save_image=False):
    try:
        with rasterio.open(file_path_cc) as src_cc, rasterio.open(file_path_hgt) as src_hgt:
            print(f"\nProcesando archivo: {file_path_cc.name}")

            data_cc = src_cc.read(1).astype(float)
            data_hgt = src_hgt.read(1).astype(float)

            nodata_mask = (data_cc == src_cc.nodata) | (data_hgt == src_hgt.nodata)
            data_cc[nodata_mask] = np.nan
            data_hgt[nodata_mask] = np.nan

            # Obtener altura de la cumbre
            fila, columna = src_hgt.index(volcano_lon, volcano_lat)
            altura_cumbre = data_hgt[fila, columna]
            altura_pie = np.nanmin(data_hgt)

            print(f"Altura de la cumbre: {altura_cumbre:.2f} m")
            print(f"Altura del pie: {altura_pie:.2f} m")

            # Crear máscara desde la base hasta la cumbre
            index_h = (data_hgt >= altura_pie) & (data_hgt <= altura_cumbre)

            # Calcular coherencia normalizada solo en esa zona
            if np.nanmax(data_cc) > 0:
                c_high = data_cc[index_h] / np.nanmax(data_cc)
            else:
                c_high = data_cc[index_h]

            average = np.nanmean(c_high)
            standar = np.nanstd(c_high)

            if save_image:
                plt.figure(figsize=(8, 6))
                plt.imshow(index_h, cmap='gray')
                plt.title(f"Zona: {altura_pie:.0f}m - {altura_cumbre:.0f}m")
                plt.savefig(f"zonas_cumbre_a_base_{file_path_cc.stem}.png", dpi=100)

            plt.figure(figsize=(8, 6))
            plt.imshow(index_h/np.nanmax(data_cc), cmap='viridis')
            plt.colorbar(label='Avg_Coh')
            plt.title(f"Clip Area {file_path_cc.stem} Avg_Coh:{average}")
            plt.savefig(f"{file_path_cc.parent}/recorte_{file_path_cc.stem}.png",dpi=50)
            print(f"Imagen recortada guardada como recorte_{file_path_cc.stem}.png")

            print("Promedio:", average, "Desviación estándar:", standar)
            return average, standar

    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return None, None

def main():
    if len(sys.argv) < 2:
        print("Uso: python script.py <Nombre_volcan>")
        return

    volcano_name = sys.argv[1]
    volcano_info = get_volcano_info(volcano_name, volcanoes_file)
    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado en {volcanoes_file}.")
        return

    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"Procesando volcán: {nombre_volcan} ({lon}, {lat})")

    hgt_file = find_hgt_file()
    if not hgt_file:
        return

    with open(input_txt, "r") as f:
        date_paths = f.read().splitlines()

    results = []
    resultsstd = []

    for i, date_path in enumerate(date_paths):
        file_path_cc = Path(f"GEOC/{date_path}/{date_path}.geo.cc.tif")
        if not file_path_cc.exists():
            print(f"Archivo no encontrado: {file_path_cc}")
            continue

        save_image = (i == 0)
        average, standar = crop_and_calculate_average(file_path_cc, hgt_file, lon, lat, save_image=save_image)

        if average is not None:
            results.append({"date": date_path, "average": average})
            resultsstd.append({"date": date_path, "standar": standar})

    # Guardar resultados
    with open(output_txt, "w") as f:
        for result in results:
            f.write(f"{result['date']} {result['average']:.4f}\n")

    with open(output_txt_std, "w") as f:
        for resultstd in resultsstd:
            f.write(f"{resultstd['date']} {resultstd['standar']:.4f}\n")

if __name__ == "__main__":
    main()
