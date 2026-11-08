"""Execute checked synthetic tests with private/effect audit refusals."""
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
pins = json.loads((HERE/'test-pins.json').read_bytes())
raw = {name:(HERE/name).read_bytes() for name in pins}
for name,digest in pins.items():
    if hashlib.sha256(raw[name]).hexdigest() != digest:
        raise RuntimeError('TEST_SOURCE_DRIFT_'+name)

def audit(event,args):
    if event == 'open' and args and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.','socket.')) or event in (
            'os.system','os.fork','os.exec'):
        raise RuntimeError('REAL_EFFECT_DISABLED')
sys.addaudithook(audit)

module = types.ModuleType('controller')
module.__file__ = str(HERE/'controller.py')
sys.modules['controller'] = module
exec(compile(raw['controller.py'],module.__file__,'exec'),module.__dict__)
tests = types.ModuleType('checked_controller_tests')
tests.__file__ = str(HERE/'test_controller.py')
exec(compile(raw['test_controller.py'],tests.__file__,'exec'),tests.__dict__)
result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(tests))
for name,digest in pins.items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
        raise RuntimeError('POST_TEST_SOURCE_DRIFT_'+name)
print(json.dumps({'schema':'context-signed-scope-controller-static-tests/v1',
                  'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'actual_signed_scope':'NOT_OPENED',
                  'real_effect':'NOT_RUN','private_archive_body':'UNOPENED'},
                 sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
