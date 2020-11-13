#! /usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--istat", help="ISTAT comuni csv", required=True)
args = parser.parse_args()

import pandas as pd
import numpy as np

# Import ISTAT comuni selected columns
dfistat = pd.read_csv(args.istat, sep=';', encoding='latin-1',
  usecols=[
    'Codice Regione',
    'Codice Provincia (1)',
    'Progressivo del Comune (2)',
    'Denominazione provincia',
    u'Denominazione Città metropolitana',
    'Denominazione in italiano',
    'Denominazione regione'
  ]
)
dfistat['prov_name'] = np.where(dfistat['Denominazione provincia']=='-', dfistat[u'Denominazione Città metropolitana'], dfistat['Denominazione provincia'])
dfistat.drop(columns=['Denominazione provincia', u'Denominazione Città metropolitana'])
dfistat.dropna(subset = ['Codice Regione'], inplace=True)


# and create map
# istat[regid]['prov'][provid]['com'][comid] = {
#  'name'      : 'Bologna'
#  'centroid'  : [0,0]
#  'sez_count' : 0
#}
import collections
def empty_nested_dict(dim=3):
  if dim==1:
    return collections.defaultdict(int)
  else:
    return collections.defaultdict(lambda: empty_nested_dict(dim-1))

istat = empty_nested_dict(7)
for index, row in dfistat.iterrows():
  regid = int(row['Codice Regione'])
  provid = int(row['Codice Provincia (1)'])
  comid = int(row['Progressivo del Comune (2)'])

  istat['reg'][regid]['name'] = row['Denominazione regione']
  istat['reg'][regid]['prov'][provid]['name'] = row['prov_name']
  istat['reg'][regid]['prov'][provid]['com'][comid]['name'] = row['Denominazione in italiano']
  istat['reg'][regid]['prov'][provid]['com'][comid]['centroid'] = [0,0]
  istat['reg'][regid]['prov'][provid]['com'][comid]['sez_count'] = 0

# Print istat map on stdout
def view(verbose, com_verbose):
  reg_tot = 0
  prov_tot = 0
  com_tot = 0
  for r, v in istat['reg'].items():
    reg_tot += 1
    if verbose:
      print('- {:03d} - {:<35s} ({: 2d}) '.format(r, v['name'], len(v['prov'])))
    for p, n in v['prov'].items():
      prov_tot += 1
      com_tot += len(n['com'])
      if verbose:
        print('\t* {:03d} - {:<35s} ({: 4d})'.format(p, n['name'], len(n['com'])))
        if com_verbose:
          for c, m in n['com'].items():
            print('\t\t+ {:03d} - {:<35s} {:03}|{:03}|{:03}'.format(c, m['name'], r, p, c))
  print("ISTAT tot reg  :",reg_tot)
  print("ISTAT tot prov :",prov_tot)
  print("ISTAT tot com  :",com_tot)
view(True, False)

import json
with open('acemap-empty-hr.json', 'w') as f:
  json.dump(istat, f, indent=2, ensure_ascii=False)
with open('acemap-empty.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)
