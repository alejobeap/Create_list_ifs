module load licsbas_comet_dev
./batch_LiCSBAS.sh
#LiCSBAS_flt2geotiff.py -i TS_GEOCml1clip/results/vel.filt.mskd -p GEOCml1clip/EQA.dem_par -o 083D_13222_131313.vel_filt.mskd.geo.tif
#LiCSBAS_flt2geotiff.py -i TS_GEOCml1clip/results/vel.filt -p GEOCml1clip/EQA.dem_par -o 083D_13222_131313.vel_filt.geo.tif
#LiCSBAS_flt2geotiff.py -i TS_GEOCml1clip/results/vel.mskd -p GEOCml1clip/EQA.dem_par -o 083D_13222_131313.vel.mskd.geo.tif
#LiCSBAS_flt2geotiff.py -i TS_GEOCml1clip/results/vel -p GEOCml1clip/EQA.dem_par -o 083D_13222_131313.vel.geo.tif
#LiCSBAS_flt2geotiff.py -i TS_GEOCml1clip/results/vstd -p GEOCml1clip/EQA.dem_par -o 083D_13222_131313.vstd.geo.tif
#cp TS_GEOCml1clip/network/network13.png 083D_13222_131313'_network.png'
#cp TS_GEOCml1clip/mask_ts.png 083D_13222_131313'_mask_ts.png'
#LiCSBAS_out2nc.py -i TS_GEOCml1clip/cum.h5 -o 083D_13222_131313.nc
#LiCSBAS_disp_img.py -i TS_GEOCml1clip/results/vel.filt.mskd -p GEOCml1clip/EQA.dem_par -c SCM.roma_r --cmin -20 --cmax 20 --kmz 083D_13222_131313.vel.mskd.kmz
#LiCSBAS_disp_img.py -i TS_GEOCml1clip/results/vel.filt.mskd -p GEOCml1clip/EQA.dem_par -c SCM.roma_r --cmin -20 --cmax 20 --title 083D_13222_131313_vel_filt_mskd --png 083D_13222_131313.vel.mskd.png
