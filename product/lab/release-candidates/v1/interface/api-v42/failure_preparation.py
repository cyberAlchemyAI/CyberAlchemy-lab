"""Select the exact failure adapter guarded by the host source manifest."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'failure-preparation-v3'
NAME='_cal_'+HERE.name.replace('-','_')+'_failure_preparation_v3'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
selected=__import__(NAME+'.preparation',fromlist=['FailurePreparation'])
assert Path(selected.__file__).resolve()==PATH/'preparation.py'
FailurePreparation=selected.FailurePreparation
FailureRuleFailure=selected.RuleFailure
