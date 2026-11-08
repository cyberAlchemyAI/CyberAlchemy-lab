"""Run one staged T16 family construction phase in the selected 4.23 ABI."""
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import sys

INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'),
        importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected T16 4.23 ABI differs')

TASK = Path(__file__).resolve().parent
INSTANCE = 'legacy-local-e084574c6d149cf0'
if len(sys.argv) != 2 or sys.argv[1] not in ('source', 'cold', 'reader', 'mapped', 'context'):
    raise ValueError('one selected phase required')
phase = sys.argv[1]
spec = importlib.util.spec_from_file_location('t16_successor_423', TASK / 'native_successor_423.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.phase(INSTANCE, phase)
print(json.dumps({'phase': phase, 'result': result.get('result', 'PASS'),
                  'environment': {'python': platform.python_version(),
                                  'jsonschema': importlib.metadata.version('jsonschema'),
                                  'cryptography': importlib.metadata.version('cryptography')}},
                 sort_keys=True))
