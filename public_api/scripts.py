"""
CLI scripts for managing the project.
"""

import subprocess
import sys


def lint() -> None:
    """Run pylint on the project source and tests."""
    print("Running pylint on src and tests...")
    try:
        subprocess.check_call(["pylint", "src", "tests"])
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def format_code() -> None:
    """Run black formatter on the project source and tests."""
    print("Running black on src and tests...")
    try:
        subprocess.check_call(["black", "src", "tests"])
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "lint":
            lint()
        elif command == "format":
            format_code()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("Please provide a command: lint or format")
        sys.exit(1)
