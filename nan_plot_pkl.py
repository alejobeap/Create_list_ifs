#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import argparse
import os

# ============================
# Argumentos
# ============================
parser = argparse.ArgumentParser(description="Visualización de PKL de LiCSAlert/LiCSBAS")
parser.add_argument("pklfile", help="Path al archivo .pkl")
args = parser.parse_args()

pklfile = args.pklfile
if not os.path.exists(pklfile):
    raise FileNotFoundError(f"No existe el archivo: {pklfile}")

# ============================
# Abrir archivo PKL
# ============================
with open(pklfile, "rb") as f:
    displacement_r3 = pickle.load(f)  # diccionario con la serie temporal y datos geográficos
    tbaseline_info = pickle.load(f)    # información de fechas
    eruption_dates = pickle.load(f)    # opcional

# ============================
# Extraer datos
# ============================
# Serie acumulada (equivalente a 'cum' en h5)
cum = displacement_r3.get('cumulative')
if cum is None:
    raise ValueError("No se encuentra 'cumulative' en displacement_r3")

# Fechas
imdates = tbaseline_info['acq_dates']
imdates_dt = [dt.datetime.strptime(d, "%Y-%m-%d") for d in imdates]  # ya vienen en formato YYYY-MM-DD

n_im, length, width = cum.shape

# ============================
# Último mapa
# ============================
last_map = cum[-1]

# Pixel máximo
max_idx = np.nanargmax(last_map)
row_max, col_max = np.unravel_index(max_idx, last_map.shape)
ts_pixel = cum[:, row_max, col_max]
nan_count_pixel = np.isnan(ts_pixel).sum()

print(f"Pixel máximo: fila={row_max}, col={col_max}")
print(f"Valor máximo: {last_map[row_max, col_max]}")
print(f"NaNs en ese pixel: {nan_count_pixel} de {n_im}")

# Mapa de NaNs
nan_map = np.isnan(cum).any(axis=0)

# ============================
# FIGURA 4 PANELES
# ============================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel 1: Último mapa acumulado
im1 = axes[0,0].imshow(last_map, cmap='viridis')
axes[0,0].set_title("Último mapa acumulado")
fig.colorbar(im1, ax=axes[0,0])

# Panel 2: Mapa con pixel máximo
im2 = axes[0,1].imshow(last_map, cmap='viridis')
axes[0,1].scatter(col_max, row_max, s=100, c='red', marker='x')
axes[0,1].set_title("Pixel máximo marcado")
fig.colorbar(im2, ax=axes[0,1])

# Panel 3: Serie temporal del pixel máximo
axes[1,0].plot(imdates_dt, ts_pixel, '-o')
axes[1,0].set_title(f"Serie temporal del pixel máximo\nNaNs: {nan_count_pixel}")
axes[1,0].set_xlabel("Fecha")
axes[1,0].set_ylabel("Desplazamiento")
axes[1,0].tick_params(axis='x', rotation=45)

# Panel 4: Mapa de NaNs
im4 = axes[1,1].imshow(nan_map, cmap='Reds')
axes[1,1].set_title("Pixeles con al menos un NaN")
fig.colorbar(im4, ax=axes[1,1])

plt.tight_layout()
plt.show()
