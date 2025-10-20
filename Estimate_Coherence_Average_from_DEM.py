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
name_file="NameVolcano.txt"
geod = Geod(ellps="WGS84")

def get_volcano_name_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return None
            # If there are spaces, dots or hyphens, wrap in quotes for matching
            if any(c in content for c in [' ', '.', '-']):
                return f'"{content}"'
            else:
                return content
    except FileNotFoundError:
        return None
        
def get_volcano_info(volcano_name, volcanoes_file):
    try:
        with open(volcanoes_file, "r", encoding="utf-8") as vf:
            next(vf)  # Skip header line
            for line in vf:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('"'):
                    parts = line.split()
                    # Get full name tokens until closing quote
                    name_tokens = []
                    for token in parts:
                        name_tokens.append(token)
                        if token.endswith('"'):
                            break
                    nombre_volcan = " ".join(name_tokens).strip('"')
                    rest = parts[len(name_tokens):]
                    if len(rest) != 3:
                        print(f"Línea con formato inesperado: {line}")
                        continue
                    # Strip commas and convert floats
                    lon = float(rest[0].rstrip(','))
                    lat = float(rest[1].rstrip(','))
                    distancia = float(rest[2].rstrip(','))
                else:
                    parts = line.split()
                    nombre_volcan = parts[0]
                    lon = float(parts[1].rstrip(','))
                    lat = float(parts[2].rstrip(','))
                    distancia = float(parts[3].rstrip(','))

                if nombre_volcan.lower() == volcano_name.strip('"').lower():
                    return nombre_volcan, lon, lat, distancia
    except Exception as e:
        print(f"Error leyendo el archivo de volcanes: {e}")
    return None


def get_base_distance_and_window(lon, lat, buffer_deg=0.2):
    """Calcula la distancia maxima cima-base y ventana cuadrada para recorte."""
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


                        # Leer toda la banda 1 (elevacion completa)
            elevacion = src.read(1)

            # Enmascarar valores nodata (convertirlos en np.nan)
            elevacion = np.where(elevacion == src.nodata, np.nan, elevacion)

            # Calcular maximos y minimos ignorando los np.nan
            maxelevacion = np.nanmax(elevacion)
            minelevacion = np.nanmin(elevacion)


            # Get current working directory
            cwd = os.getcwd()

            # Extract parts of the path (e.g., .../Erta/079D)
            parts = cwd.strip("/").split("/")
            erta = parts[-2]
            code = parts[-1]

            # Construct filename
            filename = f"{erta}_{code}_heigh.txt"
            filepath = os.path.join(cwd, filename)

            # Calculate adjusted values
            h_cima_adj = maxelevacion + 10
            h_base_adj = minelevacion - 10

            # Write to file
            #with open(filepath, "w") as f:
            #    f.write(f"{h_cima_adj:.0f} {h_base_adj:.0f}\n")


            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            elevation = src.read(1, window=window)
            elevation = np.where(elevation == src.nodata, np.nan, elevation)

            # Indices globales para la ventana
            row_min, col_min = window.row_off, window.col_off
            row_min, col_min = int(row_min), int(col_min)

            row_cima, col_cima = src.index(lon, lat)
            
            # First try using relative indices
            row_cima_rel = row_cima - row_min
            col_cima_rel = col_cima - col_min
            
            def check_position_and_height(row_rel, col_rel):
                """Check if coordinates are in window and elevation is valid."""
                if not (0 <= row_rel < elevation.shape[0]) or not (0 <= col_rel < elevation.shape[1]):
                    return False
                h_cima = elevation[row_rel, col_rel]
                if np.isnan(h_cima):
                    return False
                return True
            
            # First attempt with relative indices
            if not check_position_and_height(row_cima_rel, col_cima_rel):
                # Second attempt using absolute indices
                row_cima_rel = row_cima
                col_cima_rel = col_cima
                if not check_position_and_height(row_cima_rel, col_cima_rel):
                    raise ValueError("Coordenadas cima fuera de ventana o Elevacion cima es NaN")
            
            # If we got here, h_cima is valid
            h_cima = elevation[row_cima_rel, col_cima_rel]

            # Definir base como pixeles con elev <= percentil 10
            h_base = np.nanpercentile(elevation, 10)
            mask_base = elevation <= h_base

            # Obtener coordenadas de pixeles base
            rows_base, cols_base = np.where(mask_base)

            distances = []
            for r, c in zip(rows_base, cols_base):
                row_global = r + row_min
                col_global = c + col_min
                lon_pix, lat_pix = src.xy(row_global, col_global)
                _, _, dist_m = geod.inv(lon, lat, lon_pix, lat_pix)
                distances.append(dist_m)

            if not distances:
                print("No se encontraron pixeles base validos.")
                return None, None, None

            min_dist = min(distances)
            max_dist = max(distances)

            print(f"Cima: {h_cima:.1f} m, Base (P10): {h_base:.1f} m")
            print(f"Distancia minima cima-base: {min_dist:.1f} m")
            print(f"Distancia mixima cima-base: {max_dist:.1f} m")


            # Usar distancia maxima con margen 10%
            cut_size_m = min_dist * 1.1
            cut_size_deg = cut_size_m / 111000  # m a grados aprox.

            min_lon_cut = lon - cut_size_deg / 2
            max_lon_cut = lon + cut_size_deg / 2
            min_lat_cut = lat - cut_size_deg / 2
            max_lat_cut = lat + cut_size_deg / 2

            print(f"Ventana cuadrada en grados: lon[{min_lon_cut:.4f}, {max_lon_cut:.4f}], lat[{min_lat_cut:.4f}, {max_lat_cut:.4f}]")

            # Usar distancia maxima con margen 10%
            cut_size_m_2 = max_dist
            cut_size_deg_2 = cut_size_m_2 / 111000  # m a grados aprox.

            min_lon_cut2 = lon - cut_size_deg_2 / 2
            max_lon_cut2 = lon + cut_size_deg_2 / 2
            min_lat_cut2 = lat - cut_size_deg_2 / 2
            max_lat_cut2 = lat + cut_size_deg_2 / 2

            print(f"Ventana cuadrada en grados para futuro recorte: lon[{min_lon_cut2:.4f}, {max_lon_cut2:.4f}], lat[{min_lat_cut2:.4f}, {max_lat_cut2:.4f}]")
            
            h_base_adj = max(h_base_adj, 0)
            
                        # Write to file
            with open(filepath, "w") as f:
                f.write(f"{h_cima_adj:.0f} {h_base_adj:.0f} {min_lon_cut:.4f}/{max_lon_cut:.4f}/{min_lat_cut:.4f}/{max_lat_cut:.4f} {min_lon_cut2:.4f}/{max_lon_cut2:.4f}/{min_lat_cut2:.4f}/{max_lat_cut2:.4f}\n")

            return window, (min_lon_cut, max_lon_cut, min_lat_cut, max_lat_cut), hgt_path
    except Exception as e:
        print(f"Error procesando elevacion: {e}")
        return None, None, None

def crop_and_calculate_average(file_path, bounds, save_image=False):
    try:
        with rasterio.open(file_path) as src:
            min_lon, max_lon, min_lat, max_lat = bounds
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            data = src.read(1, window=window)
            data = np.where(data == src.nodata, np.nan, data)

            if data.size == 0 or np.all(np.isnan(data)):
                print(f"Advertencia: No hay datos validos en {file_path.name}")
                return None, None

            norm_factor = np.nanmax(data)
            if np.isnan(norm_factor) or norm_factor == 0:
                print(f"Advertencia: np.nanmax es invalido o cero en {file_path.name}")
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

    # Main logic to get volcano_name
    if len(sys.argv) < 2:
        print(f"No se ingresó el nombre del volcán por línea de comando.")
        volcano_name = get_volcano_name_from_file(name_file)
        if not volcano_name:
            print(f"No se encontró el archivo {name_file} o está vacío. Usando valor por defecto: {default_volcano_name}")
            volcano_name = default_volcano_name
    else:
        volcano_name = sys.argv[1]
    
    print(f"Nombre del volcán: {volcano_name}")
    
    volcano_info = get_volcano_info(volcano_name, volcanoes_file)
    
    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado.")
    else:
        print(f"Información del volcán: {volcano_info}")
        
    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"\n--- Procesando volcan: {nombre_volcan} en ({lon}, {lat}) ---\n")

    window, cut_bounds, hgt_used = get_base_distance_and_window(lon, lat)
    if window is None or cut_bounds is None:
        print("No se pudo determinar el area de recorte.")
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
            print(f"Sin resultado valido para {date_path}")

    with open(output_txt, "w") as f:
        for result in results:
            f.write(f"{result['date']} {result['average']:.4f}\n")

    with open(output_txt_std, "w") as f:
        for resultstd in resultsstd:
            f.write(f"{resultstd['date']} {resultstd['standar']:.4f}\n")

if __name__ == "__main__":
    main()
