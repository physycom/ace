#! /usr/bin/env python3

import os
import geopandas as gpd
import pandas as pd
import argparse
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import contextily as ctx
from shapely import geometry
import colorsys

rois = {
  'ER' : {
    'lat_max' : 45.3055084,
    'lat_min' : 43.8698767,
    'lon_max' : 12.7978165,
    'lon_min' : 9.0652115
  },
  'ITA' : {
    'lat_max' : 48.181,
    'lat_min' : 34.796,
    'lon_max' : 22.104,
    'lon_min' : 4.373
  }
}

rois_poly = {}
for tag, cv in rois.items():
  pointList = [
    [ cv['lon_min'], cv['lat_min'] ],
    [ cv['lon_max'], cv['lat_min'] ],
    [ cv['lon_max'], cv['lat_max'] ],
    [ cv['lon_min'], cv['lat_max'] ]
  ]
  poly = geometry.Polygon(pointList)
  spoly = gpd.GeoSeries([poly])
  spoly = spoly.set_crs(epsg=4326)
  rois_poly[tag] = spoly

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--datadir', help='[global] base folder', required=True)
  parser.add_argument('-s', '--dosec', help='[mode] ISTAT Sezioni(csv) preprocessing', action='store_true')
  parser.add_argument('-l', '--doloc', help='[mode] ISTAT Localita\' preprocessing', action='store_true')
  parser.add_argument('-c', '--docom', help='[mode] ISTAT Comuni preprocessing', action='store_true')
  parser.add_argument('-a', '--doace', help='[mode] ISTAT Sezioni(shp)', type=int, nargs='+', default=[])
  parser.add_argument('-asc', '--doasc', help='[mode] ISTAT ASC2011 data shp', action='store_true')
  parser.add_argument('-p', '--doplot', help='[out] enable geoplot', action='store_true')
  parser.add_argument('-o', '--doorig', help='[out] enable original shapefile csv conversion', action='store_true')
  parser.add_argument('-u', '--doout', help='[out] debug analytics to stdout', action='store_true')
  parser.add_argument('-r', '--roi', help='[para] select roi label', choices=rois.keys(), default='ITA')

  args = parser.parse_args()
  roi = args.roi
  datadir = args.datadir

  """
  ISTAT Sezioni analysis
  """
  if args.dosec:
    sec_file = f'{datadir}/Sezioni_2011_Point_WGS84/SezIta_2011_Point_WGS84.shp'
    sec_gdf = gpd.read_file(sec_file
    #,rows=10000
    #,rows=slice(300000, 350000, 1)
    )
    sec_gdf = sec_gdf.to_crs(epsg=4326)
    fullsec = len(sec_gdf)
    sec_gdf = sec_gdf[sec_gdf.within(rois_poly[roi].geometry.iloc[0])]
    filteredsec = len(sec_gdf)
    print(f'SEZIONI : roi {roi} data {fullsec} filtered {filteredsec}')
    #print(sec_gdf)
    #print(sec_gdf.columns)
    # Reference header
    # 'OBJECTID', 'PERIMETER', 'COD_REG', 'COD_ISTAT', 'PRO_COM', 'SEZ',
    #    'SEZ2011', 'X_WGS84', 'Y_WGS84', 'ORIG_FID', 'geometry'

    if args.doorig:
      pd.DataFrame(sec_gdf).to_csv(f'istat_sez_{roi}_0_original.csv', index=False, sep=';')

    sec_gdf['LAT'] = sec_gdf.geometry.y
    sec_gdf['LON'] = sec_gdf.geometry.x
    sec_gdf['PRO'] = sec_gdf.PRO_COM // 1000
    sec_gdf['COM'] = sec_gdf.PRO_COM % int(1e3)
    sec_gdf['SEZ'] = sec_gdf.SEZ
    sec_gdf['RPC'] = sec_gdf[[ 'COD_REG', 'PRO_COM']].apply(lambda x: '{:03d}{:06d}'.format(*x), axis=1)
    #print(sec_gdf)

    if args.doplot:
      ace_map = f'istat_sez_{roi}_map.png'
      plotgdf = sec_gdf.copy()
      ax = plotgdf.plot(alpha=0.5, color='red', edgecolor='k', figsize=(12, 12))
      #for idx, row in coils.iterrows(): ax.annotate(s=row['NAME'], xy=row[['x', 'y']], horizontalalignment='center')
      #ctx.add_basemap(ax, crs=coils.crs.to_string(), source=ctx.providers.CartoDB.Voyager)
      plt.savefig(ace_map)
      plt.close()

    sec_df = sec_gdf[[
      'COD_REG',
      'PRO_COM',
      'PRO',
      'COM',
      'SEZ',
      'COD_ISTAT',
      'SEZ2011',
      'LAT',
      'LON',
      'RPC'
    ]].copy()
    sez_num = len(sec_df)
    print(f'SEZIONI : Total SEZ2011 {len(sec_df)}')
    #print(sec_df)
    sec_df.to_csv(f'istat_sez_{roi}_1_converted.csv', index=False, sep=';')

  """
  ISTAT Localita analysis
  """
  if args.doloc:
    loc_file = f'{datadir}/Localita_11_WGS84/Localita_11_WGS84.shp'
    df_shp = gpd.read_file(loc_file)
    df_shp = df_shp.to_crs(epsg=4326)
    fullsec = len(df_shp)
    df_shp = df_shp[df_shp.within(rois_poly[roi].geometry.iloc[0])]
    filteredsec = len(df_shp)
    print(f'LOCALITA : roi {roi} data {fullsec} filtered {filteredsec}')

    df_shp = df_shp.to_crs(epsg=3857)
    df_shp['centroid'] = df_shp.geometry.centroid
    df_shp = df_shp.to_crs(epsg=4326)
    df_shp['lat'] = df_shp['centroid'].geometry.y
    df_shp['lon'] = df_shp['centroid'].geometry.x

    if args.doplot:
      ace_map = f'istat_loc_{roi}_map.png'
      ax = df_shp.plot(alpha=0.5, edgecolor='k', figsize=(12, 12))
      plt.savefig(ace_map)
      plt.close()

    df = pd.DataFrame(df_shp)
    if args.doorig:
      df.to_csv(f'istat_loc_{roi}_0_original.csv', index=False, sep=';')

    df[[
      'COD_REG',
      'COD_PRO',
      'PRO_COM',
      'LOC2011',
      'COD_ISTAT',
      'DENOMINAZI',
      'Shape_Area'
    ]].astype({
      'COD_REG':'int',
      'COD_PRO':'int',
      'PRO_COM':'int',
      'LOC2011':'int',
      'COD_ISTAT':'int',
      'DENOMINAZI':'str',
      'Shape_Area':'float'
    }).to_csv(f'istat_loc_{roi}_1_lite.csv', index=False, sep=';')
    # ISTAT Localita file header for reference in case of column addition
    # [
    # 'OBJECTID', 'COD_ISTAT', 'COD_REG', 'COD_PRO', 'PRO_COM', 'LOC2011',
    # 'LOC', 'TIPO_LOC', 'DENOMINAZI', 'ALTITUDINE', 'CENTRO_CL', 'POPRES',
    # 'MASCHI', 'FAMIGLIE', 'ABITAZIONI', 'EDIFICI', 'Shape_Leng',
    # 'Shape_Area', 'geometry'
    # ']

  """
  ISTAT ASC
  """
  if args.doasc:
    ascfile = f'{datadir}/ASC2011_WGS84/Italia/ASC2011_WGS84.shp'
    ascdf = gpd.read_file(ascfile)
    #ascdf = ascdf.to_crs(epsg=4326)
    asc_num = len(ascdf)
    #print(ascdf)
    print(f'ASC : data {asc_num} ')

    ax = ascdf.plot(alpha=0.5, edgecolor='k', figsize=(12, 12))
    ctx.add_basemap(ax, crs=ascdf.crs.to_string(), source=ctx.providers.CartoDB.Voyager)
    asc_map = 'istat_ASC_map.png'
    plt.savefig(asc_map)
    plt.close()

