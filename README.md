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
