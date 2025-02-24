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
$ vc --ff 4 --id 11 --fd 3 --sl 10 --ef 4
```
```
INFO:vc.fri:main():fri parameters:
    expansion factor = 16 (2^4)
    folding factor = 16 (2^4)
    initial coefficients length = 2048 (2^3)       
    final coefficients length = 8 (2^3)
    initial evaluation domain length = 32768 (2^15)

    security level = 10 bits
    number of rounds = 1
    number of query indices = 3

INFO:vc.fri:main():prover time: 209.66 s
INFO:vc.fri:main():proof:
    final polynomial: 7665344656090724315x^7 + 15001491804211313564x^6 + 5337035066452422933x^5 + 3942137744011559509x^4 + 12699361532114498063x^3 + 9761565799121261157x^2 + 16551901012716457488x + 7084323875983630801
    proof size: 4 KB

INFO:vc.fri:main():verifier time: 50 ms
INFO:vc.fri:main():verification result: True
```
