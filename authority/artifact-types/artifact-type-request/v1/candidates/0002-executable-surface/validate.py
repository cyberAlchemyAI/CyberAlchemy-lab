#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[5]
cmd=[sys.executable,str(LAB/"tooling/validators/artifact_surface_candidate_2.py"),"validate-package",str(ROOT),"--registry",str(LAB/"authority/artifact-types/candidates/0001-artifact-surface-foundation/registry.json")]
raise SystemExit(subprocess.run(cmd).returncode)
