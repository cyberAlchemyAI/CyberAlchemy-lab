import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import workspaces as w

class WorkspaceContract(unittest.TestCase):
 def setUp(self):
  self.catalog,self.profiles=w.profiles()
  self.p=copy.deepcopy(self.profiles["product/craft"])
 def rejected(self,code,fn,*args,**kwargs):
  with self.assertRaisesRegex(w.Refusal,code):fn(*args,**kwargs)
 def test_current_layout(self):
  result=w.verify_layout();self.assertEqual(result["physical_homes"],7);self.assertEqual(result["shared_runtime_targets"],1)
 def test_product_context_has_no_required_project(self):
  self.assertIsNone(w.context(self.p)["project_ref"])
 def test_multiple_projects_one_product(self):
  self.p["linked_project_refs"]+=["project:second"]
  for project in self.p["linked_project_refs"]:self.assertEqual(w.context(self.p,project_ref=project)["project_ref"],project)
 def test_foreign_project(self):self.rejected("foreign-project",w.context,self.p,project_ref="foreign")
 def test_project_without_product(self):
  p=copy.deepcopy(self.p);p.update(kind="project",primary_subject={"kind":"project","key":"project:standalone","ref":"project:standalone"},linked_project_refs=[],related_product_refs=[],goals=[])
  self.assertEqual(w.context(p)["project_ref"],"project:standalone")
 def test_project_rejects_other_primary(self):
  self.p.update(kind="project",primary_subject={"kind":"project","key":"p","ref":"p"},linked_project_refs=[],goals=[])
  self.rejected("foreign-project",w.context,self.p,project_ref="other")
 def test_kind_mismatch(self):
  self.p["primary_subject"]["kind"]="project";self.rejected("workspace-subject-kind",w.validate,self.p)
 def test_project_requires_identity(self):
  self.p.update(kind="project",primary_subject={"kind":"project","key":"p","ref":None},linked_project_refs=[],goals=[])
  self.rejected("primary-project-required",w.validate,self.p)
 def test_unselected_product_identity_is_not_invented(self):
  p=self.profiles["product/define"];self.assertIsNone(p["primary_subject"]["ref"]);w.validate(p)
 def test_stale_context(self):self.rejected("workspace-revision-mismatch",w.context,self.p,expected_revision="old")
 def test_goal_requires_project(self):self.rejected("project-required-for-goal",w.context,self.p,goal_ref=self.p["goals"][0]["goal_ref"])
 def test_goal_membership_preserved(self):
  goal=self.p["goals"][0];self.assertEqual(w.context(self.p,project_ref=goal["project_ref"],goal_ref=goal["goal_ref"])["goal_ref"],goal["goal_ref"])
 def test_wrong_goal_project(self):
  self.p["linked_project_refs"].append("other")
  self.rejected("goal-project-mismatch",w.context,self.p,project_ref="other",goal_ref=self.p["goals"][0]["goal_ref"])
 def test_work_requires_project(self):self.rejected("project-required-for-work",w.context,self.p,work={"payload":{}})
 def test_foreign_work(self):self.rejected("work-project-mismatch",w.context,self.p,project_ref=self.p["linked_project_refs"][0],work={"payload":{"project_ref":"other"}})
 def test_matching_work(self):
  project=self.p["linked_project_refs"][0];w.context(self.p,project_ref=project,work={"payload":{"project_ref":project}})
 def test_shared_default_distinct_namespaces(self):
  a=w.resolve(self.p,self.catalog);b=w.resolve(self.profiles["product/ontology"],self.catalog)
  self.assertEqual(a["runtime_ref"],b["runtime_ref"]);self.assertNotEqual(a["state_namespace_ref"],b["state_namespace_ref"])
 def specialize(self):
  self.p["runtime_selection"].update(behavior="specialized",specialization_ref="s")
  self.catalog["specializations"]["s"]={"workspace_ref":self.p["workspace_ref"],"model_version":w.MODEL,"configuration_overrides":{"context_budget_tokens":2048}}
 def test_specialization_keeps_shared_execution(self):
  self.specialize();self.assertEqual(w.resolve(self.p,self.catalog)["placement"],"shared")
 def test_specialization_cannot_grant_authority(self):
  self.specialize();self.catalog["specializations"]["s"]["configuration_overrides"]={"authority_grants":["all"]}
  self.rejected("specialization-outside-configuration",w.resolve,self.p,self.catalog)
 def test_foreign_specialization(self):
  self.specialize();self.catalog["specializations"]["s"]["workspace_ref"]="other"
  self.rejected("specialization-scope-mismatch",w.resolve,self.p,self.catalog)
 def test_bad_specialization_budget(self):
  self.specialize();self.catalog["specializations"]["s"]["configuration_overrides"]["context_budget_tokens"]=True
  self.rejected("specialization-budget",w.resolve,self.p,self.catalog)
 def test_dedicated_is_explicit(self):
  self.p["runtime_selection"].update(placement="dedicated",runtime_ref="missing")
  self.rejected("runtime-unavailable",w.resolve,self.p,self.catalog)
 def test_dedicated_selection_does_not_create_runtime(self):
  self.p["runtime_selection"].update(placement="dedicated",runtime_ref="dedicated")
  self.catalog["runtimes"]["dedicated"]={**self.catalog["runtimes"]["lab:shared-runtime"],"placement":"dedicated","bound_workspace_ref":self.p["workspace_ref"]}
  result=w.resolve(self.p,self.catalog);self.assertFalse(result["runtime_created"]);self.assertFalse(result["runtime_code_copied"])
 def test_incompatible_host(self):
  self.catalog["runtimes"]["lab:shared-runtime"]["supported_model_versions"]=["v1"]
  self.rejected("runtime-model-incompatible",w.resolve,self.p,self.catalog)
 def test_unknown_schema_version(self):
  self.p["schema_version"]="lab-workspace/v1";self.rejected("workspace-schema",w.validate,self.p)
 def test_explicit_v1_conversion(self):
  old=w.load(w.ROOT/"docs/proposals/0012-lab-workspace-model/craft/workspace.json")
  converted=w.migrate_v1(old,home="workspaces/projects/legacy-test")
  self.assertEqual(converted["primary_subject"]["ref"],old["project_ref"]);self.assertEqual(converted["workspace_ref"],old["workspace_ref"])
  self.assertEqual([g["goal_ref"] for g in converted["goals"]],[g["goal_ref"] for g in old["goals"]])
 def test_context_override_refuses_before_host(self):
  with patch("workspaces.subprocess.run") as host:
   self.rejected("dispatch-context-override",w.dispatch,self.p,self.catalog,"verify",["--repo","other"]);host.assert_not_called()
 def test_project_mutation_requires_selected_project(self):self.rejected("project-required-for-operation",w.dispatch,self.p,self.catalog,"review",["candidate.json"])
 def test_project_mutation_requires_explicit_store(self):self.rejected("explicit-native-store-required",w.dispatch,self.p,self.catalog,"review",["candidate.json"],project_ref=self.p["linked_project_refs"][0])
 def test_unbound_store_read_refuses(self):
  self.rejected("native-store-binding-required",w.dispatch,self.p,self.catalog,"status",store="/tmp/foreign")
 def test_existing_native_host_is_used(self):
  result,code=w.dispatch(self.p,self.catalog,"verify")
  self.assertEqual(code,0);self.assertEqual(result["native_result"]["result"],"PASS");self.assertFalse(result["workspace_context"]["runtime_code_copied"])
 def test_binding_cannot_bypass_native_replay(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.catalog["native_store_bindings"]=[{"workspace_ref":self.p["workspace_ref"],"project_ref":None,"store_path":tmp,"native_scope_ref":"scope:fake"}]
   self.rejected("native-store-invalid",w.dispatch,self.p,self.catalog,"status",store=tmp)
 def copied_metadata(self,root):
  import shutil
  selected=self.catalog["profiles"]
  files=["implementation/lab-workspaces/CURRENT.json","implementation/lab-workspaces/v2/catalog.json",
         "implementation/lab-workspaces/v2/workspace.schema.json","ontology/lab-workspace/v2/definition.json",
         "ontology/lab-workspace/v2/operating-model.json",*selected.values()]
  files += [p["model_binding_ref"] for p in self.profiles.values()]
  for name in files:
   target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w.ROOT/name,target)
 def test_profile_changes_require_an_exact_successor_binding(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.copied_metadata(root);p=root/self.catalog["profiles"]["product/craft"]
   body=json.loads(p.read_text());body["purpose"]="changed without a new exact binding";p.write_text(json.dumps(body))
   self.rejected("model-binding-profile-drift",w.profiles,root)
 def test_parent_contract_drift_refuses(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.copied_metadata(root);p=root/"ontology/lab-workspace/v2/operating-model.json"
   p.write_text(p.read_text()+" ")
   self.rejected("operating-model-drift",w.profiles,root)
 def test_current_entrypoint_cannot_implicitly_bypass_workspace_context(self):
  import subprocess,sys
  result=subprocess.run([sys.executable,str(w.ROOT/"implementation/lab-runtime/lab.py"),"review","unused.json"],text=True,capture_output=True)
  self.assertEqual(result.returncode,2)
  self.assertEqual(json.loads(result.stderr)["reason"],"workspace-context-required")
 def test_duplicate_scope_registration_refuses(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.copied_metadata(root);p=root/"implementation/lab-workspaces/v2/catalog.json"
   catalog=json.loads(p.read_text());catalog["profiles"]["product/duplicate"]=catalog["profiles"]["product/craft"];p.write_text(json.dumps(catalog))
   self.rejected("duplicate-workspace-identity",w.profiles,root)
if __name__=="__main__":unittest.main()
