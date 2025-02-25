# Disclaimer

This is an academic prototype which is not intended for production use, as it did not receive proper code review.

# About

This repository contains tool for verifiable computations. It is mainly focused on researching STARKs, its components and constructions based on STARKs.

# Table of contents

- [Disclaimer](#disclaimer)
- [About](#about)
- [Table of contents](#table-of-contents)
- [Setup](#setup)
  - [Linux/macOS](#linuxmacos)
  - [Windows](#windows)
- [Usage](#usage)
  - [Example](#example)

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

FRI polynomial commitment scheme experimentation program

options:
  -h, --help            show this help message and exit
  --ff FACTOR, --folding-factor-log FACTOR
                        folding factor. default: 3
  --ef FACTOR, --expansion-factor-log FACTOR
                        expansion factor. default: 3
  -f MODULUS, --field MODULUS
                        prime field size. default: 18446744069414584321 (goldilocks field)
  --fd N, --final-degree-log N
                        number of coefficients when to stop the protocol. default: 2      
  --id N, --initial-degree-log N
                        initial number of coefficients. default: 10
  --sl LEVEL, --security-level-bits LEVEL
                        desired security level in bits. default: 5
```

## Example

```
$ vc --ff 3 --id 10 --fd 1 --sl 16 --ef 2
```
```
INFO:vc.fri:main():fri parameters:
    expansion factor = 4 (2^2)
    folding factor = 8 (2^3)
    initial coefficients length = 1024 (2^1)
    final coefficients length = 2 (2^1)
    initial evaluation domain length = 4096 (2^12)

    security level = 16 bits
    number of rounds = 2
    number of query indices = 8

INFO:vc.fri:main():prover time: 13.39 s
INFO:vc.fri:main():proof:
    final polynomial: 7316626253158583747x + 4533784301111763252
    proof size: 8 KB

INFO:vc.fri:main():verifier time: 42 ms
INFO:vc.fri:main():verification result: True
```
