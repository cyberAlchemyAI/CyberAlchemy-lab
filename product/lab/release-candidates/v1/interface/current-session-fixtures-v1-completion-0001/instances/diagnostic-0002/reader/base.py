"""Explicit selected current producer helpers; copied adapter types stay local."""
import importlib.util
import sys
from pathlib import Path
ADAPTER_ROOT=Path(__file__).resolve().parent
PRODUCER_ROOT=ADAPTER_ROOT.parent/'source'
NAME='_cal_completion_diagnostic_0002_producer_module_0208_v4'
spec=importlib.util.spec_from_file_location(NAME,PRODUCER_ROOT/'__init__.py',submodule_search_locations=[str(PRODUCER_ROOT)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
B=__import__(NAME+'.base',fromlist=['*'])
C=__import__(NAME+'.cold',fromlist=['*'])
records=__import__(NAME+'.records',fromlist=['*'])
ROOT=B.ROOT
HERE=PRODUCER_ROOT
sha=B.sha;encoded=B.encoded;parse=B.parse;load=B.load;require=B.require
binding=B.binding;original=B.original;verify_source=B.verify_source
original_bridge=B.original_bridge;cut=B.cut
