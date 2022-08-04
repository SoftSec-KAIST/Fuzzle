#!/bin/bash

CRASH_DIR=$1
BIN=$2
FILE=$3

echo 'start' > triage.txt
echo $CRASH_DIR >> triage.txt
for crash in $CRASH_DIR/*crash
do
	echo $crash':' >> triage.txt
	gdb -ex 'run < '$crash -ex 'source triage.gdb' -batch $BIN
done

mv triage.txt $FILE
