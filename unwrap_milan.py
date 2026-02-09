import os
import sys
from lics_unwrap import process_ifg_pair

# Captura el argumento de línea de comandos
if len(sys.argv) < 2:
    print("Uso: python unwrap_milan.py <carpeta>")
    sys.exit(1)

folder = sys.argv[1]  # esto reemplaza el $1 de Bash

# Construye los nombres de archivo dinámicamente
wrapinput = f"GEOC/{folder}/{folder}.geo.diff_unfiltered_pha.tif"
ccinput = f"GEOC/{folder}/{folder}.geo.cc.tif"
outtif = f"GEOC/{folder}/{folder}.geo.unw.tif"

# Llamada a la función
process_ifg_pair(
    wrapinput,
    ccinput,
    procpairdir=os.getcwd(),
    landmask_tif=None,
    magtif=None,
    ml=1,
    fillby='gauss',
    thres=0.2,
    cascade=False,
    smooth=False,
    lowpass=True,
    goldstein=True,
    specmag=False,
    spatialmask_km=2.0,
    defomax=0.6,
    frame='',
    hgtcorr=False,
    gacoscorr=True,
    pre_detrend=True,
    cliparea_geo=None,
    outtif=outtif,
    prevest=None,
    prev_ramp=None,
    coh2var=False,
    add_resid=True,
    rampit=False,
    subtract_gacos=False,
    extweights=None,
    keep_coh_debug=True,
    keep_coh_px=0.25,
    use_gamma=False
)
