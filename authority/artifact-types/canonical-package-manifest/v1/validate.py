#!/usr/bin/env python3
from pathlib import Path
import sys
LAB=Path(__file__).resolve().parent.parents[3]; sys.path.insert(0,str(LAB/"tooling/validators")); import artifact_surface
if __name__=="__main__": raise SystemExit(artifact_surface.validate_package(Path(__file__).resolve().parent))
