import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v23'
SOURCE = 'd953323621c8fc4f3737cbcdef9b87c5aebfbc604565426f257f1461a2056d5b'
PROFILE = '6a15699643442bc4ce9418811e0dcaedd78a6ebc50b3a53f104ea007e74ecdbf'
NAME = '_cal_file_export_api23'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
def load(name):
    return __import__(NAME + '.' + name, fromlist=['*'])
P, M, H, G, W = [load(n) for n in ('protocol', 'artifact_model', 'handlers', 'guard', 'workspace')]
def guard():
    G.verify(SOURCE)
    return P.Schemas(PROFILE)
