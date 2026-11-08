"""Select the private original-owner Machine Context scope composition."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/"machine-context-scope-v3-api25-completion-0001"
NAME="_cal_"+HERE.name.replace("-","_")+"_machine_context_scope_v3_api25_completion_0001"
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
selected=__import__(NAME+".generation",fromlist=["generate"])
if Path(selected.__file__).resolve()!=PATH/"generation.py":
    raise ValueError("unselected v3 Machine helper")
_v3_generate=selected.generate
LEGACY_PATH=HERE.parent/"machine-context-scope-v4-api33-legacy-0001"
LEGACY_NAME="_cal_api33_exact_legacy_machine_scope_0001"
CURRENT_LEGACY_PATH=HERE.parent/"machine-context-scope-v5-api33-current-legacy-0001"
CURRENT_LEGACY_NAME="_cal_api33_exact_current_legacy_machine_scope_0001"

def generate(custodian,message,request_raw,mapped_pin,schemas):
    origin=Path(sys.modules[type(custodian).__module__].__file__).name
    if origin not in ('legacy_context_sessions.py','current_legacy_context_sessions.py'):
        return _v3_generate(custodian,message,request_raw,mapped_pin,schemas)
    path,name=(LEGACY_PATH,LEGACY_NAME) if origin=='legacy_context_sessions.py' else (CURRENT_LEGACY_PATH,CURRENT_LEGACY_NAME)
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/"__init__.py",
            submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    exact=__import__(name+".generation",fromlist=["generate"])
    if Path(exact.__file__).resolve()!=path/"generation.py":
        raise ValueError("unselected exact Machine helper")
    return exact.generate(custodian,message,request_raw,mapped_pin,schemas)
