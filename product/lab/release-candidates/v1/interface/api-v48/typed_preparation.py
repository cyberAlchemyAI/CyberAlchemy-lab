"""Select the frozen typed host composition from the full host closure."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'typed-host-composition-v3'
NAME='_cal_'+HERE.name.replace('-','_')+'_typed_preparation_v3'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
selected=__import__(NAME+'.preparation',fromlist=['TypedPreparation'])
assert Path(selected.__file__).resolve()==PATH/'preparation.py'
TypedPreparation=selected.TypedPreparation
