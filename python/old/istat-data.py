#! /usr/bin/env python3

import geopandas as gpd
import argparse
import glob
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", help="ISTAT metadata type regex", required=True)
args = parser.parse_args()

shapefiles = sorted(glob.glob(args.data))
for f in shapefiles:
  base = f[:f.rfind('.')]
  print('[dataISTAT] Processing file : {}'.format(f), flush=True)

  ti = datetime.now()

  if 'SezIta' in f:
    df = gpd.read_file(f)
    #df = df.head(10)
    df['geometry'] = df['geometry'].to_crs({'init': 'epsg:4326'})
    #print(df.columns)
    #returns : ['OBJECTID', 'PERIMETER', 'COD_REG', 'COD_ISTAT', 'PRO_COM', 'SEZ', 'SEZ2011', 'X_WGS84', 'Y_WGS84', 'ORIG_FID', 'geometry']
    df['lon'] = df.geometry.centroid.x
    df['lat'] = df.geometry.centroid.y
    df['custom'] = [ '{:03}{:06}C{:03}'.format(r, pc, s) for r, pc, s in df[['COD_REG', 'PRO_COM', 'SEZ']].values ]
    df = df.sort_values(['custom'])
    df[['COD_REG', 'COD_ISTAT', 'PRO_COM', 'SEZ', 'custom', 'lat', 'lon']].to_csv(base + '.csv', sep=';', header=True, index=False)
  else:
    pass

  print('[dataISTAT] Done in {} s'.format(datetime.now() - ti), flush=True)