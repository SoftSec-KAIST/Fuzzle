#!/bin/bash

# stores the raw data in .csv file
# and prints the summarized results to the screen
FUZZ_OUTPUT=$1
OUT_PATH=$2
PARAM=$3
DURATION=$4
MODE=$5

SCRIPT_DIR=$(readlink -f $(dirname "$0"))

ls $FUZZ_OUTPUT/cov_txt*/*txt > $FUZZ_OUTPUT/coverage_files
python3 $SCRIPT_DIR/save_results.py $FUZZ_OUTPUT/coverage_files $OUT_PATH $PARAM $DURATION $MODE
