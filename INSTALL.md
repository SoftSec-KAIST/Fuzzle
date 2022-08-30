# Installation

## Requirements

- Linux with Python 3.7+
- Z3 solver

## Clone repository

To start building Fuzzle, first clone the git repo:

```
$ git clone https://github.com/SoftSec-KAIST/Fuzzle
$ cd Fuzzle
```

## Installing Dependencies

To install dependencies for generating benchmarks, run the following from
`Fuzzle` directory:

```
$ python3 -m pip install -r ./maze-gen/requirements.txt
```

Additionally, you will need to have Z3 solver installed for handling .smt2 files
from CVEs. Below are the instructions for installing Z3 solver using pySMT's
install command. Note that pySMT should have been installed in the previous
step as one of the dependencies for Fuzzle.

```
$ pysmt-install --z3
```

To check that the solver was installed correctly, you can use the following
command:

```
$ pysmt-install --check
```

## Building Docker Images

To run the fuzzers on the generated benchmark, you must first build the
corresponding docker images:

```
$ ./scripts/build_all_dockers.sh
```

Note that this may take a few hours depending on your machine.

## Basic Usage Example

Once the installation is complete, you can quickly check that everything is
working correctly by running `test.sh`.

```
$ ./test/test.sh
```

This will first generate a benchmark program, run AFL, save results, and
generate coverage visualization. The output will be automatically saved in
`test_output` directory under `test` directory.

Note that this script will take approximately 16 minutes in total.

After the script finishes running, you should have something similar to the
below printed out to the screen:

```
Measure:        Coverage (%)
################################
Tool            Algorithm
                Wilsons
--------------------------------
afl             40.0
--------------------------------

Measure:        Bugs (%)
################################
Tool            Algorithm
                Wilsons
--------------------------------
afl             0
--------------------------------

Measure:        TTE (h)
################################
Tool            Algorithm
                Wilsons
--------------------------------
afl             -
--------------------------------
```

The `test_output` directory should also contain `visual.png` which is the visual
aid generated from the run.

## Additional Notes

- The installation and run scripts for Fuzzle were tested on Ubuntu 20.04.
- Building docker images and running fuzzers using `run_tools.py` require superuser access.

