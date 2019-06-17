#! /usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--acein", help="original acemap JSON file", required=True)
parser.add_argument("-s", "--shape", help="ISTAT shape geojson (e.g. R01_11_WGS84.geojson)", required=True)
args = parser.parse_args()

import numpy as np
import json

# Import ISTAT SEZIONI DI CENSIMENTO geometry geojson
# and update istat map values
with open(args.acein) as f:
  istat = json.load(f)

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

  if prov not in istat['reg'][reg]['prov']:
    prov_fail += 1
    continue
  else:
    if com not in istat['reg'][reg]['prov'][prov]['com']:
      com_fail += 1
      continue

  n = istat['reg'][reg]['prov'][prov]['com'][com]['sez_count']
  istat['reg'][reg]['prov'][prov]['com'][com]['sez_count'] += 1

  c = istat['reg'][reg]['prov'][prov]['com'][com]['centroid']
  c[0] = (n*c[0] + sez_lonm)/(n+1)
  c[1] = (n*c[1] + sez_latm)/(n+1)
  istat['reg'][reg]['prov'][prov]['com'][com]['centroid'] = c


print("Parsed input region     :", args.shape, reg_tag, istat['reg'][str(int(reg_tag[1:]))]['name'])
print("ISTAT tot sezioni       :", len(shape['features']))
print("ISTAT fail prov-match   :", prov_fail)
print("ISTAT fail comune-match :", com_fail)

out = args.acein.split('.')[0] + '_' + reg_tag
with open(out + '-hr.json', 'w') as f:
  json.dump(istat, f, indent=2,  ensure_ascii=False)
with open(out + '.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)
