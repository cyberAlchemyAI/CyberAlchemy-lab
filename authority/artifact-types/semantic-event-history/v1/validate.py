#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
TARGET=ROOT.parents[2]/'ontology-integration/candidates/0002-carrier-materialization/validate.py'
if __name__=='__main__':raise SystemExit(subprocess.run([sys.executable,str(TARGET),'--package',str(ROOT)]).returncode)
