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
INFO:vc.fri:main():fri_parameters = 
    expansion_factor = 8
    folding_factor = 8
    initial_coefficients_length = 1024
    final_coefficients_length = 4
    initial_evaluation_domain_length = 8192

    security_level = 32
    number_of_rounds = 2
    number_of_repetitions = 11
        
INFO:vc.fri:main():prover time: 17.75 s
INFO:vc.fri:main():proof = 
    final polynomial: 4618547800941124052x + 1164068294085142249
    proof size: 11 KB

INFO:vc.fri:main():prover time: 29 ms
INFO:vc.fri:main():verification_result = True
```
