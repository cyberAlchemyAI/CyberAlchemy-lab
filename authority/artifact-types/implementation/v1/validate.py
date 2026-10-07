#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parents[3]/'tooling/validators/endpoint_carrier.py'
spec=importlib.util.spec_from_file_location('endpoint_carrier_validator',SHARED); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
if __name__=='__main__': raise SystemExit(mod.validate_package(ROOT))
