#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parent;T=R.parents[2]/'relation-kinds/candidates/0006-definition-complete-instances/validate.py'
raise SystemExit(subprocess.run([sys.executable,str(T),'--package',str(R)]).returncode)
