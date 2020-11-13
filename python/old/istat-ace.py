#! /usr/bin/env python3

import geopandas as gpd
import argparse
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import contextily as ctx
from shapely import geometry

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--shp", help="ISTAT shapefile regex", required=True)
args = parser.parse_args()

shapefiles = sorted(glob.glob(args.shp))
acetot = 0
for f in shapefiles:
  base = f[:f.rfind('.')]
  print('[aceISTAT] Processing file : {}'.format(f), flush=True)

  ti = datetime.now()
  df_shp = gpd.read_file(f)
#  df_shp.drop(df_shp.tail(len(df_shp)-10).index,inplace=True)
  df_shp['geometry'] = df_shp['geometry'].to_crs({'init': 'epsg:4326'})
  df_shp = df_shp[[
    'COD_REG',
    'PRO_COM',
    'SEZ2011',
    'LOC2011',
    'SEZ',
    'ACE',
    'geometry'
  ]]
  df_shp = df_shp.astype({
    'COD_REG':'int',
    'PRO_COM':'int',
    'SEZ2011':'int',
    'LOC2011':'int',
    'SEZ':'int',
    'ACE':'int'
  })
  df_shp['ACE_ID'] =  df_shp['COD_REG'].apply(lambda x: '{:03d}'.format(x))
  df_shp['ACE_ID'] += df_shp['PRO_COM'].apply(lambda x: '|{:03d}|{:03d}'.format(x//1000, x - (x//1000)*1000))

  #df_shp['loc_id'] =  df_shp['ace_id']
  #df_shp['loc_id'] += df_shp['LOC2011'].apply(lambda x: '|{:03d}|{:03d}'.format(x//1000, x - (x//1000)*1000))
  #lloc = len(df_shp.groupby('loc_id'))
  #print('loc_id univocity check : {} == {} = {}'.format(len(df_shp), lloc, len(df_shp) == lloc))

  df_shp['ACE_ID'] += df_shp['ACE'].apply(lambda x: '|{:03d}'.format(x))
  df_shp['ACE_ID'] += df_shp['SEZ'].apply(lambda x: '|{:03d}'.format(x))

  df_shp['CENTROID'] = df_shp['geometry'].apply(lambda x: x.centroid)
  df_shp['LON'] = df_shp['CENTROID'].apply(lambda x: x.x)
  df_shp['LAT'] = df_shp['CENTROID'].apply(lambda x: x.y)

  lace = len(df_shp.groupby('ACE_ID'))
  acetot += lace
  print('[aceISTAT] ACE_ID check : {} == {} = {}'.format(len(df_shp), lace, len(df_shp) == lace))

  df_shp[['ACE_ID','LAT','LON']].sort_values(by=['ACE_ID']).to_csv(base + '.csv', sep=',', index=False)
  print('[aceISTAT] Done in {} s'.format(datetime.now() - ti), flush=True)

  ace_map = 'istat_ace_map.png'
  ax = df_shp.plot(alpha=0.5, edgecolor='k', figsize=(12, 12))
  #for idx, row in coils.iterrows(): ax.annotate(s=row['NAME'], xy=row[['x', 'y']], horizontalalignment='center')
  #ctx.add_basemap(ax, crs=coils.crs.to_string(), source=ctx.providers.CartoDB.Voyager)
  plt.savefig(ace_map)
  plt.close()


print('[aceISTAT] Total aceid geotagged {}'.format(acetot), flush=True)
