"""Select the exact composition whose bytes the host manifest guards."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PATH = HERE.parent / 'classification-preparation-v7'
NAME = '_cal_' + HERE.name.replace('-', '_') + '_classification_preparation_v7'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, PATH / '__init__.py', submodule_search_locations=[str(PATH)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = package
    spec.loader.exec_module(package)
selected = __import__(NAME + '.preparation', fromlist=['ClassificationPreparation'])
assert Path(selected.__file__).resolve() == PATH / 'preparation.py'
ClassificationPreparation = selected.ClassificationPreparation
RuleFailure = selected.RuleFailure
