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
usage: vc [-h] [--folding-factor-log [FACTOR]] [--expansion-factor-log [FACTOR]]
          [--field [MODULUS]] [--final-degree-log [N]] [--initial-degree-log [N]]
          [--security-level-log [LEVEL]]

FRI polynomial commitment scheme experimentation program

options:
  -h, --help            show this help message and exit
  --folding-factor-log [FACTOR]
                        folding factor
  --expansion-factor-log [FACTOR]
                        expansion factor
  --field [MODULUS]     prime field size
  --final-degree-log [N]
                        number of coefficients when to stop the protocol
  --initial-degree-log [N]
                        initial number of coefficients
  --security-level-log [LEVEL]
                        desired security level
```

## Example

```
$ vc
```

```
INFO:vc.fri:main():fri parameters:
    expansion factor = 8
    folding factor = 8
    initial coefficients length = 1024
    final coefficients length = 4
    initial evaluation domain length = 8192

    security level = 32
    number of rounds = 2
    number of repetitions = 11
        
INFO:vc.fri:main():prover time: 17.97 s
INFO:vc.fri:main():proof:
    final polynomial: 10779303811544763966x + 13148289302788285659
    proof size: 12 KB

INFO:vc.fri:main():verifier time: 32 ms
INFO:vc.fri:main():verification result: True
```
