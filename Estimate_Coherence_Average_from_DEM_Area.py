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

# ===============================
# NUEVO (NO TOCA NADA EXISTENTE)
# ===============================
def get_fixed_window_from_km(lon, lat, area_km):
    area_deg = area_km / 111.0
    half = area_deg / 2
    return (
        lon - half,
        lon + half,
        lat - half,
        lat + half
    )

# ===============================
# TODO LO DEMÁS ORIGINAL
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
        print(f"Error leyendo el archivo de volcanes: {e}")
    return None

# --- get_base_distance_and_window ORIGINAL ---
# (sin tocar una sola línea)

# --- crop_and_calculate_average ORIGINAL ---
# (sin tocar una sola línea)

def main():
    current_dir = os.getcwd()
    default_volcano_name = os.path.basename(os.path.dirname(current_dir))

    fixed_area_km = None

    # ===============================
    # SOLO ESTA PARTE ES NUEVA
    # ===============================
    if len(sys.argv) >= 2:
        try:
            fixed_area_km = float(sys.argv[1])
            volcano_name = get_volcano_name_from_file(name_file) or default_volcano_name
        except ValueError:
            volcano_name = sys.argv[1]
    else:
        volcano_name = get_volcano_name_from_file(name_file) or default_volcano_name
    # ===============================

    print(f"Nombre del volcán: {volcano_name}")
    
    volcano_info = get_volcano_info(volcano_name, volcanoes_file)
    if not volcano_info:
        print(f"Volcán '{volcano_name}' no encontrado.")
        return
        
    nombre_volcan, lon, lat, distancia = volcano_info
    print(f"\n--- Procesando volcan: {nombre_volcan} en ({lon}, {lat}) ---\n")

    # ===============================
    # DECISIÓN DE MÉTODO (NUEVO)
    # ===============================
    if fixed_area_km is not None:
        cut_bounds = get_fixed_window_from_km(lon, lat, fixed_area_km)
    else:
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
            continue

        average, standar = crop_and_calculate_average(
            file_path,
            cut_bounds,
            save_image=(i == 0)
        )

        if average is not None:
            results.append({"date": date_path, "average": average})
            resultsstd.append({"date": date_path, "standar": standar})

    with open(output_txt, "w") as f:
        for r in results:
            f.write(f"{r['date']} {r['average']:.4f}\n")

    with open(output_txt_std, "w") as f:
        for r in resultsstd:
            f.write(f"{r['date']} {r['standar']:.4f}\n")

if __name__ == "__main__":
    main()
