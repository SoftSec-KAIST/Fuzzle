#!/bin/bash

set -e

#DOCKERDIR=$(readlink -f $(dirname "$0")/..)/dockers/Eclipser_debug

# Build base image
echo "[*] Build maze-base Docker image..."
cd base
docker build -t maze-base .
echo "[*] Done!"
cd ..

# Build Eclipser image
echo "[*] Build maze-eclipser Docker image..."
cd Eclipser
docker build -t maze-eclipser-debug .
echo "[*] Done!"
