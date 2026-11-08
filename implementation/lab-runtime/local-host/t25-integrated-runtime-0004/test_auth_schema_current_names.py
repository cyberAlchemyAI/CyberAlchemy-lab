"""Real Draft2020-12 checks for current-name schema migration/oneOf boundaries."""
import copy,importlib.util,json,sys,unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,'/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001/deps')
from jsonschema import Draft202012Validator,FormatChecker
spec=importlib.util.spec_from_file_location('_cal_current_schema_patch',HERE/'auth_schema_current_names.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
OLD=json.loads((ROOT/'product/lab/release-candidates/v1/interface/api-integration-v74-portable-inputs-0001/authentication.schema.json').read_bytes());NEW,CHANGES=M.apply(OLD)
def metadata(source_name):
 row=next(r for r in NEW['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-metadata-candidate-policy/v1-candidate');binding=row['properties']['development_authorization_binding']['properties']
 return {'schema_version':'lab-local-metadata-candidate-policy/v1-candidate','principal_ref':'principal:independent-test','reader_public_key':'A'*44,'host_uid':1000,'source_name':source_name,'scope_refs':['project:cyberalchemy-v2-to-lab-migration'],'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'max_request_bytes':65536,'max_response_bytes':1048576,'max_calls':128,'allowed_operations':copy.deepcopy(row['properties']['allowed_operations']['const']),'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,'workspace':{'root':'/tmp/owned-test/workspace','manifest_sha256':'a'*64,'max_actions':64},'session_control':None,'projection_control':None,'purpose':row['properties']['purpose']['const'],'development_authorization_binding':{k:v['const'] for k,v in binding.items()},'scope_control':None}
class Names(unittest.TestCase):
 def test_all_non_source_name_constraints_exact(self):
  a=copy.deepcopy(OLD);b=copy.deepcopy(NEW)
  for value in (a,b):
   for row in value['oneOf']:row.get('properties',{}).pop('source_name',None)
  self.assertEqual(a,b)
 def test_current_metadata_policy_matches_exactly_one_real_variant(self):
  for name in ('custody-participation','completion-legacy:legacy-local-4636eca980a5d94d','completion-legacy:legacy-local-ffffffffffffffff'):
   policy=metadata(name);self.assertTrue(Draft202012Validator(NEW,format_checker=FormatChecker()).is_valid(policy));self.assertEqual(sum(Draft202012Validator(row,format_checker=FormatChecker()).is_valid(policy) for row in NEW['oneOf']),1)
 def test_metadata_unknown_names_and_extras_refuse(self):
  for name in ('completion-legacy:../escaped','completion-legacy:','unselected-other-profile'):
   self.assertFalse(Draft202012Validator(NEW).is_valid(metadata(name)))
  policy=metadata('completion-legacy:legacy-local-ffffffffffffffff');policy['wire_profile_authority']='forged';self.assertFalse(Draft202012Validator(NEW).is_valid(policy))
 def test_integrated_history_selectors_stay_exact(self):
  for before,after in zip(OLD['oneOf'],NEW['oneOf']):
   tag=before.get('properties',{}).get('schema_version',{}).get('const','')
   if 'integrated-challenge-resolution' in tag or 'genuine-history' in tag:self.assertEqual(before,after)
 def test_dedicated_lesson_variants_do_not_overlap_legacy_selector(self):
  for tag in ('lab-local-lesson-read-policy/v1-candidate','lab-local-lesson-assessment-policy/v1-candidate','lab-local-lesson-application-policy/v2-candidate','lab-local-challenge-resolution-policy/v1-candidate'):
   rows=[r for r in NEW['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')==tag]
   current=[r for r in rows if Draft202012Validator(r['properties']['source_name']).is_valid('completion-legacy:legacy-local-ffffffffffffffff')]
   self.assertEqual(len(current),1,tag)
 def test_workflow_metadata_only_adds_current_lexical_name(self):
  row=next(r for r in NEW['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-workflow-transition-policy/v1-candidate');v=Draft202012Validator(row['properties']['source_name']);self.assertTrue(v.is_valid('workflow-participation'));self.assertTrue(v.is_valid('completion-legacy:legacy-local-ffffffffffffffff'));self.assertFalse(v.is_valid('integrated-participation'))
if __name__=='__main__':unittest.main()
