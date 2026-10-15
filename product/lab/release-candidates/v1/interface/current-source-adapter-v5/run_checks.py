"""Pin the complete source closure before importing/effecting an owned replay."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);args=p.parse_args()
    raw=(HERE/'source-manifest.json').read_bytes()
    if sha(raw)!=args.source_sha256:raise ValueError('independent adapter source preflight differs')
    manifest=json.loads(raw)
    for row in manifest['files']:
        if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('source bytes changed '+row['path'])
    name='_cal_current_source_adapter_checks_v3_runtime'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    checks=__import__(name+'.checks',fromlist=['*'])
    checks.Checks.adapter_pin=args.source_sha256
    checks.SOURCE_PIN=manifest['producer_source_binding']['sha256'];checks.PACKAGE_PIN=manifest['producer_package_binding']['sha256']
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(checks.Checks))
    reader=__import__(name+'.reader',fromlist=['*']).SelectedReader(args.source_sha256,checks.SOURCE_PIN,checks.PACKAGE_PIN)
    reader.guard()
    observation={'schema_version':'lab-current-source-adapter-checks/v2-candidate','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'result':'PASS' if result.wasSuccessful() else 'FAIL','current_Agent_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
    with (HERE/'checks-result-0001.json').open('x') as stream:json.dump(observation,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps(observation),flush=True)
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
