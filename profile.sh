#!/bin/sh
python gprof2dot.py -fpstats  profile.tmp | dot -Tpng -o profile.png
