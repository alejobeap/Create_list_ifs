import sys
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
from rasterio.windows import from_bounds
import glob
import os
from pyproj import Geod

# Archivos de entrada y salida
volcanoes_file = "Volcanes_Chiles.txt"
input_txt = "combination_shorts.txt"
output_txt = "output_averages_from_cc_tifs.txt"
output_txt_std = "output_std_from_cc_tifs.txt"

geod = Geod(ellps="WGS84")

def get_volcano_info(volcano_name, volcanoes_file):
    try:
        with open(volcanoes_file, "r") as vf:
            for line in vf:
                nombre_volcan, lon, lat, distancia = line.strip().split()
                if nombre_volcan.lower() == volcano_name.lower():
                    return nombre_volcan, float(lon), float(lat), float(distancia)
    except Exception as e:
        print(f"Error leyendo el archivo de volcanes: {e}")
    return None

def get_base_distance_and_window(lon, lat, buffer_deg=0.2):
    """Calcula la distancia máxima cima-base y ventana cuadrada para recorte."""
    try:
        hgt_files = glob.glob("GEOC/*.geo.hgt.tif") + glob.glob("GEOC/geo/*.geo.hgt.tif")
        if not hgt_files:
            raise FileNotFoundError("No se encontraron archivos .geo.hgt.tif")

        hgt_path = hgt_files[0]
        with rasterio.open(hgt_path) as src:
            # Definir ventana amplia para asegurar cubrir base y cima
            min_lon = lon - buffer_deg
            max_lon = lon + buffer_deg
            min_lat = lat - buffer_deg
            max_lat = lat + buffer_deg

            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            elevation = src.read(1, window=window)
            elevation = np.where(elevation == src.nodata, np.nan, elevation)

            # Índices globales para la ventana
            row_min, col_min = window.row_off, window.col_off
            row_min, col_min = int(row_min), int(col_min)

            # Índice cima local en ventana
            row_cima, col_cima = src.index(lon, lat)
            row_cima_rel = row_cima - row_min
            col_cima_rel = col_cima - col_min

            if not (0 <= row_cima_rel < elevation.shape[0]) or not (0 <= col_cima_rel < elevation.shape[1]):
                raise ValueError("Coordenadas cima fuera de ventana")

            h_cima = elevation[row_cima_rel, col_cima_rel]
            if np.isnan(h_cima):
                raise ValueError("Elevación cima es NaN")

            # Definir base como píxeles con elev <= percentil 10
            h_base = np.nanpercentile(elevation, 10)
            mask_base = elevation <= h_base

            # Obtener coordenadas de píxeles base
            rows_base, cols_base = np.where(mask_base)

            distances = []
            for r, c in zip(rows_base, cols_base):
                row_global = r + row_min
                col_global = c + col_min
                lon_pix, lat_pix = src.xy(row_global, col_global)
                _, _, dist_m = geod.inv(lon, lat, lon_pix, lat_pix)
                distances.append(dist_m)

            if not distances:
                print("No se encontraron píxeles base válidos.")
                return None, None, None

            min_dist = min(distances)
            max_dist = max(distances)

            print(f"Cima: {h_cima:.1f} m, Base (P10): {h_base:.1f} m")
            print(f"Distancia mínima cima-base: {min_dist:.1f} m")
            print(f"Distancia máxima cima-base: {max_dist:.1f} m")

            # Usar distancia máxima con margen 10%
            cut_size_m = min_dist * 1.1
            cut_size_deg = cut_size_m / 111000  # m a grados aprox.

            min_lon_cut = lon - cut_size_deg / 2
            max_lon_cut = lon + cut_size_deg / 2
            min_lat_cut = lat - cut_size_deg / 2
            max_lat_cut = lat + cut_size_deg / 2

            print(f"Ventana cuadrada en grados: lon[{min_lon_cut:.4f}, {max_lon_cut:.4f}], lat[{min_lat_cut:.4f}, {max_lat_cut:.4f}]")

            return window, (min_lon_cut, max_lon_cut, min_lat_cut, max_lat_cut), hgt_path
    except Exception as e:
        print(f"Error procesando elevación: {e}")
        return None, None, None

def crop_and_calculate_average(file_path, bounds, save_image=False):
    try:
        with rasterio.open(file_path) as src:
            min_lon, max_lon, min_lat, max_lat = bounds
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            data = src.read(1, window=window)
            data = np.where(data == src.nodata, np.nan, data)

            if data.size == 0 or np.all(np.isnan(data)):
                print(f"Advertencia: No hay datos válidos en {file_path.name}")
                return None, None

            norm_factor = np.nanmax(data)
            if np.isnan(norm_factor) or norm_factor == 0:
                print(f"Advertencia: np.nanmax es inválido o cero en {file_path.name}")
                return None, None

            data_norm = data / norm_factor
            average = np.nanmean(data_norm)
            standar = np.nanstd(data_norm)

            if save_image:
                plt.figure(figsize=(8, 6))
                plt.imshow(data_norm, cmap='viridis')
                plt.colorbar(label='Avg_Coh')
                plt.title(f"{file_path.stem} Avg_Coh: {average:.3f}")
                plt.savefig(f"{file_path.parent}/recorte_{file_path.stem}.png", dpi=100)
                plt.close()

            return average, standar
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None, None

def main():
    current_dir = os.getcwd()
    default_volcano_name = os.path.basename(os.path.dirname(current_dir))

    if len(sys.argv) < 2:
        print(f"No se ingresó el nombre del volcán. Usando valor por defecto: {default_volcano_name}")
        volcano_name = default_volcano_name
    else:
        volcano_name = sys.argv[1]

    print(f"Nombre del volcán: {volcano_name}")

    volcano_info = get_volcano_info(volcano_name, volcanoes_file)

    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado.")
        return

    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"\n--- Procesando volcán: {nombre_volcan} en ({lon}, {lat}) ---\n")

    window, cut_bounds, hgt_used = get_base_distance_and_window(lon, lat)
    if window is None or cut_bounds is None:
        print("No se pudo determinar el área de recorte.")
        return

    with open(input_txt, "r") as f:
        date_paths = f.read().splitlines()

    results = []
    resultsstd = []

    for i, date_path in enumerate(date_paths):
        file_path = Path(f"GEOC/{date_path}/{date_path}.geo.cc.tif")
        if not file_path.exists():
            print(f"Archivo no encontrado: {file_path}")
            continue

        save_image = (i == 0)
        average, standar = crop_and_calculate_average(file_path, cut_bounds, save_image=save_image)

        if average is not None:
            results.append({"date": date_path, "average": average})
            resultsstd.append({"date": date_path, "standar": standar})
        else:
            print(f"Sin resultado válido para {date_path}")

    with open(output_txt, "w") as f:
        for result in results:
            f.write(f"{result['date']} {result['average']:.4f}\n")

    with open(output_txt_std, "w") as f:
        for resultstd in resultsstd:
            f.write(f"{resultstd['date']} {resultstd['standar']:.4f}\n")

if __name__ == "__main__":
    main()
