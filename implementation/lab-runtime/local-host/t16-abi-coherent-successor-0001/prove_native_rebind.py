"""Prove a durable, byte-identical native locator for a future source recut.

This does not mutate the original mapped/context/API selections and is not a
substitute for renewing an expired Source5 participation period.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OLD=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')
NEW=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
INSTALL=NEW.parent.parent/'installation.json'
OLD_BUILD=ROOT/'product/lab/release-candidates/v1/interface/current-mapped-context-v4/build.py'
EXECUTION=ROOT/'product/lab/release-candidates/v1/interface/current-context-delivery-v2-action-0148/EXECUTION-DEPENDENCIES.json'
PERIOD=ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'

def main():
    if OLD.exists() or not NEW.is_file() or NEW.is_symlink() or sha(NEW)!=EXPECTED:
        raise ValueError('original absence or selected durable native bytes differ')
    original=OLD_BUILD.read_text()
    if "EXE=Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')" not in original or "EXE_SHA='"+EXPECTED+"'" not in original:
        raise ValueError('original mapper executable selection differs')
    selected=json.loads(EXECUTION.read_bytes())
    row={'path':str(OLD),'sha256':EXPECTED}
    if row not in selected['external_dependency_bindings']:
        raise ValueError('original Context external selection differs')
    installation=json.loads(INSTALL.read_bytes())
    # The already selected installation owns the exact native binary. Its
    # original receipt is retained; this proof adds no generated payload.
    if len(installation.get('installed_files',{}))!=1010 or installation.get('selection_sha256')!='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835':
        raise ValueError('selected installation member count differs')
    period=json.loads(PERIOD.read_bytes())
    result={'schema_version':'lab-T16-native-locator-rebind-proof/v1-candidate',
            'result':'PASS-DURABLE-BYTE-EQUIVALENCE',
            'old_locator':str(OLD),'old_locator_present':False,
            'new_locator':str(NEW),'native_sha256':EXPECTED,
            'original_mapper_source_sha256':sha(OLD_BUILD),
            'original_execution_selection_sha256':sha(EXECUTION),
            'installed_receipt_sha256':sha(INSTALL),
            'original_period_sha256':sha(PERIOD),
            'original_period_expires_at':period['expires_at'],
            'required_successor_work':['Fresh mapper selector and execution dependency manifest select the new locator',
                'Fresh Context source pins that selector and dependency manifest',
                'Fresh API source/runner pins the Context successor and current Source family',
                'Reconcile inherited tests whose expected historical current period is expired'],
            'historical_method_passed':False,'t16_qualified':False,'authority_effect':'none'}
    target=HERE/'NATIVE-REBIND-PROOF-0001.json'
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':result['result'],'new_locator_sha256':EXPECTED,
                      'original_period_expires_at':period['expires_at'],
                      'receipt':str(target),'sha256':sha(target)},sort_keys=True))

if __name__=='__main__': main()
