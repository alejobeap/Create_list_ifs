import sys
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
from rasterio.windows import from_bounds
import glob

# Archivos de entrada y salida
volcanoes_file = "Volcanes_Chiles.txt"
input_txt = "combination_shorts.txt"
output_txt = "output_averages_from_cc_tifs.txt"
output_txt_std = "output_std_from_cc_tifs.txt"

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

def get_cima_to_base_mask(lon, lat, buffer_deg=0.2):
    """Crea una máscara desde la cima hasta la base del volcán (zonas más bajas)."""
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

            window = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
            elevation = src.read(1, window=window)
            elevation = np.where(elevation == src.nodata, np.nan, elevation)

            # Obtener índice relativo dentro de la ventana
            row_cima, col_cima = src.index(lon, lat)
            row_min, col_min = src.index(min_lon, max_lat)
            rel_row = row_cima - row_min
            rel_col = col_cima - col_min

            if (0 <= rel_row < elevation.shape[0]) and (0 <= rel_col < elevation.shape[1]):
                h_cima = elevation[rel_row, rel_col]
                if np.isnan(h_cima):
                    raise ValueError("La elevación en la cima es NaN")
            else:
                raise ValueError("Coordenadas de la cima fuera del rango de la ventana")

            h_base = np.nanpercentile(elevation, 10)
            mask = (elevation <= h_cima) & (elevation >= h_base)

            print(f"Archivo HGT usado: {hgt_path}")
            print(f"Cima: {h_cima:.1f} m, Base (P10): {h_base:.1f} m")
            print(f"Píxeles válidos en máscara: {np.sum(mask)}")

            return mask, window, hgt_path
    except Exception as e:
        print(f"Error procesando elevación: {e}")
        return None, None, None

def crop_and_calculate_average(file_path, window, mask, save_image=False):
    try:
        with rasterio.open(file_path) as src:
            data = src.read(1, window=window)
            data = np.where(data == src.nodata, np.nan, data)

            if data.shape != mask.shape:
                print(f"Shape mismatch: data {data.shape}, mask {mask.shape}")
                return None, None

            masked_data = data[mask]

            if masked_data.size == 0 or np.all(np.isnan(masked_data)):
                print(f"Advertencia: No hay datos válidos en {file_path.name}")
                return None, None

            norm_factor = np.nanmax(masked_data)
            if np.isnan(norm_factor) or norm_factor == 0:
                print(f"Advertencia: np.nanmax es inválido o cero en {file_path.name}")
                return None, None

            masked_data = masked_data / norm_factor
            average = np.nanmean(masked_data)
            standar = np.nanstd(masked_data)

            if save_image:
                plt.figure(figsize=(8, 6))
                vis_data = np.full_like(data, np.nan)
                vis_data[mask] = masked_data
                plt.imshow(vis_data, cmap='viridis')
                plt.colorbar(label='Avg_Coh')
                plt.title(f"{file_path.stem} Avg_Coh: {average:.3f}")
                plt.savefig(f"{file_path.parent}/recorte_{file_path.stem}.png", dpi=100)
                plt.close()

            return average, standar
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None, None

def main():
    if len(sys.argv) < 2:
        print("Uso: python Estimate_Coherence_Average_from_DEM.py <Nombre_volcan>")
        return

    volcano_name = sys.argv[1]
    volcano_info = get_volcano_info(volcano_name, volcanoes_file)

    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado.")
        return

    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"\n--- Procesando volcán: {nombre_volcan} en ({lon}, {lat}) ---\n")

    mask, window, hgt_used = get_cima_to_base_mask(lon, lat)
    if mask is None:
        print("No se pudo generar máscara de elevación.")
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
        average, standar = crop_and_calculate_average(file_path, window, mask, save_image=save_image)

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
