#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary
# Arg3: Timeout (in minutes)

sudo chown -R maze:maze /home/maze/maze

WORKDIR=/home/maze/workspace

INDIR=$WORKDIR/inputs
OUTDIR=$WORKDIR/outputs

# Create dummy input directory
mkdir -p $INDIR
echo 'A' > $INDIR/seed

# Create configuration file
DIRNAME=`dirname $2`
BINNAME=`basename $2`
CONFPATH=$DIRNAME/$BINNAME.fuzzolic
echo 'SYMBOLIC_INJECT_INPUT_MODE=READ_FD_0' > $CONFPATH

# Create dummy file to indicate running start
touch $WORKDIR/.start

timeout $3m /home/maze/tools/fuzzolic/fuzzolic/run_afl_fuzzolic.py --address-reasoning --fuzzy -o $OUTDIR -i $INDIR -- $2
