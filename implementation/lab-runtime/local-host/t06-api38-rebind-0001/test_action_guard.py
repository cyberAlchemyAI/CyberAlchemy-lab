"""Cold true-origin Action environment and selected source refusal tests."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[4]
OVERLAY=ROOT/'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
SOURCE='c530150e5cca87f2f3e84d897f423b16562de0fecdf3d17b39e8c6b421d07013'
PROFILE='32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869'
PROGRAM='''from importlib import import_module\nimport sys\napi=import_module("api-integration-v38-current-t06-0001")\nimport_module("api-integration-v38-current-t06-0001.protocol")\nimport_module("api-integration-v38-current-t06-0001.guard")\nm=import_module("api-action-integration-v5-current-t06-0001.dependencies")\nb={"ref":"product/lab/release-candidates/v1/interface/api-integration-v38-current-t06-0001/contract-profile.json","sha256":sys.argv[2]}\nm.guard(sys.argv[1],integration_profile_binding=b)\nprint("PASS")'''
class ActionGuard(unittest.TestCase):
 def run_guard(self,source=SOURCE,profile=PROFILE,overlay=True):
  env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1',
       'PYTHONPATH':str(OVERLAY)+':'+str(INTERFACE) if overlay else str(INTERFACE)}
  return subprocess.run([sys.executable,'-B','-c',PROGRAM,source,profile],cwd=ROOT,env=env,capture_output=True,text=True)
 def test_selected_overlay_passes(self):
  result=self.run_guard();self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'PASS')
 def test_unselected_environment_refuses(self):
  result=self.run_guard(overlay=False);self.assertNotEqual(result.returncode,0);self.assertIn('environment differs',result.stderr)
 def test_wrong_source_refuses(self):
  result=self.run_guard(source='0'*64);self.assertNotEqual(result.returncode,0)
 def test_wrong_profile_refuses(self):
  result=self.run_guard(profile='0'*64);self.assertNotEqual(result.returncode,0)
if __name__=='__main__':unittest.main()
