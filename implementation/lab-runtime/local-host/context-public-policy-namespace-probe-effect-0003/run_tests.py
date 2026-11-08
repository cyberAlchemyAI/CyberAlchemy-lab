"""Effect-denying audit suite: only read-only Docker queries may spawn."""
from pathlib import Path
import json
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
def audit(event,args):
    if event=='open' and args and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PROTECTED_BODY_DISABLED')
    if event=='subprocess.Popen':
        argv=list(args[1]) if args[1] is not None else []
        if argv[:3]==['/usr/bin/docker','image','inspect'] or \
           argv[:2]==['/usr/bin/docker','ps']:
            return
        raise RuntimeError('EFFECT_DISABLED_TEST_SUBPROCESS')
    if event.startswith('socket.') or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('EFFECT_DISABLED_TEST')
sys.addaudithook(audit)
import test_wrapper
result=unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromModule(test_wrapper))
print(json.dumps({'schema':'context-public-policy-probe-effect-one-shot-tests/v1',
                  'tests':result.testsRun,'passed':result.wasSuccessful(),
                  'docker_effect':'UNRUN','private_inputs':'UNOPENED'},sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
