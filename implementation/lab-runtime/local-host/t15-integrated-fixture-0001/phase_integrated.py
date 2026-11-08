"""Actual ABI-pinned constructor phase, with immutable per-phase receipts."""
import importlib.util
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))
spec=importlib.util.spec_from_file_location('_integrated_constructor',HERE/'construct_integrated.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
module.main()
