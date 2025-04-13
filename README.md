# Disclaimer

This is an academic prototype which is not intended for production use, as it did not receive proper code review.

# About

This repository contains tools for verifiable computations. It is mainly focused on researching STARKs, its components and constructions based on STARKs.

# Table of contents

<!-- mtoc start -->

- [Setup](#setup)
  - [Linux/macOS](#linuxmacos)
  - [Windows](#windows)
- [Usage](#usage)
  - [Example](#example)

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

```
$ vc --help
```

```
usage: vc [-h] [--ff FACTOR] [--ef FACTOR] [-f MODULUS] [--fd N] [--id N] [--sl LEVEL]
          [-s LEVEL]

FRI polynomial commitment scheme experimentation program

options:
  -h, --help            show this help message and exit
  --ff, --folding-factor-log FACTOR
                        folding factor. default: 3
  --ef, --expansion-factor-log FACTOR
                        expansion factor. default: 3
  -f, --field MODULUS   prime field size. default: 18446744069414584321
  --fd, --final-degree-log N
                        number of coefficients when to stop the protocol. default: 2
  --id, --initial-degree-log N
                        initial number of coefficients. default: 10
  --sl, --security-level-bits LEVEL
                        desired security level in bits. default: 5
  -s, --seed LEVEL      randomness seed. default: 64 bit integer chosen at random
```

## Example

```
$ vc --ff 3 --id 10 --fd 1 --sl 16 --ef 2
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
