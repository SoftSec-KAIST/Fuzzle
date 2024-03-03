# smake & scmake

A program analysis preparation tool for C programs made with GNU Make and cmake

## smake

`smake` observes the build process driven by `make`, and derives the standalone, preprocessed form of the source code that makes up each C program linked during the process. `smake` creates a directory `sparrow/`, where you can perform program analyses.

You can instantly start your program analysis in two steps:

 1. Initialize `sparrow`
 2. Use `smake` instead of `make` to build your programs.

### Usage

```plaintext
smake r1045
  a program analysis preparation tool for C programs made with GNU Make

smake observes the build process driven by make(1), and derives the
standalone, preprocessed form of the source code that makes up each
C program linked during the process.  smake creates a directory
"sparrow/", where you can perform program analyses with make(1).

You can instantly start your program analysis in three steps:
 1. Initialize "sparrow/", i.e. $AMAKEDIR.
 2. Use `smake` instead of `make` to build your programs.
 3. Use `make` under $AMAKEDIR to analyze your programs.

Usage:
 $ smake --init [<options>]
  initializes sparrow/ to handle the regular use of smake.
  If you use a special compiler (e.g. cross compiler), its type must be
  specified by appending gcc style options, e.g. `-b mips-linux -V 2.95`.

 $ smake --clean
  completely removes sparrow/.

 $ smake <parameters for make>
  runs `make [<with parameters>]` and bookkeeps $AMAKEDIR.

 $ smake ./configure
  runs `./configure` under the same environment `smake` runs.

 $ smake --help
  shows this message.
```

## scmake

`scmake` executes `cmake` and preprocesses every C source-code recorded in "compile_commands.json".
`scmake` creates a directory `sparrow/`, where you can perform program analysis.

### Usage

```plaintext
usage: scmake [-h] [--cmake] [--cmake-out CMAKE_OUT] [--out [OUT]]

optional arguments:
  -h, --help            show this help message and exit
  --cmake               execute cmake and save result into CMAKE_OUT
  --cmake-out CMAKE_OUT
                        cmake output directory (default: build)
  --out [OUT]           scmake output directory (default: sparrow)
```
