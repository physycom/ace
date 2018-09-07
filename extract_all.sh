#! /bin/bash

for file in $(find data -type f -name "*.kmz")
do
  ./bin/ace $file >> ace.csv
done
