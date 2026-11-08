"""Cold true-origin Action environment and selected source refusal tests."""
import os
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[4]
OVERLAY=ROOT/'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
SOURCE='9f8fdb8dea1545fd7767853ba867f6d10c83ea7c8c50df047c054632eed15900'
PROFILE='cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614'
PROGRAM='''from importlib import import_module\nimport sys\napi=import_module("api-integration-v40-current-t06-0001")\nimport_module("api-integration-v40-current-t06-0001.protocol")\nimport_module("api-integration-v40-current-t06-0001.guard")\nm=import_module("api-action-integration-v7-current-t06-0001.dependencies")\nb={"ref":"product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json","sha256":sys.argv[2]}\nm.guard(sys.argv[1],integration_profile_binding=b)\nprint("PASS")'''
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
 def test_installed_interpreter_import_closure_is_selected(self):
  install=ROOT/'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
  metadata=json.loads((install/'installation.json').read_bytes())
  profile=json.loads((INTERFACE/'api-integration-v40-current-t06-0001/contract-profile.json').read_bytes())
  rows={row['path']:row['sha256'] for row in profile['files']}
  self.assertEqual(len(metadata['installed_files']),1010)
  for name,binding in metadata['installed_files'].items():
   path=install/name
   relative=path.relative_to(ROOT).as_posix()
   self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),binding['sha256'])
   self.assertEqual(rows.get(relative),binding['sha256'])
  program="import sys;sys.path[:0]=sys.argv[1:4];"+PROGRAM.replace('sys.argv[1]','sys.argv[4]').replace('sys.argv[2]','sys.argv[5]')
  argv=[str(install/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(install/'lib/abi'),
        str(install/'bin/python'),'-I','-X','utf8','-B','-S','-c',program,
        str(INTERFACE),str(OVERLAY),str(install/'deps'),SOURCE,PROFILE]
  result=subprocess.run(argv,cwd=ROOT,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONNOUSERSITE':'1',
    'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(result.stdout.strip(),'PASS')
if __name__=='__main__':unittest.main()
