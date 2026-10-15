"""Select the exact lesson application implementation in this host closure."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/"lesson-application-v4-completion-0001"
NAME="_cal_"+HERE.name.replace("-","_")+"_current_lesson_application_v1"
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
selected=__import__(NAME+".preparation",fromlist=["LessonApplication"])
assert Path(selected.__file__).resolve()==PATH/"preparation.py"
LessonApplication=selected.LessonApplication
LessonApplicationFailure=selected.RuleFailure
