"""Isolated cold host-origin causal test; no actual custody admission."""
import argparse,json,unittest
from pathlib import Path
import test_endpoint as selected
p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);selected.TEMP=p.parse_args().temp_root
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([selected.EndpointTests('test_cleanup_after_positive_expiry_cannot_sign')]))
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if result.wasSuccessful()else'FAIL',
                  'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
raise SystemExit(0 if result.wasSuccessful()else 1)
