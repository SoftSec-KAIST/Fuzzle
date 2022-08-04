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

# Create dummy file to indicate running start
touch $WORKDIR/.start

timeout $3m afl-fuzz -i $INDIR -o $OUTDIR -Q -- $2
