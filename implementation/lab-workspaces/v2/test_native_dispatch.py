"""Exercise the workspace adapter against a real sealed native store."""
import copy,json,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import workspaces as w

class NativeDispatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import sys
  sys.path.insert(0,str(w.ROOT/"implementation/lab-runtime/v2"))
  from lab_runtime.store import Store
  cls.tmp=tempfile.TemporaryDirectory(prefix="lab-workspace-native-test-")
  cls.store=Path(cls.tmp.name)/"store"
  cls.private=Ed25519PrivateKey.generate()
  key=cls.private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
  native=Store(cls.store,w.ROOT)
  native.initialize(w.load(w.ROOT/"implementation/lab-runtime/v2/profile.json"),"workspace-adapter-test","role:fixture-owner",key)
  cls.data=native.replay(require_current=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):
  self.catalog,profiles=w.profiles()
  self.p=copy.deepcopy(profiles["product/craft"])
  self.project=self.data["projection"]["state"]["payload"]["project_ref"]
  self.p.update(kind="project",workspace_ref="workspace:sealed-store-fixture",primary_subject={"kind":"project","key":self.project,"ref":self.project},linked_project_refs=[],goals=[])
  self.catalog["runtimes"]["lab:shared-runtime"]["workspace_refs"].append(self.p["workspace_ref"])
  self.catalog["native_store_bindings"]=[{"workspace_ref":self.p["workspace_ref"],"project_ref":self.project,"store_path":str(self.store),"native_scope_ref":self.data["config"]["scope_ref"]}]
 def test_explicit_store_binding_replays_native_state(self):
  result,code=w.dispatch(self.p,self.catalog,"verify",store=self.store)
  self.assertEqual(code,0);self.assertEqual(result["native_result"]["result"],"PASS")
 def test_configuration_cannot_substitute_project(self):
  self.p["primary_subject"].update(key="foreign-project",ref="foreign-project")
  self.catalog["native_store_bindings"][0]["project_ref"]="foreign-project"
  with self.assertRaisesRegex(w.Refusal,"native-store-project-mismatch"):w.dispatch(self.p,self.catalog,"verify",store=self.store)
 def test_configuration_cannot_substitute_scope(self):
  self.catalog["native_store_bindings"][0]["native_scope_ref"]="foreign-scope"
  with self.assertRaisesRegex(w.Refusal,"native-store-scope-mismatch"):w.dispatch(self.p,self.catalog,"verify",store=self.store)
 def test_native_review_still_refuses_invalid_proposal(self):
  proposal=Path(self.tmp.name)/"invalid.json";proposal.write_text('{"schema_version":"invalid"}')
  result,code=w.dispatch(self.p,self.catalog,"review",[str(proposal)],store=self.store)
  self.assertEqual(code,2);self.assertEqual(result["native_result"],None)
  self.assertIn("BLOCKED",result["native_stderr"])
 def test_valid_project_work_reaches_existing_native_review(self):
  from lab_runtime.cli import example
  from lab_runtime.store import Store
  proposal=Path(self.tmp.name)/"valid-work.json"
  proposal.write_text(json.dumps(example(Store(self.store,w.ROOT),"workspace-owned-work")))
  result,code=w.dispatch(self.p,self.catalog,"review",[str(proposal)],store=self.store)
  self.assertEqual(code,0)
 def test_foreign_work_target_refuses_before_native_review(self):
  from lab_runtime.cli import example
  from lab_runtime.store import Store
  record=example(Store(self.store,w.ROOT),"workspace-foreign-work")
  record["targets"][0]["record"]["payload"]["project_ref"]="foreign-project"
  proposal=Path(self.tmp.name)/"foreign-work.json";proposal.write_text(json.dumps(record))
  with self.assertRaisesRegex(w.Refusal,"proposal-project-mismatch"):
   w.dispatch(self.p,self.catalog,"review",[str(proposal)],store=self.store)
if __name__=="__main__":unittest.main()
