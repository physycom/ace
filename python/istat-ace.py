#! /usr/bin/env python3

import os
import geopandas as gpd
import pandas as pd
import argparse
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import contextily as ctx
from shapely import geometry, ops
import colorsys

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-a', '--doace', help='[mode] list of region codes (as int)', action='store_true')
  parser.add_argument('-s', '--doasc', help='[mode] parse ISTAT ASC2011 data shp', action='store_true')
  parser.add_argument('-mp', '--mergepro', help='[mode] merge province levels starting from ace', action='store_true')
  # mode doace
  parser.add_argument('-r', '--regs', help='[MODE doace] list of region codes (as int)', type=int, nargs='+', default=[])
  parser.add_argument('-f', '--acefilter', help='[MODE doace] list of 3,6,9-digit ace subset to filter', type=str, nargs='+', default=[])
  parser.add_argument('-e', '--domerge', help='[MODE doace] merge polygons at given resolution', choices=['c', 'a'])
  parser.add_argument('-p', '--doplot', help='[MODE doace] do geoplot', action='store_true')
  parser.add_argument('-m', '--domap', help='[MODE doace] enable plot map background (slow)', action='store_true')

  args = parser.parse_args()
  regs = args.regs
  acefilter = args.acefilter

  aceintfil = [ int(a[0:3]) for a in acefilter ]
  regs.extend([ r for r in aceintfil if r not in regs ])
  print(f'Converting regions : {regs}')

  """
  ISTAT Aree Censuarie
  """
  if args.doace:
    for reg in regs:
      print(f'Processing region {reg}')

      base = 'istat_ace_shp'
      rtag = f'R{reg:02d}_11_WGS84'
      sec_file = f'{base}/{rtag}/{rtag}.shp'

      if not os.path.exists(sec_file):
        print(f'ERR: Input file {sec_file} not found')
        continue

      secdf = gpd.read_file(sec_file
      #,rows=10000
      #,rows=slice(300000, 350000, 1)
      )
      #secdf = secdf.to_crs(epsg=4326)
      fullsec = len(secdf)
      #sec_gdf = sec_gdf[sec_gdf.within(rois_poly[roi].geometry.iloc[0])]
      filteredsec = len(secdf)
      print(f'SEZIONI : data {fullsec} filtered {filteredsec}')

      secdf['R'] = secdf.COD_REG.astype('int')
      secdf['P'] = (secdf.PRO_COM // 1000).astype('int')
      secdf['C'] = (secdf.PRO_COM % 1000).astype('int')

      rgrp = secdf.groupby(['R'])
      pgrp = secdf.groupby(['R', 'P'])
      cgrp = secdf.groupby(['R', 'P', 'C'])
      agrp = secdf.groupby(['R', 'P', 'C', 'ACE'])
      sgrp = secdf.groupby(['R', 'P', 'C', 'ACE', 'SEZ2011'])
      print(f'Region {reg} Num REG :', len(rgrp))
      print(f'Region {reg} Num PRO :', len(pgrp))
      print(f'Region {reg} Num COM :', len(cgrp))
      print(f'Region {reg} Num ACE :', len(agrp))
      print(f'Region {reg} Num SEZ :', len(sgrp))
      print(f'Region {reg} Num rec :', len(secdf))

      lout = open(f'{base}/{rtag}/log.log', 'w')

      secdf['center'] = secdf.geometry.centroid
      secdf['center_x'] = secdf.center.x
      secdf['center_y'] = secdf.center.y
      secdf['RPC'] = [ f'{r:03.0f}{pc:06.0f}' for r,pc in secdf[['COD_REG', 'PRO_COM']].values ]
      secdf['FULLSEZ'] = [ f'{rpc}S{s:07.0f}' for rpc, s in secdf[['RPC', 'SEZ']].values ]
      secdf['OACE'] = [ f'{rpc}C{a:03d}' for rpc, a in secdf[['RPC', 'ACE']].values ]
      secdf = secdf.sort_values(by='OACE')
      #print(secdf)

      for r, dfr in secdf.groupby(['R']):
        grpp = dfr.groupby(['P'])
        lout.write(f'+ REG {r} ({len(grpp)})\n')
        for p, dfp in grpp:
          grpc = dfp.groupby(['C'])
          lout.write(f'  - PRO {p} ({len(grpc)})\n')
          for c, dfc in grpc:
            lout.write(f"    * COM {c} (SEZ {len(dfc)} ACE {len(dfc.groupby('ACE'))}) \n") #{dfc['OACE']} {dfc['FULLSEZ']}\n")
            for a, dfa in dfc.groupby(['ACE']):
              lout.write(f"      . ACE {a} (SEZ {len(dfa)}) \n") #{dfc['OACE']} {dfc['FULLSEZ']}\n")
              for _, s in dfa.iterrows():
                lout.write(f"        @ SEZ {s['SEZ']:.0f} {s['OACE']} {s['FULLSEZ']} \n") #{dfc['OACE']} {dfc['FULLSEZ']}\n")

      if args.doplot and len(acefilter):
        secdf['KEEP'] = False
        for acef in acefilter:
          secdf.loc[ secdf.RPC.str.startswith(acef), 'KEEP' ] = True
        pdf = secdf[ secdf.KEEP ].copy()
        print(pdf)

        pdf['color'] = pdf.ACE.values
        pdf['label'] = [ f's{s} a{a}' for s, a in pdf[['SEZ', 'ACE']].astype('int').values ]

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        axes = axes.flatten()

        ax = axes[0]
        pdf.plot(
          column='color',
          ax=ax,
          alpha=0.3,
          edgecolor='k',
        #  legend_kwds={
        #    'label': 'SEZ2011',
        #    'orientation': 'vertical'
        #  },
        #  classification_kwds=dict(bins=[0,100])
        #  classification_kwds=dict(bins=[-10,20,30,50,70])
        #  legend=True,
        #  scheme='User_Defined',
        #  classification_kwds=dict(bins=range(len(pdf))),
        ) # linewidth=5,
        #for idx, row in pdf.iterrows(): ax.annotate(s=row['label'], xy=row[['center_x', 'center_y']], horizontalalignment='center')

        acedf = {}
        for a, dfa in pdf.groupby('ACE'):
          polygons = dfa.geometry
          boundary = gpd.GeoSeries(ops.cascaded_union(polygons))
          #boundary = ops.cascaded_union(polygons)
          acedf[dfa.OACE.unique()[0]] = boundary
        #print(acedf)
        acepoly = gpd.GeoSeries([ poly for p in acedf.values() for poly in p.geometry ])
        #print(acepoly)
        acegdf = gpd.GeoDataFrame(acedf.keys())
        acegdf.geometry = acepoly.geometry
        acegdf['color'] = range(len(acegdf))
        #print(acegdf)

        ax = axes[1]
        acegdf.plot(
          column='color',
          ax=ax,
          alpha=0.3,
          edgecolor='k',
        )

        ace_map = f'{base}/{rtag}/map_{"-".join(acefilter)}.png'
        title_map = 'ACE map for {}'.format(*[ f"{acef} (sez {len(pdf)} ace {len(pdf.OACE.unique())} )" for acef in acefilter ])
        plt.suptitle(title_map)
        plt.savefig(ace_map)
        plt.close()

        if args.domap:
          fig, ax = plt.subplots(1, 1, figsize=(12, 12))
          pdf.plot(
            column='color',
            ax=ax,
            alpha=0.3,
            edgecolor='k'
          )
          ctx.add_basemap(ax, crs=pdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)#CartoDB.Voyager)
          ace_map = f'{base}/{rtag}/map_{"-".join(acefilter)}_map.png'
          plt.title(title_map)
          plt.savefig(ace_map)
          plt.close()
      lout.close()

      if args.domerge == 'c':
        poly = {}
        tot = len(cgrp)
        for i, (u, dfu) in enumerate(cgrp):
          print(f'Merging COM {i}/{tot} {u} ({len(dfu)})', flush=True)
          poly[u] = gpd.GeoSeries(ops.cascaded_union(dfu.geometry))
          #if i > 5: break
        gdf = gpd.GeoDataFrame(
          poly.keys(),
          geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p.geometry ])
        )
        gdf['color'] = range(len(gdf))

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        gdf.plot(
          column='color',
          ax=ax,
          alpha=0.3,
          edgecolor='k',
          legend=True
        )
        mapfile = f'{base}/{rtag}/R{reg:02d}_com.png'
        plt.title(f'COM based aggregation, polygons {len(gdf)}')
        plt.savefig(mapfile)
        plt.close()

      elif args.domerge == 'a':
        poly = {}
        tot = len(agrp)
        for i, (u, dfu) in enumerate(agrp):
          print(f'Merging ACE {i}/{tot} {u} ({len(dfu)})', flush=True)
          poly[u] = (gpd.GeoSeries(ops.cascaded_union(dfu.geometry)), dfu.SEZ.astype('int').to_list())
          #if i > 2: break
        gdf = gpd.GeoDataFrame(
          poly.keys(),
          columns=['REG', 'PRO', 'COM', 'ACE'],
          geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p[0].geometry ]),
          crs=dfu.crs
        )
        gdf['color'] = range(len(gdf))
        gdf['UID'] = [ f'{r:03d}{p:03d}{c:03d}{a:03d}' for r, p, c, a in gdf[['REG', 'PRO', 'COM', 'ACE']].values]
        gdf['SEZ_list'] = [ '|'.join([ f'{uid}{sez:07d}' for sez in p[1] ]) for uid, p in zip(gdf.UID.values, poly.values()) ]
        gdf['center'] = gdf.geometry.to_crs(epsg=25832).centroid.to_crs(epsg=4326)
        gdf['LAT'] = gdf.center.y
        gdf['LON'] = gdf.center.x

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        gdf.plot(
          column='color',
          ax=ax,
          alpha=0.3,
          edgecolor='k',
          legend=True
        )
        mapfile = f'{base}/{rtag}/R{reg:02d}_ace.png'
        plt.title(f'ACE based aggregation, polygons {len(gdf)}')
        plt.savefig(mapfile)
        plt.close()

        dfout = gdf.copy()
        #dfout = dfout.to_crs(epsg=25832)
        #print(dfout)
        dfout = dfout.to_crs(epsg=4326)

        geofile = f'{base}/{rtag}/R{reg:02d}_ace'
        dfout = dfout[[
          'UID',
          'REG',
          'PRO',
          'COM',
          'ACE',
          'LAT',
          'LON',
          'SEZ_list',
          'geometry'
        ]]
        dfout.to_file(f'{geofile}.geojson', driver='GeoJSON')
        dfout.to_file(f'{geofile}.shp')
        # print(gdf)
        # print(gdf.columns)

  """
  ISTAT ASC
  """
  if args.doasc:
    ascfile = 'ASC2011_WGS84/Italia/ASC2011_WGS84.shp'
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

  """
  MERGE PRO
  """
  if args.mergepro:
    for reg in regs:
      print(f'Merging PRO region {reg}')

      base = 'istat_ace_shp'
      rtag = f'R{reg:02d}_11_WGS84'
      acefile = f'{base}/{rtag}/R{reg:02d}_ace.shp'

      if not os.path.exists(acefile):
        print(f'ERR: Input file {acefile} not found')
        continue

      acedf = gpd.read_file(acefile)
      acenum = len(acedf)
      print(f'ACE : data {acenum} ')

      print(acedf)

      pgrp = acedf.groupby(['REG', 'PRO'])
      tot = len(pgrp)
      poly = {}
      for i, (k, df) in enumerate(pgrp):
        print(f'Merging PRO {i}/{tot} {k} (ACE {len(df)})', flush=True)
        poly[k] = gpd.GeoSeries(ops.cascaded_union(df.geometry))
      gdf = gpd.GeoDataFrame(
        poly.keys(),
        geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p.geometry ]),
        crs=df.crs
      )
      gdf['color'] = range(len(gdf))

      fig, ax = plt.subplots(1, 1, figsize=(12, 6))
      gdf.to_crs(epsg=3857).plot(
        column='color',
        ax=ax,
        alpha=0.3,
        edgecolor='k',
        legend=True
      )
      mapfile = f'{base}/{rtag}/R{reg:02d}_pro.png'
      plt.title(f'PRO based aggregation, polygons {len(gdf)}')
      plt.savefig(mapfile)
      plt.close()

      exit(1)

