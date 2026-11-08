"""Run pinned inert issuer-model tests; refuse private/effect operations."""
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
        raise RuntimeError('TEST_SOURCE_DRIFT')

def audit(event,args):
    if event == 'open' and args and isinstance(args[0],(str,bytes)) and \
       str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('REAL_EFFECT_DISABLED')
sys.addaudithook(audit)

adapter = types.ModuleType('adapter')
adapter.__file__ = str(HERE/'adapter.py')
sys.modules['adapter'] = adapter
exec(compile(raw['adapter.py'],adapter.__file__,'exec'),adapter.__dict__)
tests = types.ModuleType('checked_issuer_tests')
tests.__file__ = str(HERE/'test_adapter.py')
exec(compile(raw['test_adapter.py'],tests.__file__,'exec'),tests.__dict__)
result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(tests))
for name,digest in pins.items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest:
        raise RuntimeError('POST_TEST_SOURCE_DRIFT')
print(json.dumps({'schema':'context-local-issuer-adapter-static-tests/v1',
                  'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'effect':'NOT_RUN','protected_archive_body':'UNOPENED'},sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
