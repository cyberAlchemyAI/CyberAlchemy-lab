"""One explicit namespace for all original adapter/check types."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ADAPTER=HERE.parent/'current-source-adapter-v1'
NAME='_cal_current_source_adapter_for_checks_v2'
spec=importlib.util.spec_from_file_location(NAME,ADAPTER/'__init__.py',submodule_search_locations=[str(ADAPTER)])
module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
B=__import__(NAME+'.base',fromlist=['*'])
Parent=__import__(NAME+'.checks',fromlist=['*'])
