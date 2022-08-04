#!/bin/bash

MAZE=$1 # example: Wilsons_30x30_1_1_25percent_equality100_gen
TIME=$2 # in minutes

# run ecliplser
/home/maze/tools/run_eclipser.sh dummy /home/maze/maze/bin/$MAZE.bin $TIME

# collect tcs
python3 /home/maze/tools/get_tcs.py /home/maze/outputs

# get coverage info
/home/maze/tools/get_coverage.sh /home/maze/outputs /home/maze/maze/src $MAZE eclipser $TIME
