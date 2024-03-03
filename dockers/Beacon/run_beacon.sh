#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary (dummy)
# Arg3: Timeout (in minutes)

sudo chown -R maze:maze /home/maze/maze

TTE=$((3*$3/4))

CLANGDIR=/home/maze/tools/beacon/llvm4/bin
WORKDIR=/home/maze/workspace

INDIR=$WORKDIR/inputs
OUTDIR=$WORKDIR/outputs

# Create dummy input directory
mkdir -p $INDIR
echo '' > $INDIR/seed

cp $1 $WORKDIR/file.c
cd $WORKDIR

BEACON=/home/maze/tools/beacon;

ABORT_LINE=`awk '/abort*/ { print NR }' file.c`

echo 'file.c:'$ABORT_LINE > $WORKDIR/BBtargets.txt

# make bc file
$CLANGDIR/clang -g -c -emit-llvm $WORKDIR/file.c -o $WORKDIR/file.bc

# pre-work
$BEACON/precondInfer $WORKDIR/file.bc --target-file=$WORKDIR/BBtargets.txt --join-bound=5 >precond_log 2>&1

$BEACON/Ins -output=$WORKDIR/beacon_file.bc -byte -blocks=$WORKDIR/bbreaches__home_maze_workspace_BBtargets.txt -afl -log=log.txt -load=$WORKDIR/range_res.txt $WORKDIR/transed.bc

$CLANGDIR/clang $WORKDIR/beacon_file.bc -o $WORKDIR/file.bin -lm -lz -ldl $BEACON/afl-llvm-rt.o

# Create dummy file to indicate running start
touch $WORKDIR/.start

# fuzz
timeout $3m $BEACON/afl-fuzz -i $INDIR -o $OUTDIR -m none -d -- $WORKDIR/file.bin
