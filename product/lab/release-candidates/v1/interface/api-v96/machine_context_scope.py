"""Select the private original-owner Machine Context scope composition."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/"machine-context-scope-v1"
NAME="_cal_"+HERE.name.replace("-","_")+"_machine_context_scope_v1"
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
selected=__import__(NAME+".generation",fromlist=["generate"])
assert Path(selected.__file__).resolve()==PATH/"generation.py"
generate=selected.generate
