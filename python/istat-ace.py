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
from collections import defaultdict

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--parse', help='[MODE parse] parse ISTAT shapefiles', action='store_true')
  parser.add_argument('-mc', '--mergecom', help='[MODE mergecom] merge comuni levels starting from ace', action='store_true')
  parser.add_argument('-mp', '--mergepro', help='[MODE mergepro] merge province levels starting from com', action='store_true')
  parser.add_argument('-mr', '--mergereg', help='[MODE mergereg] merge regioni levels starting from pro', action='store_true')
  parser.add_argument('-pa', '--dopack', help='[MODE pack] pack per region outputs at requested scale', choices=['r', 'p', 'c', 'a'], nargs='+')
  parser.add_argument('-d', '--datadir', help='[global] base folder', required=True)
  parser.add_argument('-r', '--regs', help='[global] list of region codes (as int)', type=int, nargs='+', default=[])
  # mode doace
  parser.add_argument('-ma', '--mergeace', help='[parse] merge at ACE level', action='store_true')
  parser.add_argument('-v', '--verbose', help='[parse] enable verbose output to file', action='store_true')

  args = parser.parse_args()
  base = args.datadir

  regs = args.regs
  if len(regs) == 0:
    regs = [ i for i in range(1,21) ]
  print(f'Processing regions : {regs}')

  """
  parse ISTAT Sezioni di Censimento per region shapefiles
  """
  if args.parse:
    for reg in regs:
      print(f'Processing region {reg}')

      rtag = f'R{reg:02d}_11_WGS84'
      sec_file = f'{base}/{rtag}/{rtag}.shp'

      if not os.path.exists(sec_file):
        print(f'ERR: Input file {sec_file} not found')
        continue

      secdf = gpd.read_file(sec_file
      #,rows=10000
      #,rows=slice(300000, 350000, 1)
      )
      fullsec = len(secdf)
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

      secdf['center'] = secdf.geometry.centroid
      secdf['center_x'] = secdf.center.x
      secdf['center_y'] = secdf.center.y
      secdf['RPC'] = [ f'{r:03.0f}{pc:06.0f}' for r,pc in secdf[['COD_REG', 'PRO_COM']].values ]
      secdf['UID'] = [ f'{r:03.0f}{p:03.0f}{c:03.0f}{a:03.0f}|{s:.0f}' for r,p,c,a,s in secdf[['R', 'P', 'C', 'ACE', 'SEZ']].values ]
      secdf = secdf.sort_values(by=['R', 'P', 'C', 'ACE', 'SEZ'])
      #print(secdf)

      if args.verbose:
        lout = open(f'{base}/{rtag}/{rtag}.log', 'w')
        for r, dfr in secdf.groupby(['R']):
          grpp = dfr.groupby(['P'])
          lout.write(f'+ REG {r} ({len(grpp)})\n')
          for p, dfp in grpp:
            grpc = dfp.groupby(['C'])
            lout.write(f'  - PRO {p} ({len(grpc)})\n')
            for c, dfc in grpc:
              lout.write(f"    * COM {c} (SEZ {len(dfc)} ACE {len(dfc.groupby('ACE'))}) \n")
              for a, dfa in dfc.groupby(['ACE']):
                lout.write(f"      . ACE {a} (SEZ {len(dfa)}) \n")
                for _, s in dfa.iterrows():
                  lout.write(f"        @ SEZ {s['SEZ']:.0f} {s['UID']} \n")

      if args.mergeace:
        poly = {}
        tot = len(agrp)
        for i, (u, dfu) in enumerate(agrp):
          print(f'Merging ACE {i}/{tot} {u} ({len(dfu)})', flush=True)
          mpl = ops.cascaded_union(dfu.geometry)
          poly[u] = (mpl, dfu.SEZ.astype('int').to_list())
          #if i > 2: break

        gdf = gpd.GeoDataFrame(
          poly.keys(),
          columns=['REG', 'PRO', 'COM', 'ACE'],
          geometry=gpd.GeoSeries([ p[0] for p in poly.values() ]),
          crs=dfu.crs
        )
        gdf['color'] = range(len(gdf))
        gdf['UID'] = [ f'{r:03d}{p:03d}{c:03d}{a:03d}' for r, p, c, a in gdf[['REG', 'PRO', 'COM', 'ACE']].values]
        gdf['center'] = gdf.geometry.to_crs(epsg=25832).centroid.to_crs(epsg=4326)
        gdf['LAT'] = gdf.center.y
        gdf['LON'] = gdf.center.x

        dfout = gdf.copy()
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
          'geometry'
        ]]
        dfout.to_file(f'{geofile}.geojson', driver='GeoJSON')
        dfout.to_file(f'{geofile}.shp')

  """
  MERGE COM
  """
  if args.mergecom:
    for reg in regs:
      print(f'Merging COM region {reg}')

      rtag = f'R{reg:02d}_11_WGS84'
      acefile = f'{base}/{rtag}/R{reg:02d}_ace.shp'

      if not os.path.exists(acefile):
        print(f'ERR: Input file {acefile} not found')
        continue

      acedf = gpd.read_file(acefile)
      acenum = len(acedf)
      print(f'ACE : data {acenum} ')
      #print(acedf)

      cgrp = acedf.groupby(['REG', 'PRO', 'COM'])
      tot = len(cgrp)
      poly = {}
      for i, (k, df) in enumerate(cgrp):
        print(f'Merging COM {i}/{tot} {k} (ACE {len(df)})', flush=True)
        poly[k] = gpd.GeoSeries(ops.cascaded_union(df.geometry))
      gdf = gpd.GeoDataFrame(
        poly.keys(),
        geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p.geometry ]),
        crs=df.crs,
        columns=['REG', 'PRO', 'COM']
      )
      gdf['UID'] = [ f'{r:03d}{p:03d}{c:03d}' for r, p, c in gdf[['REG', 'PRO', 'COM']].values]
      gdf['center'] = gdf.geometry.to_crs(epsg=25832).centroid.to_crs(epsg=4326)
      gdf['LAT'] = gdf.center.y
      gdf['LON'] = gdf.center.x

      dfout = gdf.copy()
      dfout = dfout.to_crs(epsg=4326)
      geofile = f'{base}/{rtag}/R{reg:02d}_com'
      dfout = dfout[[
        'UID',
        'REG',
        'PRO',
        'COM',
        'LAT',
        'LON',
        'geometry'
      ]]
      dfout.to_file(f'{geofile}.geojson', driver='GeoJSON')
      dfout.to_file(f'{geofile}.shp')

  """
  MERGE PRO
  """
  if args.mergepro:
    for reg in regs:
      print(f'Merging PRO region {reg}')

      rtag = f'R{reg:02d}_11_WGS84'
      acefile = f'{base}/{rtag}/R{reg:02d}_ace.shp'

      if not os.path.exists(acefile):
        print(f'ERR: Input file {acefile} not found')
        continue

      acedf = gpd.read_file(acefile)
      acenum = len(acedf)
      print(f'ACE : data {acenum} ')
      #print(acedf)

      pgrp = acedf.groupby(['REG', 'PRO'])
      tot = len(pgrp)
      poly = {}
      for i, (k, df) in enumerate(pgrp):
        print(f'Merging PRO {i}/{tot} {k} (ACE {len(df)})', flush=True)
        poly[k] = gpd.GeoSeries(ops.cascaded_union(df.geometry))
      gdf = gpd.GeoDataFrame(
        poly.keys(),
        geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p.geometry ]),
        crs=df.crs,
        columns=['REG', 'PRO']
      )
      gdf['UID'] = [ f'{r:03d}{p:03d}' for r, p in gdf[['REG', 'PRO']].values]
      gdf['center'] = gdf.geometry.to_crs(epsg=25832).centroid.to_crs(epsg=4326)
      gdf['LAT'] = gdf.center.y
      gdf['LON'] = gdf.center.x

      dfout = gdf.copy()
      dfout = dfout.to_crs(epsg=4326)
      geofile = f'{base}/{rtag}/R{reg:02d}_pro'
      dfout = dfout[[
        'UID',
        'REG',
        'PRO',
        'LAT',
        'LON',
        'geometry'
      ]]
      dfout.to_file(f'{geofile}.geojson', driver='GeoJSON')
      dfout.to_file(f'{geofile}.shp')

  """
  MERGE REG
  """
  if args.mergereg:
    for reg in regs:
      print(f'Merging REG region {reg}')

      rtag = f'R{reg:02d}_11_WGS84'
      profile = f'{base}/{rtag}/R{reg:02d}_pro.shp'

      if not os.path.exists(profile):
        print(f'ERR: Input file {profile} not found')
        continue

      prodf = gpd.read_file(profile)
      acenum = len(prodf)
      print(f'PRO : data {acenum} ')
      #print(prodf)

      rgrp = prodf.groupby(['REG'])
      tot = len(rgrp)
      poly = {}
      for i, (k, df) in enumerate(rgrp):
        print(f'Merging REG {i}/{tot} {k} (PRO {len(df)})', flush=True)
        poly[k] = gpd.GeoSeries(ops.cascaded_union(df.geometry))
      gdf = gpd.GeoDataFrame(
        poly.keys(),
        geometry=gpd.GeoSeries([ polyg for p in poly.values() for polyg in p.geometry ]),
        crs=df.crs,
        columns=['REG']
      )
      gdf['color'] = range(len(gdf))
      gdf['UID'] = [ f'{r:03d}' for r in gdf.REG.values ]
      gdf['center'] = gdf.geometry.to_crs(epsg=25832).centroid.to_crs(epsg=4326)
      gdf['LAT'] = gdf.center.y
      gdf['LON'] = gdf.center.x

      fig, ax = plt.subplots(1, 1, figsize=(12, 6))
      gdf.to_crs(epsg=3857).plot(
        column='color',
        ax=ax,
        alpha=0.3,
        edgecolor='k',
        legend=True
      )
      mapfile = f'{base}/{rtag}/R{reg:02d}_reg.png'
      plt.title(f'REG based aggregation, polygons {len(gdf)}')
      plt.savefig(mapfile)
      plt.close()

      dfout = gdf.copy()
      dfout = dfout.to_crs(epsg=4326)
      geofile = f'{base}/{rtag}/R{reg:02d}_reg'
      dfout = dfout[[
        'UID',
        'REG',
        'LAT',
        'LON',
        'geometry'
      ]]
      dfout.to_file(f'{geofile}.geojson', driver='GeoJSON')
      dfout.to_file(f'{geofile}.shp')

  """
  PACK & ANNOTATE
  """
  if args.dopack:

    """ IMPORT METADATA """
    com2file = f'{base}/Archivio-elenco-comuni-codici-e-denominazioni_Anni_2011-2015/Codici-statistici-e-denominazioni-al-31_12_2011.xls'
    comdf = pd.read_excel(com2file, sheet_name='CODICI al 31_12_2011')
    # Full header
    # 'Codice Regione', 'Codice Provincia', 'Progressivo del comune',
    # 'Codice Istat del Comune \n(alfanumerico)',
    # 'Codice Istat del Comune \n(numerico)',
    # 'Denominazione (Italiana e straniera)', 'Denominazione in italiano',
    # 'Denominazione altra lingua', 'Codice Ripartizione Geografica',
    # 'Ripartizione geografica', 'Denominazione Regione',
    # 'Denominazione Provincia', 'Flag Comune capoluogo di provincia',
    # 'Sigla automobilistica',
    # 'Codice Comune numerico con 107 province (dal 2006 al 2009)\n',
    # 'Codice Comune numerico con 103 province (dal 1995 al 2005)\n',
    # 'Codice Catastale del comune', 'Codice NUTS1 2010', 'Codice NUTS2 2010',
    # 'Codice NUTS3 2010', 'Codice NUTS1 2006', 'Codice NUTS2 2006',
    # 'Codice NUTS3 2006',
    refactor = {
      'Codice Regione':'REG',
      'Codice Provincia':'PRO',
      'Progressivo del comune':'COM',
      'Denominazione Regione':'REG_NAME',
      'Denominazione Provincia':'PRO_NAME',
      'Denominazione (Italiana e straniera)':'COM_NAME',
    }
    comdf = comdf[refactor.keys()].rename(columns=refactor)
    regnum = len(comdf.groupby('REG').count())
    pronum = len(comdf.groupby(['REG', 'PRO']).count())
    comnum = len(comdf.groupby(['REG', 'PRO', 'COM']).count())
    print(f'COMUNI Data : Regioni {regnum} Province {pronum} Comuni {comnum} ')

    regmap = { k[0] : k[1] for k, _ in comdf.groupby(['REG', 'REG_NAME']) }
    promap = { (k[0],k[1]) : k[2] for k, _ in comdf.groupby(['REG', 'PRO', 'PRO_NAME']) }
    commap = { (k[0],k[1],k[2]) : k[3] for k, _ in comdf.groupby(['REG', 'PRO', 'COM', 'COM_NAME']) }
    print(f'COMUNI dict : Regioni {len(regmap)} Province {len(promap)} Comuni {len(commap)} ')

    shapefolder = 'italy_shapes'
    if not os.path.exists(shapefolder): os.mkdir(shapefolder)

    """ PACK REGIONI """
    if 'r' in args.dopack:
      regshp = glob.glob(f'{base}/R*/R*_reg.shp')
      regdf = gpd.GeoDataFrame()
      for i, rf in enumerate(regshp):
        print(f'{i: 2d}/{len(regshp)} Pack REG {rf}', flush=True)
        rdf = gpd.read_file(rf)
        regdf = regdf.append(rdf)
      regdf['REG_NAME'] = [ regmap[r] for r in regdf['REG'].values ]
      #print(regdf)

      regs = regdf[[
        'UID',
        'REG',
        'REG_NAME',
        'LAT',
        'LON',
        'geometry',
      ]]
      outfile = f'italy_reg'
      regs.to_file(f'{shapefolder}/{outfile}.geojson', driver='GeoJSON')
      regs.to_file(f'{shapefolder}/{outfile}.shp')
      regs.drop(columns='geometry').to_csv(f'{shapefolder}/{outfile}.csv', sep=';', index=False)

      missreg = regs.groupby('REG').first()
      missr = len(missreg[ missreg.REG_NAME == "N/A" ])
      print(f'Final : REG {len(missreg)} (miss {missr})')

    """ PACK PROVINCE """
    if 'p' in args.dopack:
      proshp = glob.glob(f'{base}/R*/R*_pro.shp')
      prodf = gpd.GeoDataFrame()
      for i, pf in enumerate(proshp):
        print(f'{i: 2d}/{len(proshp)} Pack PRO {pf}')
        pdf = gpd.read_file(pf)
        prodf = prodf.append(pdf)
        #if i > 2: break
      prodf['REG_NAME'] = [ regmap[r] for r in prodf['REG'].values ]
      prodf['PRO_NAME'] = [ promap[(r,p)] for r,p in prodf[['REG', 'PRO']].values ]

      pros = prodf[[
        'UID',
        'REG',
        'PRO',
        'REG_NAME',
        'PRO_NAME',
        'LAT',
        'LON',
        'geometry',
      ]]
      outfile = f'italy_pro'
      pros.to_file(f'{shapefolder}/{outfile}.geojson', driver='GeoJSON')
      pros.to_file(f'{shapefolder}/{outfile}.shp')
      pros.drop(columns='geometry').to_csv(f'{shapefolder}/{outfile}.csv', sep=';', index=False)

      # missing match
      missreg = pros.groupby(['REG']).first()
      misspro = pros.groupby(['REG', 'PRO']).first()
      missr = len(missreg[ missreg.REG_NAME == "N/A" ])
      missp = len(misspro[ misspro.PRO_NAME == "N/A" ])
      print(f'Final : REG {len(missreg)} (miss {missr}) PRO {len(misspro)} (miss {missp})')

    """ PACK COMUNI """
    if 'c' in args.dopack:
      comshp = glob.glob(f'{base}/R*/R*_com.shp')
      cdf = gpd.GeoDataFrame()
      for i, pf in enumerate(comshp):
        print(f'{i: 2d}/{len(comshp)} Pack COM {pf}', flush=True)
        pdf = gpd.read_file(pf)
        cdf = cdf.append(pdf)
        #if i > 2: break
      cdf['REG_NAME'] = [ regmap[r] for r in cdf['REG'].values ]
      cdf['PRO_NAME'] = [ promap[(r,p)] for r,p in cdf[['REG', 'PRO']].values ]
      cdf['COM_NAME'] = [ commap[(r,p,c)] for r,p,c in cdf[['REG', 'PRO', 'COM']].values ]

      coms = cdf[[
        'UID',
        'REG',
        'PRO',
        'COM',
        'REG_NAME',
        'PRO_NAME',
        'COM_NAME',
        'LAT',
        'LON',
        'geometry',
      ]]
      outfile = f'italy_com'
      coms.to_file(f'{shapefolder}/{outfile}.geojson', driver='GeoJSON')
      coms.to_file(f'{shapefolder}/{outfile}.shp')
      coms.drop(columns='geometry').to_csv(f'{shapefolder}/{outfile}.csv', sep=';', index=False)

      # missing match
      missreg = coms.groupby(['REG']).first()
      misspro = coms.groupby(['REG', 'PRO']).first()
      misscom = coms.groupby(['REG', 'PRO', 'COM']).first()
      missr = len(missreg[ missreg.REG_NAME == 'N/A' ])
      missp = len(misspro[ misspro.PRO_NAME == 'N/A' ])
      missc = len(misscom[ misscom.COM_NAME == 'N/A' ])
      print(f'Final : REG {len(missreg)} (miss {missr}) PRO {len(misspro)} (miss {missp}) COM {len(misscom)} (miss {missc})')

    """ PACK ACE """
    if 'a' in args.dopack:
      aceshp = glob.glob(f'{base}/R*/R*_ace.shp')
      adf = gpd.GeoDataFrame()
      for i, pf in enumerate(aceshp):
        print(f'{i: 2d}/{len(aceshp)} Pack ACE {pf}', flush=True)
        pdf = gpd.read_file(pf)
        adf = adf.append(pdf)
        #if i > 2: break

      adf['REG_NAME'] = [ regmap[r] for r in adf['REG'].values ]
      adf['PRO_NAME'] = [ promap[(r,p)] for r,p in adf[['REG', 'PRO']].values ]
      adf['COM_NAME'] = [ commap[(r,p,c)] for r,p,c in adf[['REG', 'PRO', 'COM']].values ]

      aces = adf[[
        'UID',
        'REG',
        'PRO',
        'COM',
        'ACE',
        'REG_NAME',
        'PRO_NAME',
        'COM_NAME',
        'LAT',
        'LON',
        'geometry',
      ]]
      outfile = f'italy_ace'
      aces.to_file(f'{shapefolder}/{outfile}.geojson', driver='GeoJSON')
      aces.to_file(f'{shapefolder}/{outfile}.shp')
      aces.drop(columns='geometry').to_csv(f'{shapefolder}/{outfile}.csv', sep=';', index=False)

      # missing match
      missreg = aces.groupby(['REG']).first()
      misspro = aces.groupby(['REG', 'PRO']).first()
      misscom = aces.groupby(['REG', 'PRO', 'COM']).first()
      missace = aces.groupby(['REG', 'PRO', 'COM', 'ACE']).first()
      missr = len(missreg[ missreg.REG_NAME == 'N/A' ])
      missp = len(misspro[ misspro.PRO_NAME == 'N/A' ])
      missc = len(misscom[ misscom.COM_NAME == 'N/A' ])
      print(f'Final : REG {len(missreg)} (miss {missr}) PRO {len(misspro)} (miss {missp}) COM {len(misscom)} (miss {missc}) ACE {len(missace)}')
