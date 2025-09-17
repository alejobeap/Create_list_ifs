#!/usr/bin/env python3
# Check if there are IFS without loops and create a list of possible candidates

import glob
import numpy as np
import os


def get_ifgdates_from_folders(geoc_dir="GEOC"):
    """Obtiene interferogramas desde las carpetas GEOC/2* y guarda en listachech.txt"""
    ifgdates = []

    # Buscar carpetas GEOC/2*
    for folder in sorted(glob.glob(os.path.join(geoc_dir, "2*"))):
        if os.path.isdir(folder):
            ifgd = os.path.basename(folder)
            if len(ifgd) == 17 and ifgd[8] == "_":  # formato YYYYMMDD_YYYYMMDD
                ifgdates.append(ifgd)

    # Guardar en listachech.txt
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


def minimal_loops_for_no_loop_ifgs(ifgdates, no_loop_ifg):
    imdates = ifgdates2imdates(ifgdates)
    results = {}

    for ifgd in no_loop_ifg:
        f1 = ifgd[:8]
        f2 = ifgd[9:17]
        loop_found = False

        for f3 in imdates:
            if f3 in (f1, f2):
                continue

            cand12 = f1 + "_" + f2
            cand23 = f2 + "_" + f3
            cand13 = f1 + "_" + f3
            existing = set(ifgdates)

            # Guardamos todos, aunque falten
            ternas = []
            for cand in (cand12, cand23, cand13):
                if cand in existing:
                    ternas.append(cand)
                else:
                    ternas.append(cand + " [MISSING]")

            results[ifgd] = ternas
            loop_found = True
            break

        if not loop_found:
            results[ifgd] = []

    return results


if __name__ == "__main__":

    # 🔹 Leer interferogramas desde carpetas GEOC/2*
    ifgdates = get_ifgdates_from_folders("GEOC")

    # 🔹 Construir loop matrix
    Aloop = make_loop_matrix(ifgdates)
    if Aloop.size == 0:
        no_loop_ifg = ifgdates
    else:
        ns_loop4ifg = np.abs(Aloop).sum(axis=0)
        ixs_ifg_no_loop = np.where(ns_loop4ifg == 0)[0]
        no_loop_ifg = [ifgdates[ix] for ix in ixs_ifg_no_loop]

    # 🔹 Guardar interferogramas sin loops
    with open("no_loop_ifg_GEOC.txt", "w") as f:
        f.write("\n".join(no_loop_ifg))

    # 🔹 Sugerir interferogramas faltantes
    missing_ifgs = suggest_missing_ifgs(ifgdates)
    with open("missing_ifgs_GEOC.txt", "w") as f:
        f.write("\n".join(missing_ifgs))

    # 🔹 Loops mínimos
    minimal_loops = minimal_loops_for_no_loop_ifgs(ifgdates, no_loop_ifg)
    with open("minimal_loops_GEOC.txt", "w") as f:
        for loop in minimal_loops.values():
            if loop:
                f.write("\n".join(loop) + "\n")
