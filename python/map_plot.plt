#! /usr/bin/env gnuplot

file_map="map.txt"
file_vector="vector.txt"

set terminal pdf enhanced

set xlabel "lon"
set ylabel "lat"

set output "map.pdf"
plot file_map u 3:2 w dots lt 1 lc rgb "red" t 'mappa'

set output "vector.pdf"
plot file_vector u 3:2 w dots lt 1 lc rgb "blue" t 'vettore'
