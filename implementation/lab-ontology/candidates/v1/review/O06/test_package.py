"""Guard every independent candidate review axis and original source gap."""
import tempfile,unittest
from jsonschema.exceptions import ValidationError
from package import *

class ReviewGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.output=HERE/'packages/0001';cls.original=original(binding(cls.output/'preparation.json'))
  cls.fixture=tempfile.TemporaryDirectory(prefix='guard-',dir=HERE/'packages');cls.mutable=Path(cls.fixture.name)
  v,files=expected(cls.mutable);cls.fixture_value=v
  for p,raw in files.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 @classmethod
 def tearDownClass(cls):cls.fixture.cleanup()
 def setUp(self):self.value=copy.deepcopy(self.original)
 def member(self,kind):return next(m for m in self.value['members'] if m['member_class']==kind)
 def reject(self):
  with self.assertRaises((ValueError,ValidationError)):validate(self.value,self.output)
 def reject_file(self,relative,fn):
  p=self.mutable/relative;raw=p.read_bytes()
  try:
   v=parse(raw);fn(v);p.write_bytes(encoded(v))
   with self.assertRaises((ValueError,ValidationError)):validate(self.fixture_value,self.mutable)
  finally:p.write_bytes(raw)
 def test_exact_preparation_valid(self):self.assertEqual(validate(self.value,self.output)['members'],323)
 def test_all_original_postimages_equal(self):
  for m in self.value['members']:
   if m['member_class']=='metadata-carrier-admission':self.assertEqual(bound(m['targets'][0]),bound(m['targets'][1]))
 def test_220_records_fit_exact_source_schemas(self):
  for row in original(binding(ONTOLOGY/'migration/candidate/0001/record-index.json')):
   Draft202012Validator(original(row['schema_binding'])).validate(parse((self.output/'postimages'/row['path']).read_bytes()))
 def test_88_adoptions_remain_independent(self):
  imports=[m for m in self.value['members'] if m['member_class']=='metadata-carrier-admission'];adoptions=[m for m in self.value['members'] if m['member_class']=='representation-adoption-intent']
  self.assertEqual((len(imports),len(adoptions)),(220,88));self.assertTrue(all(m['requested_axes']['ontology_representation_adoption'] and not m['requested_axes']['metadata_carrier_admission'] for m in adoptions))
 def test_all_140_dispositions_and_nine_blocked_retained(self):
  v=original(self.value['source_disposition_binding']);self.assertEqual(len(v['items']),140);self.assertEqual(sum(x['disposition']=='block' for x in v['items']),9)
 def test_20_excluded_and_deferred_epoch_retained(self):
  v=original(self.value['source_disposition_binding']);self.assertEqual(len(v['excluded_packages']),20);self.assertTrue(v['deferred_source_epoch'])
 def test_no_actual_authority_or_source_effects(self):self.assertFalse(any(self.value['actual_effects'].values()));self.assertIsNone(self.value['actual_owner_outcome'])
 def test_three_distinct_query_epochs_retained(self):
  v=original(self.value['query_gap_binding']);self.assertEqual(set(v),{'historical-D73','current-D75','native-O05'});self.assertTrue(all(any(q['gaps'] for q in v[k]['questions'].values()) for k in v))
 def test_mandatory_genesis_correction_bound(self):self.assertIn(b'hash-sealed genesis',bound(self.value['replay_design_correction_binding']))
 def test_W09_negative_and_bounded_evidence_retained(self):
  v=self.member('operational-evidence-selection')['scope'];self.assertEqual(v['Research_hypothesis'],'negative');self.assertFalse(v['current_application_permission']);self.assertFalse(v['human_pilot'])
 def test_missing_member_rejected(self):self.value['members'].pop();self.reject()
 def test_duplicate_member_rejected(self):self.value['members'][0]=copy.deepcopy(self.value['members'][1]);self.reject()
 def test_member_dependency_drop_rejected(self):self.member('representation-adoption-intent')['dependencies'].pop();self.reject()
 def test_unknown_dependency_rejected(self):self.member('metadata-carrier-admission')['dependencies'].append('protocol:O06:unknown');self.reject()
 def test_fixture_owner_substitution_rejected(self):self.member('metadata-carrier-admission')['scope']['fixture_owner_is_final_owner']=True;self.reject()
 def test_source_semantic_admission_rejected(self):self.member('metadata-carrier-admission')['scope']['source_semantic_admission']=True;self.reject()
 def test_domain_conformance_inferred_rejected(self):self.member('metadata-carrier-admission')['scope']['domain_instance_conformance']=True;self.reject()
 def test_carrier_admission_collapsed_into_adoption_rejected(self):self.member('metadata-carrier-admission')['requested_axes']['ontology_representation_adoption']=True;self.reject()
 def test_adoption_collapsed_into_metadata_admission_rejected(self):self.member('representation-adoption-intent')['requested_axes']['metadata_carrier_admission']=True;self.reject()
 def test_unregistered_type_invented_rejected(self):self.member('metadata-carrier-admission')['scope']['carrier_ref']='cal.artifact-type.ontology-profile/v1';self.reject()
 def test_new_implementation_realization_invented_rejected(self):self.member('metadata-generator-selection')['scope']['realizes_capability_refs']=['capability:invented'];self.reject()
 def test_final_runtime_binding_inferred_rejected(self):self.member('native-implementation-selection')['scope']['runtime_binding_materialization_required_at']='O06';self.reject()
 def test_new_operation_grant_rejected(self):self.member('native-implementation-selection')['scope']['operation_grant']=True;self.reject()
 def test_python_normative_changed_rejected(self):self.member('query-implementation-selection')['scope']['Python_normative']=False;self.reject()
 def test_Rust_acceleration_inferred_rejected(self):self.member('query-implementation-selection')['scope']['Rust_graph_acceleration_selected']=True;self.reject()
 def test_signed_genesis_inferred_rejected(self):self.member('query-implementation-selection')['scope']['governed_genesis']='owner signed';self.reject()
 def test_current_Lesson_permission_inferred_rejected(self):self.member('operational-evidence-selection')['scope']['current_application_permission']=True;self.reject()
 def test_evidence_generalized_rejected(self):self.member('operational-evidence-selection')['scope']['general_causal_efficacy_claim']=True;self.reject()
 def test_unknown_root_field_rejected(self):self.value['blanket_authority']=True;self.reject()
 def test_unknown_member_field_rejected(self):self.member('metadata-carrier-admission')['owner_approval']='yes';self.reject()
 def test_effect_description_widened_rejected(self):self.member('private-source-use-policy')['requested_effect']='Execute all original source files';self.reject()
 def test_scope_exclusion_drop_rejected(self):self.member('metadata-carrier-admission')['exclusions'].pop();self.reject()
 def test_invalidation_rule_drop_rejected(self):self.member('representation-adoption-intent')['invalidation'].pop();self.reject()
 def test_target_hash_changed_rejected(self):self.member('metadata-carrier-admission')['targets'][0]['sha256']='0'*64;self.reject()
 def test_absolute_target_path_rejected(self):self.member('metadata-carrier-admission')['targets'][0]['path']='/tmp/outside';self.reject()
 def test_parent_path_escape_rejected(self):self.member('metadata-carrier-admission')['targets'][0]['path']='../outside';self.reject()
 def test_context_pin_changed_rejected(self):self.value['source_context_binding']['sha256']='0'*64;self.reject()
 def test_prerequisite_pin_changed_rejected(self):self.value['prerequisite_bindings']['O03']['sha256']='0'*64;self.reject()
 def test_query_gap_binding_changed_rejected(self):self.value['query_gap_binding']['sha256']='0'*64;self.reject()
 def test_missing_original_replaced_rejected(self):self.reject_file('proposals/source-dispositions.json',lambda v:v['items'].__setitem__(0,dict(v['items'][0],disposition='imported-current-replacement')))
 def test_disposition_omission_rejected(self):self.reject_file('proposals/source-dispositions.json',lambda v:v['items'].pop())
 def test_exclusion_omission_rejected(self):self.reject_file('proposals/source-dispositions.json',lambda v:v['excluded_packages'].pop())
 def test_deferred_epoch_collapse_rejected(self):self.reject_file('proposals/source-dispositions.json',lambda v:v.__setitem__('deferred_source_epoch',{}))
 def test_private_body_import_rejected(self):self.reject_file('proposals/private-source-use.json',lambda v:v.__setitem__('body_import',True))
 def test_private_body_public_export_rejected(self):self.reject_file('proposals/private-source-use.json',lambda v:v.__setitem__('public_export',True))
 def test_private_memory_export_rejected(self):self.reject_file('proposals/private-source-use.json',lambda v:v.__setitem__('secrets_or_Session_memory_allowed',True))
 def test_read_policy_as_current_permission_rejected(self):self.reject_file('proposals/private-source-use.json',lambda v:v.__setitem__('current_operation_authority_required',False))
 def test_positive_confidence_invented_rejected(self):self.reject_file('proposals/unknown-confidence.json',lambda v:v['allowed_levels'].append('high'))
 def test_query_residue_omission_rejected(self):self.reject_file('proposals/query-coverage-and-gap-selection.json',lambda v:v.pop('historical-D73'))
 def test_predecessor_governance_relabel_rejected(self):
  p=next((self.mutable/'proposals/adoption').iterdir());self.reject_file(p.relative_to(self.mutable),lambda v:v['consequence_rule'].__setitem__('old_candidate_event_relabeling_allowed',True))
 def test_semantic_event_digest_changed_rejected(self):
  p=next((self.mutable/'proposals/adoption').iterdir());self.reject_file(p.relative_to(self.mutable),lambda v:v['semantic_tuple'].__setitem__('semantic_event_digest','0'*64))
 def test_adoption_confidence_boost_rejected(self):
  p=next((self.mutable/'proposals/adoption').iterdir());self.reject_file(p.relative_to(self.mutable),lambda v:v['consequence_rule'].__setitem__('evidence_confidence','high'))
 def test_adoption_fixture_owner_outcome_rejected(self):
  p=next((self.mutable/'proposals/adoption').iterdir());self.reject_file(p.relative_to(self.mutable),lambda v:v.__setitem__('actual_owner_outcome','admitted'))
 def test_source_byte_mutation_detected(self):
  p=self.mutable/'source-guard-fixture';p.write_bytes(b'original');b=binding(p);p.write_bytes(b'changed')
  try:
   with self.assertRaises(ValueError):bound(b)
  finally:p.unlink()
 def test_extra_private_body_file_rejected(self):
  p=self.mutable/'unselected-private-body';p.write_bytes(b'owned harmless guard fixture')
  try:
   with self.assertRaises(ValueError):validate(self.fixture_value,self.mutable)
  finally:p.unlink()
 def test_extra_symlink_rejected(self):
  p=self.mutable/'unselected-link';p.symlink_to(self.mutable/'preparation.json')
  try:
   with self.assertRaises(ValueError):validate(self.fixture_value,self.mutable)
  finally:p.unlink()
 def test_build_overwrite_rejected(self):
  with self.assertRaises(ValueError):build(self.output)
 def test_duplicate_json_keys_rejected(self):
  with self.assertRaises(ValueError):parse(b'{"authority_effect":"none","authority_effect":"admit"}')
 def test_nonfinite_json_rejected(self):
  with self.assertRaises(ValueError):parse(b'{"authority":NaN}')

# Each declared field/axis is independently observed in the actual unittest log.
def root_negative(field,value):
 def test(self):self.value[field]=value;self.reject()
 return test
for field,value in [('actual_owner_outcome','admitted'),('selected_outcome','accepted'),('actual_answering_principal_ref','principal:fixture'),
 ('current_owner_authority_verified',True),('authority_effect','admit'),('complete_final_package',True),('canonical_effects_applied',1),
 ('local_transactions_applied',1),('ontology_events_appended',1),('source_retirements',1),('runtime_activation',True),('human_pilot',True),
 ('private_body_exports',1),('Session_memory_exports',1)]:setattr(ReviewGuards,'test_'+field+'_inference_rejected',root_negative(field,value))
def axis_negative(axis):
 def test(self):self.member('metadata-carrier-admission')['requested_axes'][axis]=True;self.reject()
 return test
for axis in DENIED:setattr(ReviewGuards,'test_excluded_axis_'+axis+'_rejected',axis_negative(axis))

if __name__=='__main__':unittest.main()
