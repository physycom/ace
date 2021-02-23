#! /usr/bin/env python3

import geopandas as gpd
import pandas as pd
import argparse
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import contextily as ctx
from shapely import geometry

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dodata', help='parse OD data file', action='store_true')
args = parser.parse_args()

if args.dodata:
  datafiles = glob.glob('od_italia_15/*.tsv')

  for dataf in datafiles:
    print(f'Processing : {dataf}')
    df = pd.read_csv(dataf, sep='\t')

    print(df)
    print(df.columns)

    orig = data.index

    break

  acefile = 'ace_complete.csv'
  acedf = pd.read_csv(acefile, sep=';')
  print(acedf)
