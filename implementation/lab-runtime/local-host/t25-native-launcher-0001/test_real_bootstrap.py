"""Real selected bootstrap/provider over a bounded Source-metadata fixture.

This exercises actual installed native files and startup controls, not Source,
API or final full-runtime qualification.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
HERE=Path(__file__).resolve().parent
SUPPORT=HERE.parent/'t25-integrated-runtime-0004'
sys.path.insert(0,str(SUPPORT))
import test_installed_selection as T
import native_install as N
PROOF_OUTPUT = None

class RealBootstrap(unittest.TestCase):
    # Reuse fixture construction only. Provider tests have their own ready-phase
    # lane and must not be rediscovered under this construction-phase fixture.
    fixture = T.InstalledSelection.fixture
    write = staticmethod(T.InstalledSelection.write)
    def setUp(self):
        T.InstalledSelection.setUp(self)
        original=json.loads((HERE.parents[3]/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/installation.json').read_bytes())
        # HERE.parents[3] is repository root for this component directory.
        members=original['installed_files'];selection='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
        shutil.rmtree(self.private/'native')
        result=N.install(self.private,Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001',members,selection)
        self.config['values'].update({'native.identity':N.identity(self.private/'native'),
             'native.receipt':{'path':str(self.private/'native/installation.json'),'sha256':result['sha256']},
             'native.dependency_selection':{'path':'fixture-original-native-selection.json','sha256':selection}})
        self.package['native_payload']={'members':members,'selection_binding':{'path':'fixture-original-native-selection.json','sha256':selection}}
        components={
          'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/installed_selection.py':SUPPORT/'installed_selection.py',
          'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/native_install.py':SUPPORT/'native_install.py',
          'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py':SUPPORT/'child_bootstrap.py',
          'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python':HERE/'selected-python',
          'implementation/lab-runtime/local-host/t25-native-launcher-0001/probe_tree.py':HERE/'probe_tree.py'}
        for relative,source in components.items():
            target=self.root/relative;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            shutil.copyfile(source,target);target.chmod(0o755 if source.name=='selected-python' else 0o600)
            raw=target.read_bytes();self.package['members'].append({'path':relative,'repository_path':relative,'sha256':T.sha(raw),'size_bytes':len(raw),'mode':target.stat().st_mode&0o777})
        package_raw=T.encoded(self.package);self.write(self.root/'.cal-package-manifest.json',package_raw)
        self.config['package_manifest_sha256']=T.sha(package_raw)
        config_raw=T.encoded(self.config);self.write(self.private/'bindings/host-selection.json',config_raw)
        self.receipt.update({'phase':'construct-context','package_manifest_sha256':T.sha(package_raw),'host_selection_sha256':T.sha(config_raw)})
        receipt_raw=T.encoded(self.receipt);self.write(self.private/'installation.json',receipt_raw)
        self.write(self.private/'launcher.json',T.encoded({'schema_version':'lab-installed-launcher-selection/v1','installation_receipt_sha256':T.sha(receipt_raw)}))
        self.launcher=self.root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
        self.probe=self.root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/probe_tree.py'

    def test_actual_real_bootstrap_child_grandchild(self):
        child=subprocess.run([str(self.launcher),'-I','-B',str(self.probe)],capture_output=True,text=True,check=True)
        self.assertFalse(child.stderr)
        result=json.loads(child.stdout);row=result['process']
        for depth in range(3):
            self.assertEqual(row['depth'],depth);self.assertTrue(row['all_mapped_ELF_private_and_hash_verified'])
            self.assertEqual(row['bootstrap_proof']['phase'],'construct-context');self.assertEqual(row['optimization'],int(depth>0))
            if depth<2:row=row['child']['process']
        # Ordinary verification is read-only with respect to retained evidence.
        # Explicit collection creates a fresh proof without replacing any file.
        if PROOF_OUTPUT is not None:
            raw = (json.dumps({'result':result['result'], 'source_metadata_is_explicit_component_fixture':True,
                              'API_imported':False, 'proof':result},indent=2,sort_keys=True)+'\n').encode()
            fd = os.open(PROOF_OUTPUT, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as output:
                output.write(raw); output.flush(); os.fsync(output.fileno())

    def test_changed_private_selection_refused_before_target(self):
        raw=(self.private/'bindings/host-selection.json').read_bytes()
        self.write(self.private/'bindings/host-selection.json',raw+b' ')
        child=subprocess.run([str(self.launcher),'-c','print("MUST-NOT-RUN")'],capture_output=True,text=True)
        self.assertNotEqual(child.returncode,0);self.assertFalse(child.stdout)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--evidence-output')
    options,remaining=parser.parse_known_args()
    PROOF_OUTPUT=options.evidence_output
    unittest.main(argv=[__file__,*remaining])
