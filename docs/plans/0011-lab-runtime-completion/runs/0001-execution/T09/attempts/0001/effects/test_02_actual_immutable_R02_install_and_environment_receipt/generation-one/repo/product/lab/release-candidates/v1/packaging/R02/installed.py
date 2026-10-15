"""-I -S launcher: selected wheels only, no global site packages or Session state."""
import importlib.metadata, runpy, sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];INSTALL=ROOT.parent
sys.path[:0]=[str(HERE),str(INSTALL/'deps'),str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation')]
from common import environment_guard,load,need,VERSIONS
selection=load(INSTALL/'selection.json');environment_guard(selection['environment'])
need({n:importlib.metadata.version(n) for n in VERSIONS}==VERSIONS,'dependency versions changed')
allowed={'scenario.py':HERE/'scenario.py','test_transition.py':ROOT/'implementation/lab-runtime/candidates/repeatable-operation/tests/test_transition.py'}
need(len(sys.argv)>=2 and sys.argv[1] in allowed,'unselected installed entrypoint')
script=allowed[sys.argv[1]]
if sys.argv[1]=='test_transition.py':
 source=Path(sys.argv[2]);script=source/'implementation/lab-runtime/candidates/repeatable-operation/tests/test_transition.py'
 from common import read,sha
 need(sha(read(script))==sha(read(allowed['test_transition.py'])),'unselected transition regression bytes');sys.argv=[str(script),*sys.argv[3:]]
else:sys.argv=[str(script),*sys.argv[2:]]
runpy.run_path(str(script),run_name='__main__')
