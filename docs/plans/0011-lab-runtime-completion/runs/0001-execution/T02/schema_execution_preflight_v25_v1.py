"""Observe the unchanged APIv25 schema execution boundary without a Service."""
import hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pin='c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'
start=datetime.now(timezone.utc).isoformat()
name='_cal_T02_unchanged_APIv25_schema_execution_preflight'
spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
P=__import__(name+'.protocol',fromlist=['Schemas']);schemas=P.Schemas(pin);schemas.guard()
profile=json.loads((API/'contract-profile.json').read_bytes());b={'path':(API/'contract-profile.json').relative_to(ROOT).as_posix(),'sha256':sha(API/'contract-profile.json')};selection={'files':profile['files']}
report={'schema_version':'lab-T02-original-schema-execution-preflight/v1-candidate','result':'PASS-original-Schemas-execution-closure','started_at':start,'ended_at':datetime.now(timezone.utc).isoformat(),'original_profile_sha256':pin,'schema_execution_selection_binding':b,'full_original_schema_execution_row_count':len(selection['files']),'original_protocol_code_sha256':sha(API/'protocol.py'),'original_guard_code_sha256':sha(API/'guard.py'),'original_protocol_or_schema_guard_replaced':False,'vanished_native_in_schema_execution_closure':any('/tmp/cal-R03-mapped-native-build-0002/' in r['path'] for r in selection['files']),'full_API_source_guard_executed':False,'current_source_or_Context_proof_claimed':False,'private_keys_or_live_permissions_created':False,'authority_effect':'none','actual_owner_outcome':None}
with (HERE/'original-v25-schema-execution-preflight-0001.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':report['result'],'schema_execution_rows':len(selection['files'])}),flush=True)
