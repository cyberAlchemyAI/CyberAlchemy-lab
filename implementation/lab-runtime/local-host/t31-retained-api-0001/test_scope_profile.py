"""Actual scoped store/copy checks with explicit synthetic producer evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest
import scope_profile as P
ROOT=Path(__file__).resolve().parents[4];PATH=ROOT/'implementation/lab-runtime/local-host/t31-scoped-output-0001/test_scoped.py'
P.modules();spec=importlib.util.spec_from_file_location('_t31_scope_persistence_synthetic_fixture',PATH);T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)

class ScopeProfile(unittest.TestCase):
 def setUp(self):
  self.fixture=T.ScopedTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups);f=self.fixture
  self.binding={'ref':str(f.index_path),'sha256':P.R.sha(f.index_path.read_bytes())};self.vault=f.folder/'vault';self.vault.mkdir(mode=0o700);(self.vault/'inputs').mkdir(mode=0o700);self.manifest={'materials':[]}
 def test_exact_index_and_original_members_persist_then_actual_scoped_replay(self):
  before=P.capture(self.binding);selection,binding=P.persist(self.binding,vault=self.vault,manifest=self.manifest)
  self.assertEqual(P.capture({'ref':selection.index_path,'sha256':selection.index_sha256}),before);self.assertEqual(P.capture(self.binding),before)
  f=self.fixture;f.apply();module=P.modules()['scoped_store'];store=module.ScopedOutputJournal(f.journal.root,f.journal.config_sha256,scope_selection=selection)
  self.assertEqual(store.replay(),f.store.replay());self.assertEqual(store.consume(1),f.store.consume(1));self.assertEqual(binding['sha256'],self.binding['sha256'])
 def test_wrong_selected_index_hash_refuses_before_vault_copy(self):
  self.binding['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'ScopeIndex original'):P.persist(self.binding,vault=self.vault,manifest=self.manifest)
  self.assertFalse((self.vault/'inputs/scope-evidence').exists())
 def test_changed_or_linked_original_member_refuses(self):
  f=self.fixture;member=f.folder/'contract.json';member.write_bytes(member.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'scope original member'):P.persist(self.binding,vault=self.vault,manifest=self.manifest)
  member.unlink();member.symlink_to(f.folder/'receipt.json')
  with self.assertRaises((OSError,ValueError)):P.persist(self.binding,vault=self.vault,manifest=self.manifest)
 def test_preloaded_foreign_scoped_module_is_not_accepted(self):
  m=P.modules()['scoped_headers'];old=m.__file__;m.__file__='/tmp/foreign-scoped-headers.py'
  try:
   with self.assertRaisesRegex(ValueError,'module origin'):P.modules()
  finally:m.__file__=old

if __name__=='__main__':unittest.main()
