"""Select the explicit lesson host composition without changing frozen packages."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'lesson-host-composition-v36'
NAME='_cal_'+HERE.name.replace('-','_')+'_lesson_host_v3'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
selected=__import__(NAME+'.host',fromlist=['LessonHost'])
assert Path(selected.__file__).resolve()==PATH/'host.py'
LessonHost=selected.LessonHost
