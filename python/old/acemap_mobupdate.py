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


  mobfull = pd.read_csv(m, sep='\t')
  mobfull = mobfull[ [m for m in mobfull.columns if m != ' ' and not m == 'ace_nok'] ].sum(axis=0)

  for rid, prov in istat['reg'].items():
    rtag = '{:0>3}'.format(rid)
    mobdata.loc[datetime, rtag] = mobfull.loc[ [m for m in mobfull.index if m.startswith(rtag)] ].sum(axis=0)
    for pid, com in prov['prov'].items():
      ptag = '{:0>3}{:0>3}'.format(rid,pid)
      mobdata.loc[datetime, ptag] = mobfull.loc[ [m for m in mobfull.index if m.startswith(ptag)] ].sum(axis=0)
      for cid, c in com['com'].items():
        ctag = '{:0>3}{:0>3}{:0>3}'.format(rid,pid,cid)
        mobdata.loc[datetime, ctag] = mobfull.loc[ [m for m in mobfull.index if m.startswith(ctag)] ].sum(axis=0)

# update acemap timed counters values
datetimes.sort()
istat['times'] = datetimes
for dt in datetimes:
  for rid, prov in istat['reg'].items():
    prov.setdefault('time_count', []).append(mobdata.loc[dt, '{:0>3}'.format(rid)])
    for pid, com in prov['prov'].items():
      com.setdefault('time_count', []).append(mobdata.loc[dt, '{:0>3}{:0>3}'.format(rid,pid)])
      for cid, obj in com['com'].items():
        obj.setdefault('time_count', []).append(mobdata.loc[dt, '{:0>3}{:0>3}{:0>3}'.format(rid,pid,cid)])

out = '.'.join(args.acein.split('.')[:-1]) + '-' + datetimes[0] + '-' + datetimes[-1]
with open(out + '-hr.json', 'w') as f:
  json.dump(istat, f, indent=2,  ensure_ascii=False)
with open(out + '.json', 'w') as f:
  json.dump(istat, f, ensure_ascii=False)
