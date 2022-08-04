#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary
# Arg3: Timeout (in minutes)

sudo chown -R maze:maze /home/maze/maze

WORKDIR=/home/maze/workspace

OUTDIR=$WORKDIR/outputs

clang -I /home/maze/tools/klee/include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone $1 -o $WORKDIR/target.bc

# Create dummy file to indicate running start
touch $WORKDIR/.start

klee --only-output-states-covering-new=true --dump-states-on-halt=false --max-memory=4000 --max-time=$3min --output-dir $OUTDIR $WORKDIR/target.bc
