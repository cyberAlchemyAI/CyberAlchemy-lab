#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[5]
if __name__=="__main__": raise SystemExit(subprocess.run([sys.executable,str(LAB/"tooling/validators/artifact_surface_candidate_2.py"),"validate-package",str(ROOT)]).returncode)
