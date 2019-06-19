#! /usr/bin/env python3

import geopandas as gpd
df_shp = gpd.read_file('/mnt/e/Alessandro/ACE/R08_11_WGS84/R08_11_WGS84.shp')
df_shp = df_shp[[
  'COD_REG',
  'COD_ISTAT',
  'PRO_COM',
  'SEZ2011',
  'SEZ',
  'ACE',
  'geometry'
]]
df_shp = df_shp.astype({
  'COD_REG':'int',
  'COD_ISTAT':'int',
  'PRO_COM':'int',
  'SEZ2011':'int',
  'SEZ':'int',
  'ACE':'int'
})
print(df_shp.columns)
print(df_shp.shape)
print(df_shp.head)
