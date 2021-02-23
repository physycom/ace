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
from matplotlib.ticker import FuncFormatter

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--scale', help='[mode] list of plot scales', choices=['r', 'p', 'c', 'a'], nargs='+', default=[])
  parser.add_argument('-fr', '--regf', help='[params] list of UID of REGIONI to plot at PROVINCIA scale (e.g. 008)', nargs='+', default=['008'])
  parser.add_argument('-fp', '--prof', help='[params] list of UID of PROVINCE to plot at COMUNE scale (e.g. 008037)', nargs='+', default=['008037'])
  parser.add_argument('-fc', '--comf', help='[params] list of UID of COMUNI to plot at ACE scale (e.g. 008037006)', nargs='+', default=['008037006'])
  parser.add_argument('-fa', '--acef', help='[params] list of UID of ACE to plot at ACE scale (e.g. 008037006081)', nargs='+', default=['008037006081'])
  parser.add_argument('-m', '--domap', help='[params] enable background map', action='store_true')

  args = parser.parse_args()
  base = 'italy_shapes'

  for scale in args.scale:
    print(f'Plotting scale : {scale}')

    """ Plot REG scale """
    if scale == 'r':
      rfile = f'{base}/italy_reg.shp'
      basename = rfile[:rfile.rfind('.')]
      rdf = gpd.read_file(rfile)
      regmap = { k[0] : k[1] for k, _ in rdf.groupby(['REG', 'REG_NAME']) }

      fmt = FuncFormatter(lambda r, _: regmap[r])
      fig, ax = plt.subplots(1, 1, figsize=(12, 12))
      rdf = rdf.to_crs(epsg=3857)
      rdf.plot(
        column='REG',
        ax=ax,
        alpha=0.5,
        edgecolor='k',
        legend=True,
        cmap=plt.get_cmap('jet', len(regmap)),
        vmin=rdf.REG.min()-0.5,
        vmax=rdf.REG.max()+0.5,
        legend_kwds={
          'ticks': range(rdf.REG.min(), rdf.REG.max()+1),
          'format': fmt
        }
      )
      rdf['x'] = rdf.geometry.centroid.x
      rdf['y'] = rdf.geometry.centroid.y
      for idx, row in rdf.iterrows():
        ax.annotate(text=row['REG_NAME'], xy=row[['x', 'y']], horizontalalignment='center')
      ax.axis('off')
      plt.title(f'REGIONI ({len(rdf)}) annotated shapefile')
      mapfile = f'{basename}.png'
      plt.savefig(mapfile)
      plt.close()

    """ Plot PRO scale """
    if scale == 'p':
      pfile = f'{base}/italy_pro.shp'
      basename = pfile[:pfile.rfind('.')]
      prodf = gpd.read_file(pfile)

      for rf in args.regf:
        if rf != 'all':
          pdf = prodf[ prodf.UID.str.startswith(rf) ].copy()
          if len(pdf) == 0:
            print(f'No match for REG filter : {rf}')
            continue
          regname = pdf.groupby('REG').first().REG_NAME.values[0]
        else:
          pdf = prodf.copy()
          regname = 'all'

        print(f'Plotting region {rf} {regname} by PRO ({len(pdf)})')

        pdf['color'] = [ int(i) for i in range(len(pdf)) ]
        promap = { c : n for c, n in pdf[['color', 'PRO_NAME']].values }

        fmt = FuncFormatter(lambda u, _: promap[u])
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        pdf = pdf.to_crs(epsg=3857)
        pdf.plot(
          column='color',
          ax=ax,
          alpha=0.5,
          edgecolor='k',
          legend=True,
          cmap=plt.get_cmap('cividis', len(pdf)),
          vmin=pdf.color.min()-0.5,
          vmax=pdf.color.max()+0.5,
          legend_kwds={
            'ticks': range(pdf.color.min(), pdf.color.max()+1),
            'format': fmt,
            'label': 'Province',
            #'orientation': 'vertical'
          }
        )

        # annotate with label
        pdf['x'] = pdf.geometry.centroid.x
        pdf['y'] = pdf.geometry.centroid.y
        for idx, row in pdf.iterrows():
          ax.annotate(text=row['PRO_NAME'], xy=row[['x', 'y']], horizontalalignment='center')

        ax.axis('off')
        plt.suptitle(f'REGIONE {rf} {regname} PRO ({len(pdf)}) annotated shapefile')
        mapfile = f'{basename}_{rf}.png'
        plt.savefig(mapfile)
        plt.close()

    """ Plot COM scale """
    if scale == 'c':
      cfile = f'{base}/italy_com.shp'
      basename = cfile[:cfile.rfind('.')]
      comdf = gpd.read_file(cfile)

      for pf in args.prof:
        cdf = comdf[ comdf.UID.str.startswith(pf) ].copy()
        if len(cdf) == 0:
          print(f'No match for PRO filter : {pf}')
          continue
        proname = cdf.groupby('PRO').first().PRO_NAME.values[0]
        print(f'Plotting provincia {pf} {proname} by COM ({len(cdf)})')

        cdf['color'] = [ int(i) for i in range(len(cdf)) ]
        commap = { c : n for c, n in cdf[['color', 'COM_NAME']].values }

        fmt = FuncFormatter(lambda u, _: commap[u])
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        cdf = cdf.to_crs(epsg=3857)
        cdf.plot(
          column='color',
          ax=ax,
          alpha=0.5,
          edgecolor='k',
          legend=True,
          cmap=plt.get_cmap('hsv', len(cdf)),
          vmin=cdf.color.min()-0.5,
          vmax=cdf.color.max()+0.5,
          legend_kwds={
            'ticks': range(cdf.color.min(), cdf.color.max()+1),
            'format': fmt
          }
        )

        # annotate with label
        cdf['x'] = cdf.geometry.centroid.x
        cdf['y'] = cdf.geometry.centroid.y
        for idx, row in cdf.iterrows():
          ax.annotate(text=row['COM_NAME'], xy=row[['x', 'y']], horizontalalignment='center')

        ax.axis('off')
        plt.suptitle(f'PROVINCIA {pf} {proname} COM ({len(cdf)}) annotated shapefile')
        mapfile = f'{basename}_{pf}.png'
        plt.savefig(mapfile)
        # add map
        if args.domap:
          ctx.add_basemap(ax, crs=cdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
          mapfile = f'{basename}_{pf}_map.png'
          plt.savefig(mapfile)
        plt.close()

    """ Plot ACE scale """
    if scale == 'a':
      afile = f'{base}/italy_ace.shp'
      basename = afile[:afile.rfind('.')]
      acedf = gpd.read_file(afile)

      filters = args.comf + args.acef
      for cf in filters:
        adf = acedf[ acedf.UID.str.startswith(cf) ].copy()
        if len(adf) == 0:
          print(f'No match for COM filter : {cf}')
          continue
        comname = adf.groupby('COM').first().COM_NAME.values[0]
        print(f'Plotting comune {cf} {comname} by ACE ({len(adf)})')

        adf['color'] = [ int(i) for i in range(len(adf)) ]
        acemap = { c : n for c, n in adf[['color', 'UID']].values }

        fmt = FuncFormatter(lambda u, _: acemap[u])
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        adf = adf.to_crs(epsg=3857)
        adf.plot(
          column='color',
          ax=ax,
          alpha=0.5,
          edgecolor='k',
          #facecolor=(0., 0., 0., 0.),
          legend=True,
          cmap=plt.get_cmap('hsv', len(adf)),
          vmin=adf.color.min()-0.5,
          vmax=adf.color.max()+0.5,
          legend_kwds={
           'ticks': range(adf.color.min(), adf.color.max()+1),
           'format': fmt
          }
        )

        # annotate with label
        adf['x'] = adf.geometry.centroid.x
        adf['y'] = adf.geometry.centroid.y
        for idx, row in adf.iterrows():
          if row.geometry.type == 'Polygon':
            ax.annotate(text=f'{row.ACE:03d}', xy=row[['x', 'y']], horizontalalignment='center')
          elif row.geometry.type == 'MultiPolygon':
            for i, pol in enumerate(list(row['geometry'])):
              ax.annotate(text=f'{row.ACE:03d}', xy=(pol.centroid.x, pol.centroid.y), horizontalalignment='center')

        plt.suptitle(f'UID {cf} COM {comname} (objects {len(adf)}) annotated shapefile')
        ax.axis('off')
        mapfile = f'{basename}_{cf}.png'
        plt.savefig(mapfile)
        # add map
        if args.domap:
          ctx.add_basemap(ax, crs=adf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
          mapfile = f'{basename}_{cf}_map.png'
          plt.savefig(mapfile)
        plt.close()

