# Fuzzle

Fuzzle is a bug synthesizer that generates buggy benchmarks for evaluating
fuzzers. Fuzzle uses randomly created mazes and path constraints from previous
CVEs to generate subject programs. The details of Fuzzle can be found in our
paper "Fuzzle: Making a Puzzle for Fuzzers" (ASE 2022).

## Installation

To build Fuzzle and setup the docker and python environment, run the following:

```
$ git clone https://github.com/SoftSec-KAIST/Fuzzle
$ cd Fuzzle

# Build docker images
$ ./scripts/build_all_dockers.sh

# Install the dependencies
$ python3 -m pip install -r ../maze-gen/requirements.txt
```
Note that you need python 3.7+ to generate benchmark programs using Fuzzle.

## Usage

### Generating a benchmark

You can generate a buggy benchmark using `generate.sh` in scripts directory. For
example, the following command generates a default program based on a 10x10 maze
created with Wilson's algorithm.

```
$ ./scripts/generate.sh -a Wilsons -w 10 -h 10 -g default_gen -o <OUT_PATH>
```

A new program can be generated using the same maze but with realistic
constraints obtained from previous CVEs (e.g., CVE-2016-4487).

```
$ ./scripts/generate.sh -a Wilsons -w 10 -h 10 -g CVE_gen -s ./CVEs/CVE-2016-4487.smt2 -o <OUT_PATH>
```

You can optionally specify the pseudorandom seed, maze exit, percentage of
cycles with -r, -e, and -c, respectively.

To generate multiple programs for building a large benchmark, you can use
`generate_benchmark.py` as follows:

```
$ cd scripts
$ python3 generate_benchmark.py <FILE_PATH> <OUT_PATH>
```
You need to provide a path to the file that specifies the configuration of
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
$ python ./scripts/run_tools.py <CONFIG_FILE> <FUZZ_OUT>
```

The configuration file (`<CONFIG_FILE>`) should include path to subject
programs, fuzz duration, and fuzzers to run. An example configuration file is
provided under `confs` directory (`template.conf`).

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
algorithms will be displayed on screen.

- `<PARAM>`: one of four parameters of Fuzzle: Algorithm, Size, Cycle, Generator
- `<DURATION>`: length of fuzzing campaign in hours
- `<MODE>`: 'paper' for displaying tables similar to the ones shown in the
  paper, 'fuzzer' for displaying summarized results for each fuzzer.

### Visualizing coverage results

You can also visualize the code coverage results in the form of 2D maze, where
each cell represents a function in the program. The script for visualization
takes maze array (.txt), coverage results (.gcov), and maze size as input and
returns a png file.

```
$ python3 ./scripts/visualize.py <TXT_PATH> <COV_PATH> <OUT_PATH> <SIZE>
```
- `<TXT_PATH>`: path to .txt file for the chosen maze. Note that such files are
  automatically created under `txt` directory when generating a benchmark.
- `<COV_PATH>`: path to .gcov file that contains coverage information. The
  script for running fuzzers (`run_tools.py`) saves hourly coverage results in
the output directory.

## Artifact

We publicize the artifacts to help reproduce the experiments in our paper. Please
check our [Fuzzle-Artifact](https://github.com/SoftSec-KAIST/Fuzzle-artifact)
repository.

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
