#!/bin/bash

while getopts a:w:h:o:r:n:c:g:s:e: option
do
    case "${option}"
    in
    a) ALGORITHM=${OPTARG};;
    w) WIDTH=${OPTARG};;
    h) HEIGHT=${OPTARG};;
    o) OUTPUT_DIR=${OPTARG};;
    r) SEED=${OPTARG};;
    n) NUMB=${OPTARG};;
    c) CYCLE=${OPTARG};;
    g) GEN=${OPTARG};;
    s) SMT_PATH=${OPTARG};;
    e) EXIT=${OPTARG};;
    esac
done

if [ -z ${ALGORITHM+x} ]; then
    echo "No algorithm selected. Exiting..."
    exit 1
fi

if [[ -z ${WIDTH+x} || -z ${HEIGHT+x} ]]; then
    echo "Size of maze was not specified. Exiting..."
    exit 1
fi

case "${WIDTH#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid size input: width should be a positive integer"
        exit 1;;
esac

case "${HEIGHT#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid size input: height should be a positive integer"
        exit 1;;
esac

(($WIDTH < 3)) && { echo "Invalid size input: width should be greater than 2"; exit 1; }
(($HEIGHT < 3)) && { echo "Invalid size input: height should be greater than 2"; exit 1; }

if [ -z ${OUTPUT_DIR+x} ]; then
    echo "Output directory not specified. Exiting..."
    exit 1
fi

if [ -z ${NUMB+x} ]; then
    echo "NOTE: The number of mazes to generate was not specified. Default value of 1 will be used."
    NUMB=1
fi

case "${NUMB#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid input: number of mazes to generate should be a positive integer"
        exit 1;;
esac

(($NUMB < 1)) && { echo "Invalid input: number of mazes should be greater than 0"; exit 1; }

if [ -z ${SEED+x} ]; then
    echo "NOTE: The seed was not specified. Default value of 1 will be used."
    SEED=1
fi

if [ -z ${CYCLE+x} ]; then
    echo "NOTE: The percentage of cycles was not specified. Default value of 100 will be used."
    CYCLE="100"
fi

if [ -z ${EXIT+x} ]; then
    EXIT="default"
fi

if [ -z ${GEN+x} ]; then
    echo "NOTE: The program generator was not specified. Default generator will be used."
    GEN="default_gen"
fi

echo "Generating mazes..."
echo "##############################################"
echo "Algorithm: "$ALGORITHM
echo "Size: "$WIDTH" by "$HEIGHT
echo "Maze exit: "$EXIT
echo "Pseudo-random seed: "$SEED
echo "Remaining cycles: "$CYCLE"%"
echo "Number of mazes: "$NUMB
echo "Generator used: "$GEN
echo "Output directory: "$OUTPUT_DIR
echo "##############################################"

mkdir -p $OUTPUT_DIR/src $OUTPUT_DIR/bin $OUTPUT_DIR/png $OUTPUT_DIR/txt $OUTPUT_DIR/sln
MAZEGEN_DIR=$(readlink -f $(dirname "$0")/..)/maze-gen

for (( INDEX=1; INDEX<=$NUMB; INDEX++ ))
do
    NAME=$ALGORITHM"_"$WIDTH"x"$HEIGHT"_"$SEED"_"$INDEX
    python3 $MAZEGEN_DIR/array_gen.py $ALGORITHM $WIDTH $HEIGHT $SEED $EXIT $INDEX
    if [ $? -eq 1 ]; then
        echo "Select one of the following algorithms: Backtracking, Kruskal, Prims, Wilsons, Sidewinder"
        exit 1
    fi
    if [[ "$GEN" == *"CVE"* ]]; then
        SMT_NAME=$(basename $SMT_PATH .smt2)
        NAME_P=$NAME"_"$CYCLE"percent_"$SMT_NAME"_gen"
        python3 $MAZEGEN_DIR/array_to_code.py $NAME $WIDTH $HEIGHT $CYCLE $SEED $GEN $SMT_PATH
    else
        NAME_P=$NAME"_"$CYCLE"percent_"$GEN
        python3 $MAZEGEN_DIR/array_to_code.py $NAME $WIDTH $HEIGHT $CYCLE $SEED $GEN
    fi
    gcc -O3 -w -o $NAME_P".bin" $NAME_P".c"
    mv $NAME".png" $OUTPUT_DIR/png
    mv $NAME".txt" $OUTPUT_DIR/txt
    mv $NAME_P".c" $OUTPUT_DIR/src
    mv $NAME_P".bin" $OUTPUT_DIR/bin
    mv $NAME"_solution.txt" $OUTPUT_DIR/sln
done

echo "Done!"
