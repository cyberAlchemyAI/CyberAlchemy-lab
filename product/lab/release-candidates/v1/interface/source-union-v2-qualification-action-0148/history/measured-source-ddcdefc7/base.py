"""Original frozen reader helpers in a distinct, explicitly selected family."""
import importlib.util,sys
from pathlib import Path
ADAPTER_ROOT=Path(__file__).resolve().parent
PARENT_ROOT=ADAPTER_ROOT.parent/'current-source-adapter-v4'
NAME='_cal_source_union_original_adapter_action_0148'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PARENT_ROOT/'__init__.py',submodule_search_locations=[str(PARENT_ROOT)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
parent=__import__(NAME+'.reader',fromlist=['SelectedReader'])
B=parent.adapter.source.B;C=parent.adapter.source.C;records=parent.records
PRODUCER_ROOT=B.HERE;HERE=B.HERE;ROOT=B.ROOT
sha=B.sha;encoded=B.encoded;parse=B.parse;load=B.load;require=B.require;binding=B.binding;original=B.original;verify_source=B.verify_source;original_bridge=B.original_bridge;cut=B.cut
