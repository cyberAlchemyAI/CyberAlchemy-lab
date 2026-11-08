"""Frame semantics over real retained fixture originals; no currentness claim."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps')]
import frame as F
SOURCE=ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-5bd4f03a7076695c/source/packages/0001'
class Frame(unittest.TestCase):
 def setUp(self):
  rows=json.loads((SOURCE/'record-index.json').read_bytes());self.inputs={}
  for key,kind in [('intent','intent'),('work','work'),('goal','goal'),('coordination','coordination-context')]:
   row=next(r for r in rows if r['kind']==kind);raw=(ROOT/row['original_binding']['path']).read_bytes();ref=row['version_ref']
   self.inputs[key]=({'scope_ref':'project:cyberalchemy-v2-to-lab-migration','identity_ref':ref.rsplit('@',1)[0],'version_ref':ref,'carrier_ref':row['carrier_ref'],'byte_sha256':hashlib.sha256(raw).hexdigest()},raw)
  row=next(r for r in rows if ':goal-project@' in r['version_ref']);raw=(ROOT/row['original_binding']['path']).read_bytes();ref=row['version_ref']
  self.inputs['goal_project']=({'scope_ref':'project:cyberalchemy-v2-to-lab-migration','identity_ref':ref.rsplit('@',1)[0],'version_ref':ref,'carrier_ref':row['carrier_ref'],'byte_sha256':hashlib.sha256(raw).hexdigest()},raw)
  edge=json.loads(raw);raw=(SOURCE/'setup-artifacts/project.json').read_bytes();project=edge['payload']['target']
  self.inputs['project']=({'scope_ref':project['ref'],'identity_ref':project['ref'],'version_ref':project['version_ref'],'carrier_ref':'cal.artifact-type.project-identity/v1','byte_sha256':hashlib.sha256(raw).hexdigest()},raw)
 def make(self):return F.construct(root=ROOT,inputs=self.inputs,source_cut={'store_ref':'retained-fixture-component-only'},principal='principal:synthetic-private-coordinator',run_ref='workflow-run:frame-component')
 def test_exact_roles_keep_original_bytes_and_emit_four_typed_declarations(self):
  before=copy.deepcopy(self.inputs);capsule,raws=self.make();self.assertEqual(self.inputs,before);self.assertEqual(len(raws),4)
  self.assertFalse(capsule['original_Work_Goal_or_Source_bytes_rewritten']);self.assertEqual(capsule['private_records']['intent-resolution']['payload']['selected_subject_refs'][0],self.inputs['work'][0]['version_ref'])
 def test_changed_original_bytes_refused(self):
  h,raw=self.inputs['work'];self.inputs['work']=(h,raw+b' ')
  with self.assertRaisesRegex(ValueError,'original/header'):self.make()
 def test_semantically_valid_other_goal_cannot_retarget_original_work(self):
  h,raw=self.inputs['goal'];h=copy.deepcopy(h);h['identity_ref']='goal:foreign';h['version_ref']='goal:foreign@1';self.inputs['goal']=(h,raw)
  with self.assertRaisesRegex(ValueError,'identity/header|Work/Goal'):self.make()
 def test_rebound_goal_project_edge_refused_even_with_updated_sha(self):
  h,raw=self.inputs['goal_project'];body=json.loads(raw);body['payload']['target']['version_ref']='project:foreign@1';raw=F.enc(body);h=copy.deepcopy(h);h['byte_sha256']=F.sha(raw);self.inputs['goal_project']=(h,raw)
  with self.assertRaisesRegex(ValueError,'Goal/Project'):self.make()
if __name__=='__main__':unittest.main()
