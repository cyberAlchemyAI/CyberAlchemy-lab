"""Compatibility entry point for the repository-owned website build."""
from pathlib import Path
import subprocess
import sys


def build():
    website = Path(__file__).resolve().parents[2]
    subprocess.run([sys.executable, str(website / 'build.py')], cwd=website.parent, check=True)


if __name__ == '__main__':
    build()
