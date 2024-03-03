#!/bin/bash

WORKDIR=/home/maze/workspace
BINARY=$WORKDIR/file_run.bin
OUTDIR=/home/maze/outputs
SCRIPT_DIR=/home/maze/tools/triage

mkdir -p $OUTDIR/triage
$SCRIPT_DIR/triage.sh $OUTDIR $BINARY $OUTDIR/triage/trace > /dev/null 2>&1
