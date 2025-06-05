# Disclaimer

This is an academic prototype which is not intended for production use, as it did not receive proper code review.

# About

This repository contains tools for verifiable computations. It is mainly focused on researching STARKs, its components and constructions based on STARKs. Now FRI and STARK are implemented. A lot of improvements are planned, such as

- [x] Basic arbitrary-degree FRI
- [x] Basic STARK
- [x] Basic AIRs for Fibonacci numbers and factorial
- [ ] Batch FRI
- [ ] Zero-knowledge in STARK
- [ ] Batch proof for transition constraints in STARK
- [ ] AET definition DSL for convenient custom AIR definition

And many more.

# Table of contents

<!-- mtoc start -->

- [Setup](#setup)
    - [Linux/macOS](#linuxmacos)
    - [Windows](#windows)
- [Usage](#usage)
    - [FRI](#fri)
        - [Example](#example)
    - [STARK](#stark)
        - [Example](#example-1)

<!-- mtoc end -->

# Setup

## Linux/macOS

1. Create a virtual environment. In the cloned project directory run

   ```bash
   python3 -m venv .venv
   ```

2. Activate virtual environment:

   ```bash
   source ./.venv/bin/activate
   ```

3. Install dependencies in virtual environment:

   ```bash
   pip3 install -e '.[test]'
   ```

## Windows

It is assumed below that you have installed python from the [official website](https://www.python.org/). Execute the commands below using **PowerShell**.

1. Create a virtual environment. In the cloned project directory run

   ```PowerShell
   python -m venv .venv
   ```

2. Activate virtual environment:

   ```PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

   If you are unable to run this script, please refer to the [`Set-ExecutionPolicy` cmdlet manual](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5).

3. Install dependencies in virtual environment:

   ```bash
   pip install -e '.[test]'
   ```

# Usage

The program is divided into subprograms each for experimenting with different primitives.

```bash
vc --help
```

```
usage: vc [-h] {fri,stark} ...

verifiable computations (VC) experimentation program

options:
  -h, --help   show this help message and exit

subprograms:
  choose one of the subprograms for running and experimenting with
  corresponding protocols or primitives

  {fri,stark}
    fri        run FRI with specified parameters
    stark      run STARK for one of preprogrammed tasks
```

## FRI

```bash
vc fri --help
```

```
usage: vc fri [-h] [--ff NUMBER] [--ef NUMBER] [-f NUMBER] [--fd NUMBER]
              [--id NUMBER] [--sl NUMBER] [-s NUMBER]

subprogram for running FRI IOPP with specified parameters

options:
  -h, --help            show this help message and exit
  --ff, --folding-factor-log NUMBER
                        folding factor. default: 3
  --ef, --expansion-factor-log NUMBER
                        expansion factor. default: 3
  -f, --field NUMBER    prime field size. default: 18446744069414584321
  --fd, --final-degree-log NUMBER
                        number of coefficients when to stop the protocol.
                        default: 2
  --id, --initial-degree-log NUMBER
                        initial number of coefficients. default: 10
  --sl, --security-level-bits NUMBER
                        desired security level in bits. default: 5
  -s, --seed NUMBER     randomness seed. default: 64 bit integer chosen at
                        random
```

### Example

```bash
vc fri --ff 3 --id 10 --fd 1 --sl 16 --ef 2
```

```
seed: 1434708073160630454
fri parameters:
    expansion factor = 4 (2^2)
    folding factor = 8 (2^3)
    initial coefficients length = 1024 (2^1)
    final coefficients length = 2 (2^1)
    initial evaluation domain length = 4096 (2^12)

    security level = 16 bits
    number of rounds = 2
    number of query indices = 8

prover time: 10.14 s
proof:
    final polynomial: 15241627350980849523x + 9569292054215004480
    proof size: 8 KB

verifier time: 21 ms
verification result: True
```

## STARK

```bash
vc stark --help
```

```
usage: vc stark [-h] [-l] [-a {fibonacci,factorial,count}] [--ff NUMBER]
                [--ef NUMBER] [--fd NUMBER] [--sl NUMBER] [-s NUMBER]
                [air_arguments ...]

subprogram for running STARK with specified parameters for proving the results
of a specified task

positional arguments:
  air_arguments         arguments to pass to AIR generation, like "n" in
                        fibonacci(n)

options:
  -h, --help            show this help message and exit
  -l, --list            list available AIRs for experimanting with
  -a, --air {fibonacci,factorial,count}
                        chose the function STARK should prove the result for.
                        default: fibonacci
  --ff, --folding-factor-log NUMBER
                        folding factor. default: 3
  --ef, --expansion-factor-log NUMBER
                        expansion factor. default: 3
  --fd, --final-degree-log NUMBER
                        number of coefficients when to stop the protocol.
                        default: 2
  --sl, --security-level-bits NUMBER
                        desired security level in bits. default: 5
  -s, --seed NUMBER     randomness seed. default: 64 bit integer chosen at
                        random
```

### Example

```bash
vc stark --air fibonacci --ff 2 --sl 64 90
```

```
proving that 90-th fibonacci number is 2880067194370816120
AET shape: (90, 2)
number of boundary constraints: 2
number of transition constraints: 2

fri parameters: 
    expansion factor = 8 (2^3)
    folding factor = 4 (2^2)
    initial coefficients length = 1024 (2^2)
    final coefficients length = 4 (2^2)
    initial evaluation domain length = 8192 (2^13)

    security level = 64 bits
    number of rounds = 3
    number of query indices = 22

prover time: 10.25 s
proof size: 78 KB
verifier time: 306 ms
verification result: True
```
