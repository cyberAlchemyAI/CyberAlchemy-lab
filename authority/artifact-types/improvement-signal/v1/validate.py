#!/usr/bin/env python3
from pathlib import Path
import importlib.util
R=Path(__file__).resolve().parent;S=R.parents[3]/'tooling/validators/definition_complete_carrier.py'
s=importlib.util.spec_from_file_location('v',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
raise SystemExit(m.validate_package(R))
