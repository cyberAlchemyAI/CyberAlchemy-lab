"""Real candidate schemas with synthetic projection transport, no native claim."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import ontology_evidence as P

class OntologyEvidence(unittest.TestCase):
 def setUp(self):
  self.scope='project:cyberalchemy-v2-to-lab-migration';self.cut={'synthetic-source-cut':True};self.owner='principal:synthetic-private-reader'
  dataset=json.loads((P.ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-de585bd7df9a130d/portable-dataset.json').read_bytes())
  bindings=dataset['bindings'];portable=SimpleNamespace(binding=lambda role:copy.deepcopy(bindings[role]),value=lambda role:self.scope)
  protocol=SimpleNamespace(source=SimpleNamespace(original=lambda row:(P.ROOT/row['path']).read_bytes()))
  actual=SimpleNamespace(root=lambda:P.ROOT,guard=lambda:None,current=lambda:SimpleNamespace(package={'entrypoint':{'api_directory':'synthetic-api'}}))
  self.patches=[patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':actual}),patch.object(P.importlib,'import_module',side_effect=lambda name:portable if name.endswith('.runtime_selection')else protocol)]
  for patcher in self.patches:patcher.start();self.addCleanup(patcher.stop)
  self.raw=b'{"synthetic-native-event-only":true}';self.mapping={'source_cut':self.cut,'rows':[{'artifact':{'scope_ref':self.scope}}]}
  self.manifest={'lab_source_cut':self.cut,'mapping_binding':{'ref':'synthetic:mapping-policy','sha256':'m'*64},'files':[{'path':'semantic/one.json','sha256':P.R.sha(self.raw)}]}
  self.head={'generation':'generation-synthetic','generation_sha256':P.R.sha(P.enc(self.manifest)),'store_ref':'owned-ontology:synthetic'}
  body=json.loads((P.ROOT/'authority/artifact-types/ontology-view/v1/fixtures/valid/record.json').read_bytes());raw=P.enc(body)
  self.view={'scope_ref':self.head['store_ref'],'identity_ref':body['node_id'],'version_ref':body['node_id']+'@synthetic.1','carrier_ref':'cal.artifact-type.ontology-view/v1','byte_sha256':P.R.sha(raw)}
  self.records={self.view['version_ref']:(self.view,raw)};self.seal()
 def seal(self):
  mraw=P.enc(self.manifest);self.head['generation_sha256']=P.R.sha(mraw);hraw=P.enc(self.head)
  receipt={'ontology_view':self.view,'ontology_applied_cut':{'commit_sha256':P.R.sha(hraw),'store_ref':self.head['store_ref']},'lab_source_cut':self.cut,'mapping_binding':self.manifest['mapping_binding']}
  self.observed={'observation_binding':{'ref':'synthetic:projection-observation','sha256':'o'*64},'original_source_cut':self.cut,
   'projection_producer':{'producer_kind':'actual-ontology-projection','receipt':receipt,'receipt_original_binding':{'ref':'synthetic:receipt','sha256':'r'*64}},
   'original_request':{'message':{'actor':{'principal_ref':self.owner}}},
   'files':{'vault/ontology/HEAD.json':hraw,'vault/ontology/generation-synthetic/manifest.json':mraw,'vault/ontology/generation-synthetic/semantic/one.json':self.raw,
            'native-inputs/mapping.json':P.enc(self.mapping),'vault/workspace.json':P.enc({'scope_refs':[self.scope],'principal_ref':self.owner})}}
 def produce(self):return P.produce(records=self.records,observations=[self.observed],controls={'projection_observation_ref':'synthetic:projection-observation'})
 def test_exact_original_evidence_emits_only_explicit_private_candidates(self):
  out=self.produce();self.assertEqual(len(out['records']),6);self.assertFalse(out['receipt']['SourceAdmission_requirement_satisfied'])
  self.assertEqual(out['receipt']['hypothesis_disposition'],'open')
  source=json.loads(next(raw for h,raw in out['records']if h['carrier_ref']=='cal.artifact-type.source/v1'));self.assertEqual(source['lifecycle_state'],'candidate');self.assertEqual(source['scope_ref'],self.scope)
 def test_changed_native_original_or_head_correspondence_refuses(self):
  self.observed['files']['vault/ontology/generation-synthetic/semantic/one.json']+=b' '
  with self.assertRaisesRegex(ValueError,'original member'):self.produce()
  self.seal();self.observed['projection_producer']['receipt']['ontology_applied_cut']['commit_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'head/store'):self.produce()
 def test_native_store_scope_cannot_replace_project_or_actor(self):
  self.mapping['rows'][0]['artifact']['scope_ref']=self.head['store_ref'];self.seal()
  with self.assertRaisesRegex(ValueError,'Project/Actor'):self.produce()
  self.mapping['rows'][0]['artifact']['scope_ref']=self.scope;self.seal();self.observed['files']['vault/workspace.json']=P.enc({'scope_refs':[self.scope],'principal_ref':'principal:foreign'})
  with self.assertRaisesRegex(ValueError,'Project/Actor'):self.produce()
 def test_extra_generation_member_or_unknown_control_refuses(self):
  self.observed['files']['vault/ontology/generation-synthetic/unlisted.json']=b'{}'
  with self.assertRaisesRegex(ValueError,'generation closure'):self.produce()
  with self.assertRaisesRegex(ValueError,'closed actual projection'):P.produce(records=self.records,observations=[self.observed],controls={'projection_observation_ref':'synthetic:projection-observation','undeclared':True})

if __name__=='__main__':unittest.main()
