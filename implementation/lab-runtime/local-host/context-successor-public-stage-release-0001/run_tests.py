"""Execute pinned release/test source under an inert effect audit hook."""
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, '/usr/lib/python3/dist-packages')
pins = json.loads((HERE/'test-pins.json').read_bytes())
raw = {name:(HERE/name).read_bytes() for name in pins}
for name, expected in pins.items():
    if hashlib.sha256(raw[name]).hexdigest() != expected:
        raise RuntimeError('TEST_SOURCE_DRIFT')

def audit(event,args):
    if event == 'open' and args and isinstance(args[0],(str,bytes)) and \
       str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PRIVATE_ARCHIVE_BODY_DISABLED')
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('REAL_EFFECT_DISABLED')
sys.addaudithook(audit)

release = types.ModuleType('release')
release.__file__ = str(HERE/'release.py')
sys.modules['release'] = release
exec(compile(raw['release.py'], release.__file__, 'exec'), release.__dict__)
tests = types.ModuleType('checked_release_tests')
tests.__file__ = str(HERE/'test_release.py')
exec(compile(raw['test_release.py'], tests.__file__, 'exec'), tests.__dict__)
result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(tests))
for name, expected in pins.items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != expected:
        raise RuntimeError('POST_TEST_SOURCE_DRIFT')
print(json.dumps({'schema':'context-stage-release-static-tests/v1',
                  'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'effect':'NOT_RUN','protected_archive_body':'UNOPENED'},sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
