#!/usr/bin/env python3
# Check if there are IFS without loops and create a list of possible candidates

import glob
import numpy as np
import os
from datetime import datetime

# ------------------------------
# Funciones auxiliares de fechas
# ------------------------------
def parse_date(dstr):
    """Convierte YYYYMMDD a datetime"""
    return datetime.strptime(dstr, "%Y%m%d")

def months_between(d1, d2):
    """Diferencia en meses aproximada"""
    return abs((d1.year - d2.year) * 12 + (d1.month - d2.month))

# ------------------------------
# Funciones principales
# ------------------------------
def get_ifgdates_from_folders(geoc_dir="GEOC"):
    """Obtiene interferogramas desde las carpetas GEOC/2* y guarda en listachech.txt"""
    ifgdates = []

    for folder in sorted(glob.glob(os.path.join(geoc_dir, "2*"))):
        if os.path.isdir(folder):
            ifgd = os.path.basename(folder)
            if len(ifgd) == 17 and ifgd[8] == "_":  # formato YYYYMMDD_YYYYMMDD
                ifgdates.append(ifgd)

    with open("listachech.txt", "w") as f:
        f.write("\n".join(ifgdates))

    return sorted(set(ifgdates))

def ifgdates2imdates(ifgdates):
    primarylist = [ifgd[:8] for ifgd in ifgdates]
    secondarylist = [ifgd[-8:] for ifgd in ifgdates]
    return sorted(set(primarylist + secondarylist))

def make_loop_matrix(ifgdates):
    n_ifg = len(ifgdates)
    Aloop = []

    for ix_ifg12, ifgd12 in enumerate(ifgdates):
        f1 = ifgd12[0:8]
        f2 = ifgd12[9:17]

        ifgdates23 = [ifgd for ifgd in ifgdates if ifgd.startswith(f2)]
        for ifgd23 in ifgdates23:
            f3 = ifgd23[9:17]
            candidate_ifg13 = f1 + "_" + f3

            if candidate_ifg13 in ifgdates:
                ix_ifg23 = ifgdates.index(ifgd23)
                ix_ifg13 = ifgdates.index(candidate_ifg13)

                Aline = [0] * n_ifg
                Aline[ix_ifg12] = 1
                Aline[ix_ifg23] = 1
                Aline[ix_ifg13] = -1
                Aloop.append(Aline)

    return np.array(Aloop)

def suggest_missing_ifgs(ifgdates):
    missing_ifgs = set()
    for ifgd12 in ifgdates:
        f1 = ifgd12[:8]
        f2 = ifgd12[9:17]

        ifgdates23 = [ifgd for ifgd in ifgdates if ifgd.startswith(f2)]
        for ifgd23 in ifgdates23:
            f3 = ifgd23[9:17]
            candidate_ifg13 = f1 + "_" + f3
            if candidate_ifg13 not in ifgdates:
                missing_ifgs.add(candidate_ifg13)

    return sorted(missing_ifgs)

def minimal_loops_for_no_loop_ifgs(ifgdates, no_loop_ifg, max_months=13):
    """Genera loops mÃ­nimos para interferogramas sin loops, respetando orden temporal y lÃ­mite de meses"""
    imdates = ifgdates2imdates(ifgdates)
    results = {}

    for ifgd in no_loop_ifg:
        f1 = ifgd[:8]
        f2 = ifgd[9:17]
        d1 = parse_date(f1)
        d2 = parse_date(f2)

        # Solo permitir loops con f1 < f2
        if d1 >= d2:
            continue

        ternas_list = []
        for f3 in imdates:
            if f3 in (f1, f2):
                continue
            d3 = parse_date(f3)

            # Orden cronolÃ³gico f1 < f2 < f3
            if not (d1 < d2 < d3):
                continue

            # RestricciÃ³n de mÃ¡ximo 13 meses entre cualquier par
            if (months_between(d1, d2) > max_months or
                months_between(d2, d3) > max_months or
                months_between(d1, d3) > max_months):
                continue

            cand12 = f1 + "_" + f2
            cand23 = f2 + "_" + f3
            cand13 = f1 + "_" + f3

            ternas_list.append([cand12, cand23, cand13])

        results[ifgd] = ternas_list

    return results

# ------------------------------
# Script principal
# ------------------------------
if __name__ == "__main__":

    # Leer interferogramas desde carpetas GEOC/2*
    ifgdates = get_ifgdates_from_folders("GEOC")

    #  Construir loop matrix
    Aloop = make_loop_matrix(ifgdates)
    if Aloop.size == 0:
        no_loop_ifg = ifgdates
    else:
        ns_loop4ifg = np.abs(Aloop).sum(axis=0)
        ixs_ifg_no_loop = np.where(ns_loop4ifg == 0)[0]
        no_loop_ifg = [ifgdates[ix] for ix in ixs_ifg_no_loop]

    # Guardar interferogramas sin loops
    with open("no_loop_ifg_GEOC.txt", "w") as f:
        f.write("\n".join(no_loop_ifg))

    # Sugerir interferogramas faltantes
    missing_ifgs = suggest_missing_ifgs(ifgdates)
    with open("missing_ifgs_GEOC.txt", "w") as f:
        f.write("\n".join(missing_ifgs))

    # Loops mi­nimos respetando orden temporal y lÃ­mite de 13 meses
    minimal_loops = minimal_loops_for_no_loop_ifgs(ifgdates, no_loop_ifg, max_months=13)
    with open("minimal_loops_GEOC.txt", "w") as f:
       for loops in minimal_loops.values():
        # Tomamos solo las primeras 5 conexiones
           for loop in loops[:5]:
               f.write("\n".join(loop) + "\n")
