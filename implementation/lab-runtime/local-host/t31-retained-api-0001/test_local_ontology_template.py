"""Exact declared local adaptation, preserving original ontology template."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'docs/proposals/0007-lab-integrated-schema-package'

class LocalOntologyTemplate(unittest.TestCase):
 def test_only_explicit_source_evidence_role_and_workflow_identity_are_adapted(self):
  original=json.loads((BASE/'workflows/ontology-migration.json').read_bytes());adapted=json.loads((BASE/'workflows/ontology-migration-local-runtime-evidence.json').read_bytes())
  expected=copy.deepcopy(original);expected['workflow_type_ref']='workflow:ontology-migration-local-runtime-evidence:v1-candidate'
  for row in expected['transitions']:row['input_carriers']=['cal.artifact-type.evidence-set/v1'if c=='cal.artifact-type.source-admission/v1'else c for c in row['input_carriers']]
  self.assertEqual(adapted,expected)
  common=json.loads((BASE/'schemas/common.schema.json').read_bytes());schema=json.loads((BASE/'schemas/workflow-definition.schema.json').read_bytes())
  registry=Registry().with_resources([(common['$id'],Resource.from_contents(common))]);Draft202012Validator(schema,registry=registry).validate(adapted)
 def test_original_and_successor_mapping_are_bound_without_original_coverage_claim(self):
  mapping=json.loads((Path(__file__).parent/'ONTOLOGY-LOCAL-ADAPTATION-0001.json').read_bytes())
  for key in ('original_definition','successor_definition'):
   row=mapping[key];self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])
  self.assertFalse(mapping['original_definition_bytes_modified']);self.assertFalse(mapping['input_role_mapping']['exact_original_requirement_satisfied'])
  self.assertEqual(mapping['coverage_posture'],'adapted-local-technical-coverage-only');self.assertFalse(mapping['SourceAdmission_or_canonical_Source_admission_claimed'])

if __name__=='__main__':unittest.main()
