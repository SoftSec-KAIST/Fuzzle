#!/bin/bash

set -e

DOCKERDIR=$(readlink -f $(dirname "$0")/..)/dockers

# Build base image
echo "[*] Build maze-base Docker image..."
cd $DOCKERDIR/base
docker build -t maze-base .
echo "[*] Done!"

# Build AFL image
echo "[*] Build maze-afl Docker image..."
cd $DOCKERDIR/AFL
docker build -t maze-afl .
echo "[*] Done!"

# Build AFL++ image
echo "[*] Build maze-afl++ Docker image..."
cd $DOCKERDIR/AFL++
docker build -t maze-aflpp .
echo "[*] Done!"

# Build AFLGo image
echo "[*] Build maze-aflgo Docker image..."
cd $DOCKERDIR/AFLGo
docker build -t maze-aflgo .
echo "[*] Done!"

# Build Eclipser image
echo "[*] Build maze-eclipser Docker image..."
cd $DOCKERDIR/Eclipser
docker build -t maze-eclipser .
echo "[*] Done!"

# Build fuzzolic image
echo "[*] Build maze-fuzzolic Docker image..."
cd $DOCKERDIR/fuzzolic
docker build -t maze-fuzzolic .
echo "[*] Done!"
