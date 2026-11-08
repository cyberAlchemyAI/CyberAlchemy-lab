#!/usr/bin/env python3
"""Independent fixed JSON Schema tests, not parser/graph/native evidence. Open Questions: docs/BUSINESS-AUTHORING-V2.md."""
import copy,json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
CORE=Path(__file__).resolve().parents[2]
ROOT=CORE.parents[4]
SCHEMA=json.loads((CORE/'contracts/business-spec-v2.schema.json').read_text())
SPEC=json.loads((CORE/'test/profile-engine/fixtures/u0-v2/spec.json').read_text())
VALIDATOR=Draft202012Validator(SCHEMA)
class U0Contract(unittest.TestCase):
 def rejects(self,change):
  value=copy.deepcopy(SPEC);change(value);self.assertTrue(list(VALIDATOR.iter_errors(value)))
 def test_01_fixed_schema_is_standard_closed_shape(self):
  Draft202012Validator.check_schema(SCHEMA);VALIDATOR.validate(SPEC)
  self.assertEqual(SPEC['definitions'],[]);self.assertEqual(SPEC['claims'],[])
 def test_02_direct_condition_cannot_be_omitted_or_supplied_by_a_claim(self):
  self.rejects(lambda v:v['rules'][0].pop('condition'))
  self.rejects(lambda v:v['rules'][0].update(claim_ref='Fake'))
  self.rejects(lambda v:v['rules'][0].update(condition={'kind':'javascript','code':'true'}))
  self.rejects(lambda v:v['rules'][0]['condition']['value'].update(path=[]))
  self.rejects(lambda v:v['rules'][0]['condition']['value'].update(path=['nested','verified']))
 def test_03_only_the_selected_entity_field_types_are_declared(self):
  self.rejects(lambda v:v['entities'][0]['fields'][1].update(type='String'))
  self.rejects(lambda v:v['entities'][0]['fields'].pop())
  self.rejects(lambda v:v['entities'][0]['fields'].append({'name':'label','type':'Bool','meaning':'Extra.'}))
 def test_04_guard_result_and_effects_are_explicit(self):
  self.rejects(lambda v:v['operations'][0].update(guards=[]))
  self.rejects(lambda v:v['operations'][0]['result'].update(path=['id']))
  self.rejects(lambda v:v['operations'][0].update(effects=['write']))
  self.rejects(lambda v:v['operations'][0].pop('on_rejection'))
 def test_05_permission_is_closed_and_attached_to_entry(self):
  self.rejects(lambda v:v['entries'][0].pop('permission'))
  self.rejects(lambda v:v['entries'][0].update(permission={'kind':'authenticated'}))
  self.rejects(lambda v:v['entries'][0].update(permission={'kind':'public','verified':True}))
  self.rejects(lambda v:v.update(permissions={'ProcessHttp':'public'}))
 def test_06_annotations_are_optional_and_cannot_grant_custody(self):
  prior=json.loads((CORE/'contracts/business-spec-v1.schema.json').read_text())
  self.assertEqual(prior['properties']['claims']['minItems'],1)
  self.assertEqual(SCHEMA['properties']['claims']['minItems'],0)
  self.rejects(lambda v:v.update(accepted=True))
  self.rejects(lambda v:v.update(graph={'ready':True}))
  self.rejects(lambda v:v.update(schema_version='alchlang.business-spec/v1-candidate'))
 def test_07_requirement_context_and_counterexample_remain_required(self):
  self.rejects(lambda v:v['requirements'][0].pop('context'))
  self.rejects(lambda v:v['requirements'][0].update(counterexamples=[]))
 def test_08_source_version_and_generated_mirror_have_one_owner(self):
  self.assertEqual((CORE/'test/profile-engine/fixtures/u0-v2/business.alch').read_text().splitlines()[0],'source-contract alchlang.business-spec/v2-candidate')
  canonical=(CORE/'src/profile-engine/business-authoring-protocol-v2.ts').read_text()
  mirror=(ROOT/'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-protocol-v2.ts').read_text()
  self.assertEqual(mirror,'// GENERATED from Core business-authoring-protocol-v2.ts; canonical owner is Core.\n'+canonical)
 def test_09_claim_shape_is_separate_and_subject_explicit(self):
  self.rejects(lambda v:v.update(claims=[{'id':'Claim','proposition':'true'}]))
  self.assertNotIn('claim_ref',SCHEMA['$defs']['direct_rule']['properties'])
  self.assertIn('subject_refs',SCHEMA['$defs']['assurance_claim']['required'])
  value=copy.deepcopy(SPEC)
  value['definitions']=[{'id':'Eligibility','requirement_ref':'Processing','input':{'name':'item','type_ref':'Submission'},'meaning':'Supplied eligibility.','boolean_field':{'root':'item','path':['verified']}}]
  value['claims']=[{'id':'EligibilityClaim','version':'1','supersedes':None,'requirement_ref':'Processing','logic_profile':'fol-core/1-candidate','sorts':[{'name':'SubmissionValue','type_ref':'Submission'}],'predicates':[{'name':'Eligible','sort_refs':['SubmissionValue'],'definition_ref':'Eligibility'}],'constants':[{'name':'current','sort_ref':'SubmissionValue'}],'proposition':'Eligible(current)','ceiling':'One supplied flag; no proof.','subject_refs':['CanProcess']}]
  VALIDATOR.validate(value)
  self.assertEqual(value['rules'],SPEC['rules'])
  self.assertEqual(value['operations'],SPEC['operations'])

if __name__=='__main__':unittest.main(verbosity=2)
