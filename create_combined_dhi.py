#!/usr/bin/env python
# -*- coding: utf-8 -*-

#******************************************************************************
#
# create_combined_dhi.py
# ---------------------------------------------------------
# Create combined DHI product
# More: http://github.com/nextgis/dhi
#
# Usage: 
#      create_combined_dhi.py input_folder output_folder1 output_folder2 suffix product
#      where:
#           input_folder    input folder
#           output_folder1  where to store TIFs for each time slice
#           output_folder2  where to store the result
#           suffix          suffix to end to resulting file name
#           product         product code used in folder name
# Example:
#      python create_combined_dhi.py x:\MCD15A2\ x:\MCD15A2\combined\fpar8\ y:\dhi\global\fpar_8\combined-v2\ fpar8 fpar
#
# Copyright (C) 2015 Maxim Dubinin (sim@gis-lab.info)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

'''Prepare DHI data from stacks of TIFs. To run:
   
input_folder - where are input TIFs
output_folder1 - where to store TIFs for each time slice
output_folder2 - where to store resulting TIFs
suffix - suffix for output names
product - short name for product
'''

import os
import sys
import glob
import time
import shutil

#prepare environment
gisbase = os.environ['GISBASE'] = "c:/tools/NextGIS_QGIS/apps/grass/grass-6.4.4/"
gisdbase = os.environ['GISDBASE'] = "e:/users/maxim/thematic/dhi/"
location = "dhi_grass"
mapset   = "PERMANENT"

sys.path.append(os.path.join(gisbase, "etc", "python"))
 
import grass.script as grass
import grass.script.setup as gsetup
gsetup.init(gisbase, gisdbase, location, mapset)

id = sys.argv[1]
od1 = sys.argv[2]
od2 = sys.argv[3]
prefix = 'dhi'
suffix = sys.argv[4]
product = sys.argv[5]
os.chdir(id)

years = range(2003,2014+1)
numslices = len(glob.glob(str(years[0]) + '/tif-' + product + '-qa/' + '*.tif'))

for year in years:
    i = 0
    for f in glob.glob(str(year) + '/tif-' + product + '-qa/' + '*.tif'):
        i+=1
        grass.run_command('r.in.gdal', input=f, output=str(year) + '_' + str(i))

#Calculate counts and medians for N time slices
for i in range(1,numslices+1):
    list = ''
    for year in years:
        list = list + ',' + str(year) + '_' + str(i)
    list = list.strip(',')
    
    grass.run_command('r.series', input=list, output=str(i) + '_cnt,' + str(i) + '_med', method='count,median')

#Filter out pixels where count is 3 and less
for i in range(1,numslices+1):
    grass.mapcalc(str(i) + '_f' ' = if(' + str(i) + '_cnt>3, ' + str(i) + '_med, null())')


#export averaged rasters
#for i in range(1,numslices+1):
#    grass.run_command('r.out.gdal', input=str(i)+'_med', output=od1 + str(i) + '_med.tif', type='Byte', createopt='PROFILE=BASELINE,INTERLEAVE=PIXEL,TFW=YES')
#    grass.run_command('r.out.gdal', input=str(i)+'_avg', output=od1 + str(i) + '_avg.tif', type='Byte', createopt='PROFILE=BASELINE,INTERLEAVE=PIXEL,TFW=YES')
    
#    cmd = "gdal_edit -a_srs \"EPSG:4326\" " + od1 + str(i) + '_med.tif'
#    os.system(cmd)
#    cmd = "gdal_edit -a_srs \"EPSG:4326\" " + od1 + str(i) + '_avg.tif'
#    os.system(cmd)
    
#for t in ['med','avg']:
fn_out = prefix + '_' + suffix + '_f.tif'

t = '_f'
list = ''
for i in range(1,numslices+1):
    list = list + ',' + str(i) + t
    
list = list.strip(',')

grass.run_command('r.series', input=list, output='dh1' + t + ',dh2' + t + ',ave' + t + ',std' + t, method='sum,minimum,average,stddev')
grass.mapcalc('dh3' + t + ' = std' + t + '/ave' + t)


grass.run_command('i.group', group='rgb_group' + t, input='dh1' + t + ',dh2' + t + ',dh3' + t)
grass.run_command('r.out.gdal', input='rgb_group' + t, output=fn_out, type='Float32', createopt='PROFILE=BASELINE,INTERLEAVE=PIXEL,TFW=YES')
shutil.move(fn_out,od2 + fn_out)
shutil.move(fn_out + '.aux.xml',od + fn_out + '.aux.xml')

shutil.move(fn_out.replace('.tif','.tfw'),od2 + fn_out.replace('.tif','.tfw'))

cmd = "gdal_edit -a_srs \"EPSG:4326\" " + od2 + fn_out
os.system(cmd)

