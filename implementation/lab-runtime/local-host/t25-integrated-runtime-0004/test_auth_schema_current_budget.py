"""Only newly declared current-Legacy fixture policies may request <=3600s."""
import copy,json,sys,unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,'/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001/deps')
from jsonschema import Draft202012Validator,FormatChecker
import auth_schema_current_names as N
import auth_schema_current_budget_0001 as B
OLD=json.loads((ROOT/'product/lab/release-candidates/v1/interface/api-integration-v74-portable-inputs-0001/authentication.schema.json').read_bytes());NAMED,_=N.apply(OLD);NEW,CHANGED=B.apply(NAMED)
def participation(name,seconds):
 row=NEW['oneOf'][0];p=row['properties']
 return {'schema_version':'lab-local-candidate-policy/v4-candidate','principal_ref':'principal:declared-fixture','reader_public_key':'A'*44,'host_uid':1000,'source_name':name,'scope_refs':['project:cyberalchemy-v2-to-lab-migration'],'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'max_request_bytes':65536,'max_response_bytes':1048576,'max_calls':128,'allowed_operations':copy.deepcopy(p['allowed_operations']['const']),'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,'workspace':{'root':'/tmp/owned-fixture/workspace','manifest_sha256':'a'*64,'max_actions':64},'session_control':{'period_binding':{'ref':'declared-period.json','sha256':'b'*64},'max_session_seconds':seconds},'projection_control':None}
class Budget(unittest.TestCase):
 def test_actual_schema_matches_exact_constructed_successor(self):
  self.assertEqual(NEW,json.loads((ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/authentication.schema.json').read_bytes()))
 def test_current_longer_policy_is_exactly_one_variant(self):
  for seconds in (1,900,3600):
   value=participation('completion-legacy:legacy-local-5bd4f03a7076695c',seconds);self.assertTrue(Draft202012Validator(NEW,format_checker=FormatChecker()).is_valid(value));self.assertEqual(sum(Draft202012Validator(row).is_valid(value) for row in NEW['oneOf']),1)
 def test_current_budget_outside_bound_refuses(self):
  for seconds in (0,3601,True):self.assertFalse(Draft202012Validator(NEW).is_valid(participation('completion-legacy:legacy-local-5bd4f03a7076695c',seconds)))
 def test_historical_policy_remains_900(self):
  self.assertTrue(Draft202012Validator(NEW).is_valid(participation('custody-participation',900)));self.assertFalse(Draft202012Validator(NEW).is_valid(participation('custody-participation',901)))
 def test_source8_branches_unchanged(self):
  for before,after in zip(NAMED['oneOf'],NEW['oneOf']):
   if 'completion-current-participation:' in json.dumps(before.get('properties',{}).get('source_name',{})):self.assertEqual(before,after)
 def test_only_reviewed_cap_rows_changed(self):
  self.assertEqual(CHANGED,[35,31,33]);self.assertEqual(len(NEW['oneOf']),len(NAMED['oneOf'])+1)
  for i in range(len(NAMED['oneOf'])):
   if i not in (0,31,33):self.assertEqual(NAMED['oneOf'][i],NEW['oneOf'][i])
if __name__=='__main__':unittest.main()
