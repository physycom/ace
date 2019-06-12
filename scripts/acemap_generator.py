#! /usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--istat", help="ISTAT comuni csv", required=True)
args = parser.parse_args()

import pandas as pd
import numpy as np

# Import ISTAT comuni
# and create map
# istat[regid]['prov'][provid]['com'][comid] = {
#  'name'      : 'Bologna'
#  'centroid'  : [0,0]
#  'sez_count' : 0
#}
dfistat = pd.read_csv(args.istat, sep=';', encoding='latin-1')
dfistat.dropna(subset = ['Codice Regione'], inplace=True)

istat = {}
for index, row in dfistat.iterrows():
  regid = int(row['Codice Regione'])
  try:
    provid = int(row['Codice Provincia (1)'])
    provname = row['Denominazione provincia']

    comid = int(row['Progressivo del Comune (2)'])
    comname = row['Denominazione in italiano']
  except:
    print(row)
    continue

  if regid not in istat:
    istat[regid] = {}
    istat[regid]['name'] = row['Denominazione regione']
    istat[regid]['prov'] = {}

  if provid not in istat[regid]['prov']:
    istat[regid]['prov'][provid] = {}
    istat[regid]['prov'][provid]['com'] = {}
    if provname != '-':
      istat[regid]['prov'][provid]['name'] = provname
    else:
      istat[regid]['prov'][provid]['name'] = row[u'Denominazione Città metropolitana']

  if comid not in istat[regid]['prov'][provid]['com']:
    istat[regid]['prov'][provid]['com'][comid] = {}
    istat[regid]['prov'][provid]['com'][comid]['name'] = comname
    istat[regid]['prov'][provid]['com'][comid]['centroid'] = [0,0]
    istat[regid]['prov'][provid]['com'][comid]['sez_count'] = 0

# Print istat map on stdout
def view(verbose):
  reg_tot = 0
  prov_tot = 0
  com_tot = 0
  for r, v in istat.items():
    reg_tot += 1
    if verbose:
      print('- {:03d} - {:<35s} ({: 2d}) '.format(r, v['name'], len(v['prov'])))
    for c, n in v['prov'].items():
      prov_tot += 1
      com_tot += len(n['com'])
      if verbose:
        print('\t* {:03d} - {:<35s} ({: 4d})'.format(c, n['name'], len(n['com'])))
        #print('{}'.format(n['com'].keys()))
  print("ISTAT tot reg  :",reg_tot)
  print("ISTAT tot prov :",prov_tot)
  print("ISTAT tot com  :",com_tot)
view(True)

import json
with open('acemap-empty-hr.json', 'w') as f:
  json.dump(istat, f, indent=2,  ensure_ascii=False)
with open('acemap-empty.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)
