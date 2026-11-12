"""Verify the selected shared workflow without replacing its execution selection."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3]
subprocess.run(['node',str(ROOT/'implementation/lab-runtime/lab.mjs'),'shared','activate'],check=True)
subprocess.run(['python3','-B',str(Path(__file__).with_name('validate.py'))],check=True)
