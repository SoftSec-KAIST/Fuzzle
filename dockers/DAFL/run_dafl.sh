#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary
# Arg3: Timeout (in minutes)

set -e

WORKDIR=/home/maze/workspace
OUTDIR=$WORKDIR/outputs
INDIR=$WORKDIR/dafl-input

rm -rf $WORKDIR/src/*
rm -rf $INDIR/*

# copy makefile
cp /home/maze/script/clang-compile.mk $WORKDIR/src/Makefile
cp /home/maze/script/dafl-compile-noasan.mk $INDIR/Makefile

# target source code copy
cp $1 $WORKDIR/src/file.c
cp $1 $INDIR/file.c

# run smake
cd $WORKDIR/src
yes | /home/maze/smake/smake --init
/home/maze/smake/smake -j 1
cp sparrow/file/00.file.c.i ./

# target line set
TARGET_LINE=$(awk '/\tfunc_bug*/ { print NR }' file.c)
TARGET="file.c:$TARGET_LINE"

# run sparrow
mkdir -p $WORKDIR/src/sparrow-output
/home/maze/sparrow/bin/sparrow -outdir $WORKDIR/src/sparrow-output -frontend cil -unsound_alloc -unsound_const_string \
-unsound_recursion -unsound_noreturn_function -unsound_skip_global_array_init 1000 -skip_main_analysis -cut_cyclic_call \
-unwrap_alloc -entry_point main -max_pre_iter 100 -slice target="$TARGET" $WORKDIR/src/00.file.c.i

cp $WORKDIR/src/sparrow-output/target/slice_func.txt $INDIR/target_selective_cov
cp $WORKDIR/src/sparrow-output/target/slice_dfg.txt $INDIR/target_dfg

# DAFL Compile
export DAFL_SELECTIVE_COV="$INDIR/target_selective_cov"
export DAFL_DFG_SCORE="$INDIR/target_dfg"
cd $INDIR
make

# Fuzzing setting
unset ASAN_OPTIONS
export AFL_NO_AFFINITY=1
export AFL_SKIP_CRASHES=1
export UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

# Create dummy file to indicate running start
touch $WORKDIR/.start

timeout $3m /home/maze/fuzzer/DAFL/afl-fuzz -m none -d -i /home/maze/seed -o $OUTDIR -- /home/maze/workspace/dafl-input/file_dafl
