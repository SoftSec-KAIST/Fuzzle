#!/bin/bash

CRASH_DIR=$1
BIN=$2
FILE=$3

for crash in $CRASH_DIR/*crash
do
	echo $crash':' >> triage.txt
	gdb -ex 'run < '$crash -ex 'source /home/maze/tools/triage/triage.gdb' -batch $BIN
done

mv triage.txt $FILE
