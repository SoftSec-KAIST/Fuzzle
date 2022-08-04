#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary
# Arg3: Timeout (in minutes)

sudo chown -R maze:maze /home/maze/maze

TTE=$((3*$3/4))

WORKDIR=/home/maze/workspace

INDIR=$WORKDIR/inputs
OUTDIR=$WORKDIR/outputs

# Create dummy input directory
mkdir -p $INDIR
echo 'A' > $INDIR/seed

cp $1 $WORKDIR/file.c

mkdir obj-aflgo; mkdir obj-aflgo/temp;
AFLGO=/home/maze/tools/afl; SUBJECT=$PWD; TMP_DIR=$PWD/obj-aflgo/temp

ABORT_LINE=`awk '/abort*/ { print NR }' file.c`

echo 'file.c:'$ABORT_LINE > $TMP_DIR/BBtargets.txt

# first build
$AFLGO/afl-clang-fast -targets=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps -lpthread -o file.bin file.c

# clean up
cat $TMP_DIR/BBnames.txt | rev | cut -d: -f2- | rev | sort | uniq > $TMP_DIR/BBnames2.txt && mv $TMP_DIR/BBnames2.txt $TMP_DIR/BBnames.txt
cat $TMP_DIR/BBcalls.txt | sort | uniq > $TMP_DIR/BBcalls2.txt && mv $TMP_DIR/BBcalls2.txt $TMP_DIR/BBcalls.txt

# generate distances
$AFLGO/scripts/genDistance.sh $SUBJECT $TMP_DIR file.bin
# second build
$AFLGO/afl-clang-fast -g -distance=$TMP_DIR/distance.cfg.txt -lpthread -o file_run.bin file.c

# Create dummy file to indicate running start
touch $WORKDIR/.start

# fuzz
timeout $3m $AFLGO/afl-fuzz -z exp -c $TTE -i $INDIR -o $OUTDIR -- ./file_run.bin
