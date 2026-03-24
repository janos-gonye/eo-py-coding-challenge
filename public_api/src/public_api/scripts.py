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
