# Sinolify
*Sinolify* is a utility for converting from Sowa format of task 
packages (detailed format specification available 
[here](https://www.youtube.com/watch?v=dQw4w9WgXcQ))
to Sinol task packages (format specification [here](https://sio2project.mimuw.edu.pl/display/DOC/Preparing+Task+Packages)).

## Installation
This utility requires Python 3.8 or higher.
To install, run `pip install .` from the main
directory. You might want to setup a 
[venv](https://docs.python.org/3/tutorial/venv.html)
first.

## Usage
```text
sinolify-convert [-h] [-v {error,warning,info,debug}] [-f] [-t] [-j J] source output
```

Positional arguments:
- `source`               - Sowa .zip package path 
- `output`               - Output .zip file path

Optional arguments:
- `-h`, `--help`            - Show help message and exit
- `-v {error,warning,info,debug}` - Verbosity level, default is `warning`
- `-f`                  - Allow overwrite of output file 
- `-t`                  - Auto adjust time limits (see below for more details)
- `-j NUMBER`                - Number of threads for adjusting time limits

## Automatic time limits adjustments
Sinolify uses the following algorithm for estimating time limits:
- The model solution is run on all input files. 
  Execution time is measured the same way as on SIO2: number of instructions
  is multiplied by 2GHz.
- Maximum result of measures is multiplied by 3 and rounded up to 0.5s.
- Such limit is set for all tests in `config.yml`.