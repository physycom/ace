#! /usr/bin/env python3

import geopandas as gpd
import argparse
import glob

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--shp", help="ISTAT shapefile regex", required=True)
args = parser.parse_args()

shapefiles = sorted(glob.glob(args.shp))

for f in shapefiles:
  print('Processing {}'.format(f))
  df_shp = gpd.read_file(f)
#  df_shp = df_shp[[
#    'COD_REG',
#    'COD_ISTAT',
#    'PRO_COM',
#    'SEZ2011',
#    'SEZ',
#    'ACE',
#    'geometry'
#  ]]
#  df_shp = df_shp.astype({
#    'COD_REG':'int',
#    'COD_ISTAT':'int',
#    'PRO_COM':'int',
#    'SEZ2011':'int',
#    'SEZ':'int',
#    'ACE':'int'
#  })
  print(df_shp.columns, df_shp.shape)
  print(df_shp.crs)

  df_shp.to_crs({'init': 'epsg:4326'})
#  print(df_shp.head)

  for r in df_shp.iterrows():
    print(r[1]['geometry'])
    break

  df_shp.plot()