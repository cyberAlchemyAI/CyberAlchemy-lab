"""Isolated actual signed-store tests for the pinned no-cache read bridge."""
import copy
from dataclasses import replace
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest

PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3]
sys.path.insert(0,str(PACKAGE))
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load, sealed
from lab_runtime.replay import ReplayPins, full_replay, replay
from lab_runtime.store import VerifiedLegacyReadStore
LEGACY=ROOT/'implementation/lab-runtime/v2'
spec=importlib.util.spec_from_file_location('replay_fixture_v2',LEGACY/'lab_runtime/__init__.py',submodule_search_locations=[str(LEGACY/'lab_runtime')])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
from replay_fixture_v2.store import Store,keygen
from replay_fixture_v2.cli import example

class ReplayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=TemporaryDirectory(prefix='lab-replay-parity-fixture-');cls.root=Path(cls.temp.name)
  cls.repository=cls.root/'repository';cls.repository.mkdir()
  from replay_fixture_v2.sources import capture
  snapshot=capture(ROOT,load(LEGACY/'profile.json'))
  source_paths=set(snapshot['materials'])
  for names in snapshot['epoch_inventory'].values(): source_paths.update(names)
  for name in source_paths:
   target=cls.repository/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
  private=cls.root/'test-only.pem';public=cls.root/'test-only.pub';keygen(private,public)
  cls.fixture=cls.root/'fixture';store=Store(cls.fixture,cls.repository)
  store.initialize(load(LEGACY/'profile.json'),'parity-fixture','role:test-only-candidate-operator',public.read_text().strip())
  proposal=example(store,'parity-work');store.apply(proposal,store.authorize(proposal,private))
  manifest=PACKAGE/'design/legacy-runtime-bindings.json'
  cls.pins=ReplayPins('v2',manifest.relative_to(ROOT).as_posix(),byte_digest(manifest.read_bytes()),byte_digest((cls.fixture/'config.json').read_bytes()),load(cls.fixture/'baseline.json')['snapshot_digest'])
  cls.performance=[]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def setUp(self):
  self.temp=TemporaryDirectory(prefix='lab-replay-parity-case-');self.root=Path(self.temp.name);self.store=self.root/'store';shutil.copytree(self.fixture,self.store)
 def tearDown(self):self.temp.cleanup()
 def read(self,**kw):return replay(self.store,self.repository,ROOT,self.pins,**kw)
 def test_full_noop_parity(self):
  t=time.perf_counter();a=full_replay(self.store,self.repository,ROOT,self.pins,require_current=True);ta=time.perf_counter()-t
  t=time.perf_counter();b=self.read(require_current=True);tb=time.perf_counter()-t
  self.assertEqual(a,b);self.performance.append({'case':'one-signed-transaction','full_seconds':ta,'public_noop_seconds':tb,'projection_digest':digest(a['projection']),'equal':True,'samples':1,'variance':None})
 def test_fresh_process_reconstruction(self):
  args=json.dumps({'path':str(self.store),'repository':str(self.repository),'executable_repo':str(ROOT),'pins':self.pins.__dict__})
  code="import json,sys;from lab_runtime.replay import ReplayPins,full_replay;from lab_runtime.common import digest;x=json.loads(sys.argv[1]);x['pins']=ReplayPins(**x['pins']);r=full_replay(**x,require_current=True);print(digest(r['projection']))"
  result=subprocess.run([sys.executable,'-c',code,args],cwd=PACKAGE,capture_output=True,text=True,timeout=45)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(result.stdout.strip(),digest(Store(self.store,self.repository).replay(require_current=True)['projection']))
 def test_historical_transaction_mutation_same_mtime_and_head(self):
  path=self.store/'transactions/0000000001.json';stat=path.stat();d=load(path);d['proposal']['reason']='tampered';path.write_bytes(encoded(d));import os;os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
  with self.assertRaises(RuntimeFault):self.read()
 def test_resealed_invalid_historical_signature(self):
  txpath=self.store/'transactions/0000000001.json';tx=load(txpath);tx['approval']['signature']='0'*128;tx=sealed({k:v for k,v in tx.items() if k!='digest'});txpath.write_bytes(encoded(tx))
  head=load(self.store/'HEAD.json');head['transaction_digest']=tx['digest'];(self.store/'HEAD.json').write_bytes(encoded(sealed({k:v for k,v in head.items() if k!='digest'})))
  with self.assertRaises(RuntimeFault):self.read()
 def test_self_resealed_configuration_cannot_change_pin(self):
  path=self.store/'config.json';d=load(path);d['owner_ref']='role:other';path.write_bytes(encoded(sealed({k:v for k,v in d.items() if k!='digest'})))
  with self.assertRaisesRegex(RuntimeFault,'configuration pin'):self.read()
 def test_self_resealed_baseline_cannot_change_pin(self):
  path=self.store/'baseline.json';d=load(path);d['subjects'][next(iter(d['subjects']))]['effective_state']='admitted-current';d['profile']['challenge_route']='route:forged';d['snapshot_digest']=digest({k:v for k,v in d.items() if k!='snapshot_digest'});path.write_bytes(encoded(d))
  with self.assertRaisesRegex(RuntimeFault,'baseline pin'):self.read()
 def test_wrong_runtime_profile(self):
  with self.assertRaises(RuntimeFault):full_replay(self.store,self.repository,ROOT,replace(self.pins,runtime_version='v1'),require_current=True)
 def test_external_head_pin(self):
  with self.assertRaisesRegex(RuntimeFault,'HEAD pin'):full_replay(self.store,self.repository,ROOT,replace(self.pins,expected_head='0'*64))
 def test_executable_manifest_pin(self):
  with self.assertRaisesRegex(RuntimeFault,'executable manifest'):full_replay(self.store,self.repository,ROOT,replace(self.pins,manifest_sha256='0'*64))
 def test_persistent_checkpoint_cannot_bypass(self):
  (self.store/'CHECKPOINT.json').write_bytes(encoded(sealed({'projection':{'subjects':{}},'head':load(self.store/'HEAD.json')})))
  with self.assertRaisesRegex(RuntimeFault,'checkpoint'):self.read()
 def test_store_symlink_rejected(self):
  p=self.store/'baseline.json';raw=p.read_bytes();other=self.root/'baseline';other.write_bytes(raw);p.unlink();p.symlink_to(other)
  with self.assertRaisesRegex(RuntimeFault,'symlink'):self.read()
 def test_duplicate_json_transaction_keys_rejected(self):
  p=self.store/'transactions/0000000001.json';p.write_text('{"sequence":1,"sequence":2}')
  with self.assertRaisesRegex(RuntimeFault,'duplicate JSON'):self.read()
 def test_changed_source_requires_fresh_verification(self):
  name=next(n for n in load(self.store/'baseline.json')['materials'] if n.endswith('schema.json'))
  file=self.repository/name;raw=file.read_bytes()
  try:
   file.write_bytes(raw+b'\n')
   with self.assertRaisesRegex(RuntimeFault,'stale repository'):self.read(require_current=True)
  finally:file.write_bytes(raw)
 def test_readonly_facade_has_no_effect_methods(self):
  facade=VerifiedLegacyReadStore(self.store,self.repository,ROOT,self.pins)
  for name in ['initialize','authorize','apply','recover','checkpoint']:self.assertFalse(hasattr(facade,name))

if __name__=='__main__':unittest.main()
