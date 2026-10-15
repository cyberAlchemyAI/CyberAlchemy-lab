"""Explicit selected current producer helpers; copied adapter types stay local."""
import importlib.util
import sys
from pathlib import Path
ADAPTER_ROOT=Path(__file__).resolve().parent
PRODUCER_ROOT=ADAPTER_ROOT.parent/'current-participation-v2'
NAME='_cal_current_source_adapter_producer_v2'
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
SOURCE_PIN='4f9336b9a8e540b938be7bc12353a4359222685da81ead64fc7b0f12e792290c'
PACKAGE_PIN='26cd785ee370eb99004d8e8b74d6c0f0d7a368eeb13a79027756d2906871c7a7'
