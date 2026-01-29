
import sys
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
from rasterio.windows import from_bounds
import glob
import os
from pyproj import Geod

# ===============================
# Archivos de entrada y salida
# ===============================
volcanoes_file = "Volcanes_Chiles.txt"
input_txt = "combination_shorts.txt"
output_txt = "output_averages_from_cc_tifs.txt"
output_txt_std = "output_std_from_cc_tifs.txt"
name_file = "NameVolcano.txt"

geod = Geod(ellps="WGS84")

# ===============================
# Utilidades volcán
# ===============================
def get_volcano_name_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return None
            if any(c in content for c in [' ', '.', '-']):
                return f'"{content}"'
            else:
                return content
    except FileNotFoundError:
        return None


def get_volcano_info(volcano_name, volcanoes_file):
    try:
        with open(volcanoes_file, "r", encoding="utf-8") as vf:
            next(vf)
            for line in vf:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('"'):
                    parts = line.split()
                    name_tokens = []
                    for token in parts:
                        name_tokens.append(token)
                        if token.endswith('"'):
                            break
                    nombre_volcan = " ".join(name_tokens).strip('"')
                    rest = parts[len(name_tokens):]
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
        print(f"Error leyendo archivo de volcanes: {e}")

    return None


# ===============================
# NUEVO: ventana fija por km
# ===============================
def get_fixed_window_from_km(lon, lat, area_km):
    """
    Ventana cuadrada centrada en lon/lat
    area_km x area_km
    """
    area_deg = area_km / 111.0
    half = area_deg / 2

    min_lon = lon - half
    max_lon = lon + half
    min_lat = lat - half
    max_lat = lat + half

    print(f"\nUsando ventana fija de {area_km} km")
    print(f"lon[{min_lon:.4f}, {max_lon:.4f}], lat[{min_lat:.4f}, {max_lat:.4f}]\n")

    return (min_lon, max_lon, min_lat, max_lat)


# ===============================
# Metodo original DEM (SIN CAMBIOS)
# ===============================
def get_base_distance_and_window(lon, lat, buffer_deg=0.2):
    try:
        hgt_files = glob.glob("GEOC/*.geo.hgt.tif") + glob.glob("GEOC/geo/*.geo.hgt.tif")
        if not hgt_files:
            raise FileNotFoundError("No se encontraron archivos .geo.hgt.tif")

        hgt_path = hgt_files[0]
        with rasterio.open(hgt_path) as src:
            min_lon = lon - buffer_deg
            max_lon = lon + buffer_deg
            min_lat = lat - buffer_deg
            max_lat = lat + buffer_deg

            elevacion = src.read(1)
            elevacion = np.where(elevacion == src.nodata, np.nan, elevacion)

            maxelevacion = np.nanmax(elevacion)
            minelevacion = np.nanmin(elevacion)

            h_cima_adj = maxelevacion + 10
            h_base_adj = max(minelevacion - 10, 0)

            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            elevation = src.read(1, window=window)
            elevation = np.where(elevation == src.nodata, np.nan, elevation)

            h_base = np.nanpercentile(elevation, 10)
            mask_base = elevation <= h_base

            rows_base, cols_base = np.where(mask_base)

            distances = []
            for r, c in zip(rows_base, cols_base):
                row_global = r + window.row_off
                col_global = c + window.col_off
                lon_pix, lat_pix = src.xy(row_global, col_global)
                _, _, dist_m = geod.inv(lon, lat, lon_pix, lat_pix)
                distances.append(dist_m)

            max_dist = max(distances)

            cut_size_deg = max_dist / 111000
            half = cut_size_deg / 2

            cut_bounds = (
                lon - half,
                lon + half,
                lat - half,
                lat + half
            )

            return window, cut_bounds, hgt_path

    except Exception as e:
        print(f"Error procesando DEM: {e}")
        return None, None, None


# ===============================
# Recorte + estadísticas
# ===============================
def crop_and_calculate_average(file_path, bounds, save_image=False):
    try:
        with rasterio.open(file_path) as src:
            min_lon, max_lon, min_lat, max_lat = bounds
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            data = src.read(1, window=window)
            data = np.where(data == src.nodata, np.nan, data)

            if data.size == 0 or np.all(np.isnan(data)):
                return None, None

            norm_factor = np.nanmax(data)
            if norm_factor == 0 or np.isnan(norm_factor):
                return None, None

            data_norm = data / norm_factor
            average = np.nanmean(data_norm)
            standar = np.nanstd(data_norm)

            if save_image:
                plt.imshow(data_norm)
                plt.colorbar()
                plt.title(f"{file_path.stem} Avg: {average:.3f}")
                plt.savefig(f"{file_path.parent}/recorte_{file_path.stem}.png", dpi=100)
                plt.close()

            return average, standar

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None, None


# ===============================
# MAIN
# ===============================
def main():
    current_dir = os.getcwd()
    default_volcano_name = os.path.basename(os.path.dirname(current_dir))

    fixed_area_km = None

    if len(sys.argv) == 2:
        try:
            fixed_area_km = float(sys.argv[1])
            volcano_name = get_volcano_name_from_file(name_file) or default_volcano_name
        except ValueError:
            volcano_name = sys.argv[1]

    elif len(sys.argv) >= 3:
        volcano_name = sys.argv[1]
        fixed_area_km = float(sys.argv[2])

    else:
        volcano_name = get_volcano_name_from_file(name_file) or default_volcano_name

    print(f"Volcán: {volcano_name}")

    volcano_info = get_volcano_info(volcano_name, volcanoes_file)
    if not volcano_info:
        print("Volcán no encontrado.")
        return

    nombre_volcan, lon, lat, _ = volcano_info
    print(f"Procesando {nombre_volcan} ({lon}, {lat})")

    # --- Selección de método de recorte ---
    if fixed_area_km is not None:
        cut_bounds = get_fixed_window_from_km(lon, lat, fixed_area_km)
    else:
        _, cut_bounds, _ = get_base_distance_and_window(lon, lat)
        if cut_bounds is None:
            print("No se pudo definir área de recorte.")
            return

    with open(input_txt, "r") as f:
        date_paths = f.read().splitlines()

    results = []
    resultsstd = []

    for i, date_path in enumerate(date_paths):
        file_path = Path(f"GEOC/{date_path}/{date_path}.geo.cc.tif")
        if not file_path.exists():
            continue

        avg, std = crop_and_calculate_average(
            file_path,
            cut_bounds,
            save_image=(i == 0)
        )

        if avg is not None:
            results.append(f"{date_path} {avg:.4f}\n")
            resultsstd.append(f"{date_path} {std:.4f}\n")

    with open(output_txt, "w") as f:
        f.writelines(results)

    with open(output_txt_std, "w") as f:
        f.writelines(resultsstd)


if __name__ == "__main__":
    main()
