#!/bin/bash
OUT_PATH=$(readlink -f $(dirname "$0"))/test_output
CONFIG_DIR=$(readlink -f $(dirname "$0"))/test_config
SCRIPT_DIR=$(readlink -f $(dirname "$0")/..)/scripts
mkdir -p $OUT_PATH

cd $SCRIPT_DIR

# generate a benchmark program
python3 ./generate_benchmark.py $CONFIG_DIR/test.list $OUT_PATH/test_benchmark

# run fuzzers (AFL for 10 minutes)
OUT_TEST=$OUT_PATH/outputs
python3 ./run_tools.py $CONFIG_DIR/test.conf $OUT_TEST

# store and print results (coverage report in 'test_results.csv')
./save_results.sh $OUT_TEST $OUT_PATH/test_results "Algorithm" "0" "paper" > $OUT_PATH/test_summary

# visualize coverage
PATH_TO_TXT=$OUT_PATH/test_benchmark/txt/Wilsons_20x20_1_1.txt
PATH_TO_COV=$OUT_TEST/cov_gcov_Wilsons_20x20_1_1_25percent_default_gen_afl_0/Wilsons_20x20_1_1_25percent_default_gen_afl_0.c.gcov
python3 ./visualize.py $PATH_TO_TXT $PATH_TO_COV $OUT_PATH/visual 20

cat $OUT_PATH/test_summary