import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Define file paths
# Get the parent and current directory names
current_dir = os.path.basename(os.getcwd())
parent_dir = os.path.basename(os.path.dirname(os.getcwd()))
mean_file = f"Longs_mean_value_{parent_dir}_{current_dir}.txt"

# Check if mean file exists
if not os.path.isfile(mean_file):
    print(f"Error: Mean value file {mean_file} does not exist.")
    sys.exit(1)

# Read the mean value from the text file
try:
    with open(mean_file, 'r') as file:
        mean_value = float(file.readline().split()[0])  # Assumes the format is "Mean: value"
    print(f"Mean value read from file: {mean_value}")
except Exception as e:
    print(f"Error reading mean value from file: {e}")
    sys.exit(1)


# Cargar los datos del archivo
file_path = "output_averages_from_cc_tifs.txt"
data = []

with open(file_path, "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 2:
            dates, value = parts
            date1, date2 = dates.split("_")
            data.append([date1, date2, float(value)])

# Crear un DataFrame
df = pd.DataFrame(data, columns=["date1", "date2", "coherence"])

# Crear una matriz de coherencia
unique_dates1 = sorted(df["date1"].unique())
unique_dates2 = sorted(df["date2"].unique())
matrix = np.full((len(unique_dates1), len(unique_dates2)), np.nan)

matrix_filt = np.full((len(unique_dates1), len(unique_dates2)), np.nan)

nifgs=0
# Rellenar la matriz con los valores de coherencia
for _, row in df.iterrows():
    i = unique_dates1.index(row["date1"])
    j = unique_dates2.index(row["date2"])
    matrix[i, j] = row["coherence"]
    nifgs=nifgs+1

# Graficar la matriz
plt.figure(figsize=(30, 20))
cmap = plt.cm.viridis
plt.imshow(matrix, cmap=cmap, aspect="auto", origin="upper")

# AÃ±adir etiquetas a los ejes
plt.xticks(ticks=range(len(unique_dates2)), labels=unique_dates2, rotation=90, fontsize=7)
plt.yticks(ticks=range(len(unique_dates1)), labels=unique_dates1, fontsize=7)
plt.colorbar(label="Coherence")
plt.title(f"Coherence Matrix (All longs IFS:{nifgs})")
plt.xlabel("Date2")
plt.ylabel("Date1")

# Add `nigs` value in the top-left corner
#plt.text(
#    x=-0.1,  # Adjust based on plot dimensions
#    y=1.05,  # Adjust based on plot dimensions
#    s=f"IFS: {nifgs}", 
#    fontsize=10, 
#    transform=plt.gca().transAxes  # Use axes-relative coordinates
#)


# Guardar la imagen
plt.tight_layout()

output_file = f"Longs_matrix_{parent_dir}_{current_dir}.png"

#output_file = "mnatris.png"
plt.savefig(output_file, dpi=100)
plt.close()

print(f"Imagen guardada como {output_file}")




nifgs=0
# Rellenar la matriz con los valores de coherencia
for _, row in df.iterrows():
    if row["coherence"]>mean_value:
      i = unique_dates1.index(row["date1"])
      j = unique_dates2.index(row["date2"])
      matrix_filt[i, j] = row["coherence"]
      nifgs=nifgs+1
    else:
      continue


# Graficar la matriz
plt.figure(figsize=(30, 20))
cmap = plt.cm.viridis
plt.imshow(matrix_filt, cmap=cmap, aspect="auto", origin="upper")

# AÃ±adir etiquetas a los ejes
plt.xticks(ticks=range(len(unique_dates2)), labels=unique_dates2, rotation=90, fontsize=7)
plt.yticks(ticks=range(len(unique_dates1)), labels=unique_dates1, fontsize=7)
plt.colorbar(label="Coherence")
plt.title(f"Filter Coherence Matrix (IFS:{nifgs})")
plt.xlabel("Date2")
plt.ylabel("Date1")

# Add `nigs` value in the top-left corner
#plt.text(
#    x=-0.1,  # Adjust based on plot dimensions
#    y=1.05,  # Adjust based on plot dimensions
#    s=f"IFS: {nifgs}",
#    fontsize=10,
#    transform=plt.gca().transAxes  # Use axes-relative coordinates
#)


# Guardar la imagen
plt.tight_layout()

output_file = f"Longs_filtered_matrix_{parent_dir}_{current_dir}.png"

#output_file = "filtered_matriz.png"
plt.savefig(output_file, dpi=100)
plt.close()

print(f"Imagen guardada como {output_file}")
