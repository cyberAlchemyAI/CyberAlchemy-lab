"""Actual journal cold replay over a synthetic candidate transition only."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import prior_journal as P
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001'))
import output_store as S
PATH=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/current-api30-output-fixture-20261023/test_output_journal.py'
spec=importlib.util.spec_from_file_location('_t31_prior_journal_synthetic_plan',PATH);F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)

class PriorJournal(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-prior-journal-component-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.root.chmod(0o700)
  plan,before,header=F.candidate_plan();body=json.loads((ROOT/'authority/artifact-types/challenge-event/v1/fixtures/valid/record.json').read_bytes());body['scope_ref']=header['scope_ref'];raw=S.J.K.encoded(body)
  self.store=S.OutputJournal.initialize(self.root/'live',before,header['scope_ref'],plan['next_run']['actor']['principal_ref'])
  self.store.apply(plan,originals={header['version_ref']:raw},request_binding=F.binding('fixture:actual-component-request',b'component only'),host_guard=lambda:None)
  self.archive=self.root/'retained-archive';shutil.copytree(self.store.root,self.archive)
  head,run=self.store.replay();index,files=P.capture(self.archive)
  self.expected={'journal_config_sha256':self.store.journal.config_sha256,'head':head,'run_sha256':P.R.sha(run),'inventory_sha256':P.R.sha(P.enc(index))}
  self.target=self.root/'restored';self.original=(index,files)
 def test_exact_originals_are_copied_independent_of_inode_then_replayed(self):
  restored=P.copy_selected(self.archive,self.target,self.expected,S.OutputJournal)
  self.assertEqual(restored.replay(),self.store.replay());self.assertEqual(restored.consume(1),self.store.consume(1));self.assertEqual(P.capture(self.archive),self.original)
  self.assertNotEqual((self.archive/'HEAD.json').stat().st_ino,(self.target/'HEAD.json').stat().st_ino)
 def test_wrong_selected_head_refuses_before_live_copy(self):
  self.expected['head']['sequence']+=1
  with self.assertRaisesRegex(ValueError,'HEAD differs'):P.copy_selected(self.archive,self.target,self.expected,S.OutputJournal)
  self.assertFalse(self.target.exists())
 def test_linked_prior_member_refuses_before_live_copy(self):
  p=self.archive/'HEAD.json';p.unlink();p.symlink_to(self.store.root/'HEAD.json')
  with self.assertRaisesRegex(ValueError,'linked prior'):P.copy_selected(self.archive,self.target,self.expected,S.OutputJournal)
  self.assertFalse(self.target.exists())
 def test_stale_or_changed_archive_inventory_refuses(self):
  p=self.archive/'outputs'/next(iter((self.archive/'outputs').iterdir())).name;p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'inventory'):P.copy_selected(self.archive,self.target,self.expected,S.OutputJournal)
  self.assertFalse(self.target.exists())
 def test_resealed_inventory_does_not_replace_actual_transaction_replay(self):
  path=self.archive/'transactions/00000001.json';tx=json.loads(path.read_bytes());tx['event']['to_state']='invented';path.write_bytes(S.J.K.encoded(tx))
  index,_=P.capture(self.archive);self.expected['inventory_sha256']=P.R.sha(P.enc(index))
  with self.assertRaises(ValueError):P.copy_selected(self.archive,self.target,self.expected,S.OutputJournal)

if __name__=='__main__':unittest.main()
