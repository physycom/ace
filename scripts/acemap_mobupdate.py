#! /usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--acein", help="acemap JSON file", required=True)
parser.add_argument("-f", "--fpr", help="OLIVETTI fpr data regex", required=True)
args = parser.parse_args()

import pandas as pd
import numpy as np
import json
import glob
import re

with open(args.acein) as f:
  istat = json.load(f)

mobfiles = glob.glob(args.fpr)
mobdata = pd.DataFrame()
datetimes = []
for m in mobfiles:
  datetime = re.search(r'\d{8}_\d{4}', m).group(0)
  datetimes.append(datetime)
  print('Processing: ',m.split('/')[-1], datetime)

  mob = pd.read_csv(m, sep='\t')
  mob = mob[ [m for m in mob.columns if m != ' ' and not m == 'ace_nok'] ]
  #print(mob.shape)

  for rid, prov in istat.items():
    for pid, com in prov['prov'].items():
      for cid, c in com['com'].items():
        acetag = '{:0>3}{:0>3}{:0>3}'.format(rid,pid,cid)
        rtag = '{:0>3}'.format(rid)
        mob[rtag] = mob[ [m for m in mob.columns if m.startswith(rtag)] ].sum(1)
#        print(acetag)

#  print(mob.shape)
#  print(mob[ [c for c in mob.columns if len(c) == 3] ])

  if mobdata.shape == (0,0):
    mobdata = pd.DataFrame(columns=mob.columns)
  mobdata.loc[datetime] = pd.Series(mob.sum())
datetimes.sort()

# Update acemap timed counters values
for rid, prov in istat.items():
  prov['time_count'] = {}
  for dt in datetimes:
    prov['time_count'][dt] = mobdata.loc[dt, '{:0>3}'.format(rid)]

#print(mobdata)
#print(mobdata.loc[datetimes[0],'019'])
out = '.'.join(args.acein.split('.')[:-1]) + '-' + datetimes[0] + '-' + datetimes[-1]
with open(out + '-hr.json', 'w') as f:
  json.dump(istat, f, indent=2,  ensure_ascii=False)
with open(out + '.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)


#  newrow = pd.Series(mob.sum())
#  newrow[' '] = 'Total'
#  mob.loc[mob.shape[0]] = newrow
#  print(mob.shape)
#  print(mob.to_string())

"""
  pattern = '001001120'
  print(mob.columns)
  mob = mob[[' '] + cols]
  print(mob)



reg_tag = args.shape.split('/')[-1][:3]
with open(args.shape) as f:
  shape = json.load(f)

com_fail = 0
prov_fail = 0
for f in shape['features']:
  reg = str(int(f['properties']['COD_REG']))
  pc = int(f['properties']['PRO_COM'])
  prov = str(pc // 1000)
  com = str(pc - int(prov) * 1000)
  sez_type = f['geometry']['type']
  if sez_type == 'Polygon':
    if len(f['geometry']['coordinates'][0]) == 1:
      sez_poly = np.array(f['geometry']['coordinates'])
    elif len(f['geometry']['coordinates'][0]) > 1:
      sez_poly = np.array([f['geometry']['coordinates'][0]])
    #print(sez_type,"-",pc, sez_poly.shape)
  elif sez_type == 'MultiPolygon':
    if len(f['geometry']['coordinates'][0]) == 1:
      sez_poly = np.array(f['geometry']['coordinates'][0])
    elif len(f['geometry']['coordinates'][0]) > 1:
      sez_poly = np.array([f['geometry']['coordinates'][0][0]])
  else:
    print("ERROR:",pc, "unhandled feature type", sez_type)
    continue

  sez_lonm = sez_poly[0,:,0].sum() / len(sez_poly[0,:,0])
  sez_latm = sez_poly[0,:,1].sum() / len(sez_poly[0,:,1])

  if prov not in istat[reg]['prov']:
    prov_fail += 1
    continue
  else:
    if com not in istat[reg]['prov'][prov]['com']:
      com_fail += 1
      continue

  n = istat[reg]['prov'][prov]['com'][com]['sez_count']
  istat[reg]['prov'][prov]['com'][com]['sez_count'] += 1

  c = istat[reg]['prov'][prov]['com'][com]['centroid']
  c[0] = (n*c[0] + sez_lonm)/(n+1)
  c[1] = (n*c[1] + sez_latm)/(n+1)
  istat[reg]['prov'][prov]['com'][com]['centroid'] = c

print("Parsed input region     :", args.shape, reg_tag, istat[str(int(reg_tag[1:]))]['name'])
print("ISTAT tot sezioni       :", len(shape['features']))
print("ISTAT fail prov-match   :", prov_fail)
print("ISTAT fail comune-match :", com_fail)

out = args.acein.split('.')[0] + '_' + reg_tag
with open(out + '-hr.json', 'w') as f:
  json.dump(istat, f, indent=2,  ensure_ascii=False)
with open(out + '.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)
"""