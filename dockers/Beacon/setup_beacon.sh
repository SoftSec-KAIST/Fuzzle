#!/bin/bash

## Beacon is only provided in prebuilt forms.
## Consequently, we need to match the llvm version that built Beacon.
## However, building llvm 4 in our environment was not trivial.
## Therefore, we use the both Beacon and llvm4 as prebuilt forms,
## directed extracted from the official Beacon docker image.
## They are copied to docker by the Dockerfile.
cd /home/maze/tools/beacon
cat /home/maze/tools/beacon/llvm4.tar.gz* > /home/maze/tools/beacon/llvm4.tar.gz
tar -zxf /home/maze/tools/beacon/llvm4.tar.gz
rm /home/maze/tools/beacon/llvm4.tar.gz*

