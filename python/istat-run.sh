#! /usr/bin/env bash

# Perform ISTAT shapefile analysis, merge by scale level
(time ~/Codice/ace/python/istat-ace.py -d istat_data -p -v -ma -mc -mp -mr) 2>&1 | tee log_merge_full.log

# Pack and annotate joining naming data
(time ~/Codice/ace/python/istat-ace.py -d istat_data -pa r p c a) 2>&1 | tee log_pack_full.log

# Plot to test
(time ~/Codice/ace/python/istat-plot.py -s r p c a -m) 2>&1 | tee log_plot_full.log

#(time ../python/istat-ace.py -a -r $(seq 1 20) -e a) 2>&1 | tee mergione_ace.log
#(time ../python/istat-ace.py -a -r $(seq 1 20) -e c) 2>&1 | tee mergione_com.log
#(time ../python/istat-ace.py -r $(seq 1 20) -mp) 2>&1 | tee mergione_pro.log
#(time ../python/istat-ace.py -r $(seq 1 20) -mr) 2>&1 | tee mergione_reg.log

#(time ../python/istat-ace.py -pa r) 2>&1 | tee pack_reg.log
#(time ../python/istat-ace.py -pa p) 2>&1 | tee pack_pro.log
#(time ../python/istat-ace.py -pa c) 2>&1 | tee pack_com.log
#(time ../python/istat-ace.py -pa a) 2>&1 | tee pack_ace.log
#(time ../python/istat-ace.py -pa r p c a) 2>&1 | tee pack_all.log