# Fuzzle

Fuzzle is a bug synthesizer that generates buggy benchmarks for evaluating
fuzzers. Fuzzle uses randomly created mazes and path constraints from previous
CVEs to generate subject programs. The details of Fuzzle can be found in our
paper "Fuzzle: Making a Puzzle for Fuzzers" (ASE 2022).

# Modifications

Fuzzle was modified to generate programs that contain multiple bugs for evaluating multi-target directed fuzzers. The details can be found in the paper "On the Effectiveness of Synthetic Benchmarks for Evaluating Directed Grey-box Fuzzers" (APSEC 2023).

## Installation

To build Fuzzle and setup the docker and python environment, run the following:

```
$ git clone https://github.com/SoftSec-KAIST/Fuzzle
$ cd Fuzzle

# Build docker images (this step may take a few hours to complete)
$ ./scripts/build_all_dockers.sh

# Install the dependencies
$ python3 -m pip install -r ./maze-gen/requirements.txt
```
Note that you need python 3.7+ and Z3 solver to generate benchmark programs
using Fuzzle.

For more detailed installation instructions, please see  `INSTALL.md`.

## Usage

For a quick tutorial on how to use Fuzzle, please skip to the
[tutorial](#tutorial).

### Generating a benchmark

You can generate a buggy benchmark using `generate.sh` in the `scripts`
directory. You need to specify values for the following parameters using the
command line arguments:
- Maze generation algorithm (`-a`): Backtracking, Kruskal, Prims, Wilsons,
  Sidewinder
- Width of the maze (`-w`): any integer greater than 2
- Height of the maze (`-h`): any integer greater than 2
- Output directory (`-o`): path to the output directory

You can optionally specify the following parameters:
- Pseudorandom seed (`-r`): any integer between 0 and 2^32 - 1
- Percentage of cycles (`-c`): any integer between 0 and 100
- Maze exit (`-e`): default or random
- Generator (`-g`): default_gen or CVE_gen

Note, if you use CVE_gen for the generator, you must also provide a path to SMT
file with `-s` option.

For example, the following command generates a default program based on a 10x10
maze created with Wilson's algorithm.

```
$ ./scripts/generate.sh -a Wilsons -w 10 -h 10 -o <OUT_PATH>
```

A different program can be generated using the same maze but with realistic
constraints obtained from the previous CVE (e.g., CVE-2016-4487).

```
$ ./scripts/generate.sh -a Wilsons -w 10 -h 10 -g CVE_gen -s ./CVEs/CVE-2016-4487.smt2 -o <OUT_PATH>
```

After the script finishes running, the output directory specified with
`<OUT_PATH>` will contain 5 subdirectories as follows:

- `src`: contains C source code of generated programs
- `bin`: contains compiled binaries of generated programs
- `txt`: contains array form of mazes used in generating programs
- `png`: contains images (.png files) of mazes used
- `sln`: contains the shortest solution path for each maze


### Generating a large benchmark

To generate multiple programs for building a large benchmark, you can use
`generate_benchmark.py` as follows:

```
$ cd scripts
$ python3 ./generate_benchmark.py <FILE_PATH> <OUT_PATH>
```

Here, `<FILE_PATH>` is a path to the file that specifies the configuration of
programs to be generated. The template for the configuration of a program is:

```
<algorithm>,<width>,<height>,<seed>,<index>,<percentage of cycles>,<generator>
```

Below is an example file for the two programs generated above with
`generate.sh`.

```
Wilsons,10,10,1,1,100percent,default_gen
Wilsons,10,10,1,1,100percent,CVE-2016-4487_gen
```

### Running a fuzzing experiment

To run fuzzers on the generated benchmark in a separate docker container:

```
$ python3 ./scripts/run_tools.py <CONFIG_FILE> <FUZZ_OUT>
```

An example of the configuration file (`<CONFIG_FILE>`) is provided below.

```
{
    "MazeList" : "../examples/example1.list",
    "Repeats"  : 1,
    "Duration" : 60,
    "MazeDir"  : "../examples/example1_benchmark",
    "Tools"    : ["afl", "afl++", "aflgo", "eclipser", "fuzzolic"]
}
```

- `MazeList`: path to the list of programs in the benchmark
- `Repeats`: number of repeats for each fuzzer
- `Duration`: length of fuzzing campaign in minutes
- `MazeDir`: path to a directory that contains benchmark programs
- `Tools`: one or more of the available fuzzers (`afl`, `afl++`, `aflgo`,
  `eclipser`, `fuzzolic`)

Note that all paths (`MazeList` and `MazeDir`) should be either absolute paths
or relative paths from the `scripts` directory.

More examples of configuration files are provided under `examples` directory.
Running each example should take about 1 hour. Please refer to
[Examples](#examples) section for more details.

After the experiment is finished, the output directory (`<FUZZ_OUT>`) will
contain generated testcases from each run as well as code coverage measured with
gcov.

### Storing and summarizing results

Once the fuzzing campaign is finished, the coverage and bug finding results can
be summarized in csv format using the script as follows:

```
$ ./scripts/save_results.sh <FUZZ_OUT> <FILE_PATH> <PARAM> <DURATION> <MODE>
```

- `<FUZZ_OUT>`: directory that contains fuzzing outputs
- `<FILE_PATH>`: path to save the output file

The script summarizes the fuzzing results based on the given parameter and
fuzzing duration. For example, by running:

```
$ ./scripts/save_results.sh <FUZZ_OUT> <FILE_PATH> Algorithm 24 paper
```
each fuzzer's performance after 24 hours across different maze generation
algorithms will be displayed on the screen.

- `<PARAM>`: one of four parameters of Fuzzle (`Algorithm`, `Size`, `Cycle`, `Generator`)
- `<DURATION>`: length of fuzzing campaign in hours
- `<MODE>`: `paper` for displaying tables similar to the ones shown in the
  paper, `fuzzer` for displaying summarized results for each fuzzer.

### Visualizing coverage results

You can also visualize the code coverage results in the form of 2D maze, where
each cell represents a function in the program. The script for visualization
takes maze array (.txt), coverage results (.gcov), and maze size as input and
returns a png file.

```
$ python3 ./scripts/visualize.py <TXT_PATH> <COV_PATH> <OUT_PATH> <SIZE>
```
- `<TXT_PATH>`: path to .txt file for the chosen maze. Note that such files are
  automatically created under the `txt` directory when generating a benchmark.
- `<COV_PATH>`: path to .gcov file that contains coverage information. The
  script for running fuzzers (`run_tools.py`) saves hourly coverage results in
the output directory.

### Examples

There are 3 sets of examples (`example#.list` and `example#.conf`) each of which
takes about 1 hour to run.

To generate the benchmark and test the fuzzers using these examples, run the
following commands from the `scripts` directory:

```
$ python3 ./generate_benchmark.py ../examples/example#.list ../examples/example#_benchmark
$ python3 ./run_tools.py ../examples/example#.conf ../examples/example#_outputs
$ ./save_results.sh ../examples/example#_outputs ../examples/example#_outputs/example#_results <PARAM> 0 paper > ../examples/example#_outputs/example#_summary
$ cat ../examples/example#_outputs/example#_summary
```

Note that you should replace # with the example number. Also, you should use the
matching pair to run the experiment. For example, if you used `example1.list` to
generate the benchmark, you should use `example1.conf` to run the fuzzers.

Because each example varies different parameters, `<PARAM>` for
`save_results.sh` script is specific to each example.

- For example 1: `Algorithm`
- For example 2: `Size`
- For example 3: `Generator`

The fuzzing results for each experiment will be saved in the `example#_outputs`
directory.

### Tutorial

In this tutorial, we will generate a benchmark consisting of 5 programs and run
AFL on the generated benchmark for 5 minutes per program. We will then visualize
the coverage results from one of the fuzzing campaigns using Fuzzle.

1. Generate the benchmark with:
```
$ cd scripts
$ python3 ./generate_benchmark.py ../tutorial/programs.list ../tutorial/benchmark
```
Note that `programs.list` contains the configurations of 5 programs to be
generated.

2. Run AFL:
```
$ python3 ./run_tools.py ../tutorial/run.conf ../tutorial/outputs
```
The `run.conf` file specifies the path to the generated benchmark, the duration
of the fuzzing run (5 minutes), and the fuzzer to run (AFL). This step will take
approximately 1 hour.

3. Store and visualize results:
```
$ ./save_results.sh ../tutorial/outputs ../tutorial/results Algorithm 0 paper > ../tutorial/summary
$ cat ../tutorial/summary
$ PATH_TO_TXT=../tutorial/benchmark/txt/Wilsons_20x20_1_1.txt
$ PATH_TO_COV=../tutorial/outputs/cov_gcov_Wilsons_20x20_1_1_25percent_default_gen_afl_0/Wilsons_20x20_1_1_25percent_default_gen_afl_0.c.gcov
$ python3 ./visualize.py $PATH_TO_TXT $PATH_TO_COV ../tutorial/wilsons 20
```
The fuzzing results will be stored in `results.csv` and the summary of results
will be printed out to the screen. You can also check the visual aid generated
(`wilsons.png`) in the `tutorial` directory.

## Artifact

We publicize the artifacts to help reproduce the experiments in our paper. Please
check our [Fuzzle-Artifact](https://doi.org/10.5281/zenodo.7031393) repository.

## Citation

If you use Fuzzle in scientific work, consider citing our paper:

```bibtex
@INPROCEEDINGS{lee:ase:2022,
  author = {Haeun Lee and Soomin Kim and Sang Kil Cha},
  title = {{Fuzzle}: Making a Puzzle for Fuzzers},
  booktitle = {Proceedings of the International Conference on Automated Software Engineering},
  year = 2022
}
```
