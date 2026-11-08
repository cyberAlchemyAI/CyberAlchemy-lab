"""Run frozen candidate fixtures with no real effects or private archive reads."""
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

writer = types.ModuleType('stage_writer')
writer.__file__ = str(HERE/'stage_writer.py')
sys.modules['stage_writer'] = writer
exec(compile(raw['stage_writer.py'], writer.__file__, 'exec'), writer.__dict__)
tests = types.ModuleType('checked_stage_writer_tests')
tests.__file__ = str(HERE/'test_stage_writer.py')
exec(compile(raw['test_stage_writer.py'], tests.__file__, 'exec'), tests.__dict__)
result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(tests))
for name, expected in pins.items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != expected:
        raise RuntimeError('POST_TEST_SOURCE_DRIFT')
print(json.dumps({'schema':'context-stage-writer-static-tests/v1',
                  'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'effect':'NOT_RUN','protected_archive_body':'UNOPENED'},sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
