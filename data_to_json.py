#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import glob
import json
import os
import re
import sys
import h5py as h5
import netCDF4 as nc
import numpy as np
from scipy.interpolate import griddata

def get_distance(start_lat, start_lon, end_lat, end_lon,
                 use_km=True, use_round=False, earth_radius=6371e3):
    """
    Returns the distance between two points in m / km

    This uses the haversine method as described here:

      https://www.movable-type.co.uk/scripts/latlong.html
    """
    # Convert lats and lons to radians:
    lat_a = np.deg2rad(start_lat)
    lat_b = np.deg2rad(end_lat)
    lon_a = np.deg2rad(start_lon)
    lon_b = np.deg2rad(end_lon)
    # Differences in lat and lon values:
    d_lat = (lat_b - lat_a)
    d_lon = (lon_b - lon_a)
    # "Square of half the chord length between the points":
    var_a = (np.square(np.sin(d_lat / 2)) + np.cos(lat_a) * np.cos(lat_b)
             * np.square(np.sin(d_lon / 2)))
    # "Angular distance in radians":
    var_c = 2 * np.arctan2(np.sqrt(var_a), np.sqrt(1 - var_a))
    # Distance in metres:
    dist = earth_radius * var_c
    # Convert to km?:
    if use_km:
        dist = dist / 1000
    # Round?:
    if use_round:
        dist = np.round(dist)
    # Return the distance:
    return dist

# function to get dates:
def get_dates(h5_file, var_name, dict_name):
    # get h5 variable:
    h5_var = h5_file[var_name]
    # get values:
    h5_values = h5_var[()]
    # list for storing date strings:
    dates = []
    # for each value, convert to string and add dashes:
    for i in h5_values.astype(int):
        date_str = str(i)
        formatted_date = '{0}-{1}-{2}'.format(date_str[0:4], date_str[4:6],
                                              date_str[6:8])
        dates.append(formatted_date)
    # return dict:
    return {dict_name: dates}

# function for h5 var conversion to dict:
def var_to_dict(h5_file, var_name, dict_name, dtype=None, round=None,
                flipud=False):
    # get h5 variable:
    h5_var = h5_file[var_name]
    # get values:
    h5_values = h5_var[()]
    # if flipping y axis:
    if flipud:
        # presuming 3d array. '1' is y axis of each step:
        h5_values = np.apply_along_axis(np.flipud, 1, h5_values)
    # if type specified and rounding:
    if dtype and round:
        h5_values = h5_values.astype(dtype).round(round).tolist()
    # if just type:
    elif dtype:
        h5_values = h5_values.astype(dtype).tolist()
    # if just rounding:
    elif round:
        h5_values = h5_values.round(round).tolist()
    # else, just convert to list:
    else:
        h5_values = h5_values.tolist()
    # dict of values:
    var_dict = {dict_name: h5_values}
    # return the dict:
    return var_dict

# function to get x / y values:
def get_dim(h5_file, dim_name, dict_name):
    # get number of points from 'cum':
    if dict_name == 'x':
        var_sz = h5_file['cum'].shape[2]
    else:
        var_sz = h5_file['cum'].shape[1]
    # get corner / min value:
    var_name = 'corner_{0}'.format(dim_name)
    var_min = h5_file[var_name][()]
    # get offset / increment value:
    var_name = 'post_{0}'.format(dim_name)
    var_inc = h5_file[var_name][()]
    # create list of values:
    var_val = [round((i * var_inc) + var_min, 4) for i in range(0, var_sz)]
    # create dict:
    var_dict = {dict_name: var_val}
    # return the dict:
    return var_dict

# function to get gap dates:
def get_gaps():
    # init output dict:
    out_dict = {
        'gaps': []
    }
    # file containing gap info:
    gap_files = glob.glob('TS*/info/12network_gap_info.txt')
    if not gap_files:
        return out_dict
    gap_file = gap_files[0]
    # read in gap file and search for gaps:
    with open(gap_file, 'r') as gap_text:
        for gap_line in gap_text.readlines():
            gap_line = gap_line.strip()
            gap = re.findall(r'[0-9]{8}\s[0-9]{8}$', gap_line)
            if gap:
                gap_start, gap_end = gap[0].split()
                out_dict['gaps'].append([
                    '{0}-{1}-{2}'.format(
                        gap_start[0:4], gap_start[4:6], gap_start[6:8]
                    ),
                    '{0}-{1}-{2}'.format(
                        gap_end[0:4], gap_end[4:6], gap_end[6:8]
                    )
                ])
    # return the results dict:
    return out_dict

def main():
    # input files should be in here:
    out_dir = glob.glob('TS_GEOCml2mask*')[0]

    # input file:
    in_file = sys.argv[1]
    # output file:
    out_file = sys.argv[2]

    # coherence file:
    coh_file = '/'.join([out_dir, 'results/coh_avg'])
    # mask file:
    mask_file = '/'.join([out_dir, 'results/mask'])
    # elevation file:
    elev_file = '/'.join([out_dir, 'results/hgt'])
    # landmask file:
    landmask_file = 'landmask.nc'

    # output dict:
    out_dict = {}

    # open the hdf5 file:
    h5_file = h5.File(in_file, 'r')
    # get image dates and add to output dict:
    out_dict.update(get_dates(h5_file, 'imdates', 'dates'))
    # deformation data. different names for raw file and filtered file:
    if in_file.endswith('_filt.h5'):
        out_dict.update(var_to_dict(h5_file, 'cum', 'data_filt',
                                    dtype=float, flipud=False))
    else:
        out_dict.update(var_to_dict(h5_file, 'cum', 'data_raw',
                                    dtype=float, flipud=False))
    # add los information:
    out_dict.update(
        var_to_dict(
            h5_file, 'E.geo', 'e_geo', dtype=float, flipud=False
        )
    )
    out_dict.update(
        var_to_dict(
            h5_file, 'N.geo', 'n_geo', dtype=float, flipud=False
        )
    )
    out_dict.update(
        var_to_dict(
            h5_file, 'U.geo', 'u_geo', dtype=float, flipud=False
        )
    )
    # y / lat values ... get values and add to dict:
    out_dict.update(get_dim(h5_file, 'lat', 'y'))
    # x / lon values ... get values and add to dict:
    out_dict.update(get_dim(h5_file, 'lon', 'x'))
    # x / y distances:
    x_dist = get_distance(out_dict['y'][0], out_dict['x'][0],
                          out_dict['y'][0], out_dict['x'][-1])
    out_dict.update({'x_dist': x_dist})
    y_dist = get_distance(out_dict['y'][0], out_dict['x'][0],
                          out_dict['y'][-1], out_dict['x'][0])
    out_dict.update({'y_dist': y_dist})
    # refarea ... get value from file:
    h5_ref = h5_file['refarea'][()].decode()
    # split in to individual values:
    h5_ref = h5_ref.split('/')
    h5_ref_x = h5_ref[0].split(':')
    h5_ref_y = h5_ref[1].split(':')
    # create list and convert to int:
    ref_area = [h5_ref_x[0], h5_ref_x[1], h5_ref_y[0], h5_ref_y[1]]
    ref_area = list(map(int, ref_area))
    # add to dict:
    out_dict.update({'refarea': ref_area})
    # close hdf5 file:
    h5_file.close()

    # get coherence values from np image file. need x and y sizes:
    y_sz = len(out_dict['y'])
    x_sz = len(out_dict['x'])
    # read data from np file:
    coh_data = np.fromfile(coh_file, dtype=np.float32).reshape(y_sz, x_sz)
    # convert to float and add to dict:
    out_dict.update({'coh': coh_data.astype(float).tolist()})

    # read mask data from np file:
    mask_data = np.fromfile(mask_file, dtype=np.float32).reshape(y_sz, x_sz)
    # convert to int and add to dict:
    out_dict.update({'mask': mask_data.astype(int).tolist()})

    # read landmask from nc file, if exists:
    if os.path.exists(landmask_file):
        # read in landmask (1 = land, 0 = not land):
        lm_data = nc.Dataset(landmask_file)
        lm_lat = lm_data['lat'][:]
        lm_lon = lm_data['lon'][:]
        lm_mask = lm_data['Band1'][:]
        lm_mask.mask = False
        # meshgrid the lats and lons:
        lm_gridlon, lm_gridlat = np.meshgrid(lm_lon, lm_lat)
        out_gridlon, out_gridlat = np.meshgrid(out_dict['x'], out_dict['y'])
        # regrid to data resolution:
        lm_mask_out = griddata(
            (lm_gridlon.ravel(), lm_gridlat.ravel()), lm_mask.ravel(),
            (out_gridlon, out_gridlat), method='nearest', fill_value=np.nan
        )
        # add to dict:
        out_dict.update({'landmask': lm_mask_out.astype(int).tolist()})

    # read elevation data from np file, if exists:
    if os.path.exists(elev_file):
        elev_data = np.fromfile(elev_file, dtype=np.float32).reshape(y_sz, x_sz)
        # convert to float and add to dict:
        out_dict.update({'elev': elev_data.astype(float).tolist()})

    # get gap dates:
    out_dict.update(get_gaps())

    # add time stamp to output data:
    date_time = datetime.datetime.now()
    time_stamp = datetime.datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')
    out_dict.update({'timestamp': time_stamp})

    # open output file for writing:
    with open(out_file, 'w') as json_file:
        # json dump the data:
        json.dump(out_dict, json_file, separators=(',', ':'))

    # update file time stamp:
    os.utime(out_file, times=(date_time.timestamp(), date_time.timestamp()))

if __name__ == '__main__':
    main()
