#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent;SHARED=ROOT.parents[3]/'tooling/validators/artifact_type_successor.py'
s=importlib.util.spec_from_file_location('v',SHARED);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m)
if __name__=='__main__':raise SystemExit(m.validate_package(ROOT))
