import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import box
import earthpy.spatial as es
import matplotlib as mpl
from cmcrameri import cm
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import matplotlib.ticker as ticker
from osgeo import gdal
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.gridspec as gridspec


def add_scalebar(ax, lat, length_fraction=0.25, position="upper left"):
    """
    Añade una barra de escala en kilómetros adaptada a mapas en coordenadas geográficas (°).

    Parámetros:
    -----------
    ax : matplotlib axes
        Eje o inset al que añadir la barra.
    lat : float
        Latitud del centro del mapa (para calcular km/°).
    length_fraction : float
        Proporción del ancho del mapa que ocupa la barra.
    position : str
        Posición ('upper left', 'upper right', etc.).
    """
    deg_to_km = 111.32 * np.cos(np.deg2rad(lat))

    scalebar = ScaleBar(
        dx=deg_to_km * 1000,   # convierte grados a metros
        units="m",
        dimension="si-length",
        scale_loc="bottom",
        length_fraction=length_fraction,
        location=position,
        box_alpha=1,
        color="black",
        label=None,
        fixed_units="km",
        font_properties={'size': 8},   # texto pequeño
    )
    ax.add_artist(scalebar)

def opentif(path):
	
	Ori = gdal.Open(path)
	mOri = np.array(Ori.ReadAsArray(), dtype=float)
	mOri[mOri == 0.] = np.nan
	return mOri
	
def minmax(path):
    Ori = gdal.Open(path)
    mOri = np.array(Ori.ReadAsArray(), dtype=float)

    # mask zeros
    mOri[mOri == 0] = np.nan

    # compute min and max ignoring NaN
    vmin = np.nanmin(mOri)
    vmax = np.nanmax(mOri)

    return vmin, vmax


def opentxt(path):

	# Load the file, skipping lines starting with '#'
	df = pd.read_csv(path,
	    sep=r"\s+",
	    comment="#",
	    header=None,
	    names=["date", "cum"]
	)
	
	# Convert YYYYMMDD → datetime
	df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
	
	return df
	

Original="Resultados/Original.cum.geo.tif"
Originaltxt="Resultados/Original.txt"
All="Resultados/All.cum.geo.tif"
Alltxt="Resultados/All.txt"
GACOS="Resultados/GACOS.cum.geo.tif"
GACOStxt="Resultados/GACOS.txt"
ERA5="Resultados/ERA5.cum.geo.tif"
ERA5txt="Resultados/ERA5.txt"
dem_path="TS_GEOCml2mask/results/hgt.geo.tif"
azimuth = -167.92738  # for hillshade
point=[110.45084,-7.54581]
reference=[110.51996,-7.61061]




# === Read DEM ===
with rio.open(dem_path) as src:
    elevation = src.read(1)  # read the first (and usually only) band
    elevation[elevation < 0] = np.nan  # mask negative values

    # Compute hillshade
    hillshade = es.hillshade(elevation, azimuth=azimuth)

    # Extent for imshow
    extent = [
        src.bounds.left,
        src.bounds.right,
        src.bounds.bottom,
        src.bounds.top
    ]


vmin, vmax = minmax(Original)

# === Plotting ===
fig = plt.figure(figsize=(14, 10),constrained_layout=True)

grid = gridspec.GridSpec(2,4, height_ratios=[1,1], width_ratios=[1,1,1,1])



ax0 = fig.add_subplot(grid[0,0])
ax0.imshow(hillshade, cmap='Greys', alpha=0.7, extent=extent)
ax0.imshow(elevation, cmap='Greys', alpha=0.5, extent=extent)
add_scalebar(ax0, lat=-1.45, position="upper right")
ax0.scatter(point[0],point[1],s=60, marker='.', color='cyan', label="Standard")
ax0.scatter(reference[0],reference[1],s=10, marker='s', color='black', label="Reference")
ax0.legend(frameon=False, loc='lower left')
ax0.imshow(opentif(All),extent=extent,interpolation="nearest",cmap=cm.roma_r, alpha=0.8, vmin=vmin, vmax=vmax)


ax1 = fig.add_subplot(grid[0,1])
# DEM and hillshade
ax1.imshow(hillshade, cmap='Greys', alpha=0.7, extent=extent)
ax1.imshow(elevation, cmap='Greys', alpha=0.5, extent=extent)
#add_scalebar(ax1, lat=-1.45) 
ax1.scatter(point[0],point[1],s=60, marker='.', color='red', label="Original")
ax1.scatter(reference[0],reference[1],s=10, marker='s', color='black')
ax1.legend(frameon=False, loc='upper right')
    # plotear en el inset correspondiente
ax1.set_yticklabels([])

imv=ax1.imshow(opentif(Original),extent=extent,interpolation="nearest",cmap=cm.roma_r, alpha=0.8, vmin=vmin, vmax=vmax)

# Add custom colorbar axes [left, bottom, width, height] in figure coordinates (0–1)
#cbar_ax = fig.add_axes([0.59, 0.27, 0.012, 0.18])  # Adjust x, y, width, height




ax2 = fig.add_subplot(grid[0,2])
ax2.imshow(hillshade, cmap='Greys', alpha=0.7, extent=extent)
ax2.imshow(elevation, cmap='Greys', alpha=0.5, extent=extent)
ax2.imshow(opentif(GACOS),extent=extent,interpolation="nearest",cmap=cm.roma_r, alpha=0.8, vmin=vmin, vmax=vmax)
ax2.set_yticklabels([])
ax2.scatter(point[0],point[1],s=60, marker='.', color='blue', label="GACOS")
ax2.scatter(reference[0],reference[1],s=10, marker='s', color='black')
ax2.legend(frameon=False, loc='upper right')

ax3 = fig.add_subplot(grid[0,3])
ax3.imshow(hillshade, cmap='Greys', alpha=0.7, extent=extent)
ax3.imshow(elevation, cmap='Greys', alpha=0.5, extent=extent)
ax3.imshow(opentif(ERA5),extent=extent,interpolation="nearest",cmap=cm.roma_r, alpha=0.8, vmin=vmin, vmax=vmax)
ax3.set_yticklabels([])
ax3.scatter(point[0],point[1],s=60, marker='.', color='green', label="ERA5")
ax3.scatter(reference[0],reference[1],s=10, marker='s', color='black')
ax3.legend(frameon=False, loc='upper right')

ax4 = fig.add_subplot(grid[1, :])

df  = opentxt(Originaltxt)
dfG = opentxt(GACOStxt)
dfE = opentxt(ERA5txt)
dfA  = opentxt(Alltxt)


# Plot each with style variations
ax4.plot(dfA["date"],  dfA["cum"],  marker="o",  markersize=5,
         linestyle="-", linewidth=0.5, markerfacecolor='none', markeredgecolor="cyan",   label="Standard", color="cyan")


ax4.plot(df["date"],  df["cum"],  marker="o",  markersize=5,
         linestyle="-", linewidth=0.5, markerfacecolor='none', markeredgecolor="red",   label="Original", color="red")

ax4.plot(dfG["date"], dfG["cum"], marker="s", markersize=5,
         linestyle="--", linewidth=0.5, markerfacecolor='none', markeredgecolor="blue",  label="GACOS",color="blue")

ax4.plot(dfE["date"], dfE["cum"], marker="^", markersize=5,
         linestyle=":", linewidth=0.5, markerfacecolor='none', markeredgecolor="green", label="ERA5",color="green")

# Improve readability
ax4.grid(True, linestyle="--", alpha=0.4)
ax4.set_xlabel("Dates")
ax4.set_ylabel("Cumulative (mm)")
ax4.axvline(x=(pd.to_datetime(20201231, format="%Y%m%d")), color='black', linestyle='--', label="Eruptions", alpha=0.5, lw=1)
ax4.axvline(x=(pd.to_datetime(20200104, format="%Y%m%d")), color='black', linestyle='--', alpha=0.5,lw=1)
ax4.axvline(x=(pd.to_datetime(20180511, format="%Y%m%d")), color='black', linestyle='--', alpha=0.5,lw=1)

# Legend
ax4.legend(loc="upper left")

# --- YEAR TICKS ---
ax4.xaxis.set_major_locator(mdates.YearLocator())          # one tick per year
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # show only the year

grid.update(wspace=0,hspace=0.07)

cbar = plt.colorbar(imv, ax=[ax0,ax1,ax2,ax3], orientation='horizontal', shrink=0.5, pad=0.1, fraction=0.03)

# Añadir "mm" a la derecha
cbar.ax.text(1.02, 0.5, "mm",transform=cbar.ax.transAxes,va='center', ha='left')

fig.savefig('Merapi.jpg', format='jpg', dpi=200, bbox_inches='tight', transparent=True)
plt.show()
