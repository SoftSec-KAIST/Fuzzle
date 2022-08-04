#!/bin/bash

TC_DIR=$1
TARGET_DIR=$2
TARGET=$3
MAZE_TOOL=$4
DURATION=$5 # in minutes
NUMB_HOURS=$((DURATION/60))

python3 /home/maze/tools/convert_to_cov_code.py $TARGET_DIR/$TARGET
gcc -fprofile-arcs -ftest-coverage -o gcov-bin $TARGET_DIR/$TARGET'_cov.c'
mkdir $TC_DIR/cov_txt_$MAZE_TOOL $TC_DIR/cov_gcov_$MAZE_TOOL

if [ $NUMB_HOURS -lt 1 ]
then
	for tc in $TC_DIR/*tc
	do
		cat $tc | ./gcov-bin
	done

	for crash in $TC_DIR/*crash
	do
		cat $crash | ./gcov-bin
		if (($? == 134)); then
			mv $crash $crash'_abort'
			break
		fi
	done

	gcov -b -c -s $TARGET_DIR $TARGET'_cov.c' > $TC_DIR/cov_txt_$MAZE_TOOL/$MAZE_TOOL.txt
	ls $TC_DIR/*crash_abort | head -1 >> $TC_DIR/cov_txt_$MAZE_TOOL/$MAZE_TOOL.txt
	mv $TARGET'_cov.c.gcov' $TC_DIR/cov_gcov_$MAZE_TOOL/$MAZE_TOOL.c.gcov
fi

HOUR=1
while [ $HOUR -le $NUMB_HOURS ]
do
	for tc in $TC_DIR/*tc
	do
		TIMESTAMP=${tc:19:5}
		if [ $TIMESTAMP -ge $(((HOUR-1)*3600)) ] && [ $TIMESTAMP -lt $((HOUR*3600)) ]
		then
			cat $tc | ./gcov-bin
		fi
	done

	for crash in $TC_DIR/*crash
	do
		TIMESTAMP=${crash:19:5}
		if [ $TIMESTAMP -ge $(((HOUR-1)*3600)) ] && [ $TIMESTAMP -lt $((HOUR*3600)) ]
		then
			cat $crash | ./gcov-bin
			if (($? == 134)); then
				mv $crash $crash'_abort'
				break
			fi
		fi
	done

	gcov -b -c -s $TARGET_DIR $TARGET'_cov.c' > $TC_DIR/cov_txt_$MAZE_TOOL/$MAZE_TOOL'_'$HOUR'hr.txt'
	ls $TC_DIR/*crash_abort | head -1 >> $TC_DIR/cov_txt_$MAZE_TOOL/$MAZE_TOOL'_'$HOUR'hr.txt'
	mv $TARGET'_cov.c.gcov' $TC_DIR/cov_gcov_$MAZE_TOOL/$MAZE_TOOL'_'$HOUR'hr.c.gcov'
	((HOUR++))
done