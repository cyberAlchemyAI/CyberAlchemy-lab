"""Check actual exact payload/protected dispositions and native restore evidence."""
import argparse,datetime,json
from pathlib import Path
from jsonschema import Draft202012Validator
import build as B

def run(pin):
 source=B.frozen(pin);root=B.ROOT;here=B.HERE
 dispositions=B.load(here/'dependency-dispositions.json');selection=B.load(here/'payload-selection.json');prior=B.load(here/'prior-exclusions.json');native=B.load(here/'native-remediation.json');blocked=B.load(here/'runtime-blockers.json')
 a,p,s=B.check_api_controls();actual={r['path']:r for r in a['files']};rows={r['path']:r for r in dispositions['rows']};validator=Draft202012Validator(B.load(here/'disposition.schema.json'))
 checks={}
 checks['all_actual_API12_source_rows_accounted_exactly']=len(rows)==len(actual)==len(dispositions['rows']) and all(rows[k]['sha256']==v['sha256'] for k,v in actual.items())
 checks['all_profile_and_schema_dependencies_accounted']=all(x['path'] in rows and rows[x['path']]['sha256']==x['sha256'] for x in p['files']+s['files'])
 checks['all_disposition_rows_conform']=all(validator.is_valid(x) for x in rows.values())
 checks['all_original95_and_additional17_exclusions_preserved']=prior['original95']==95 and prior['additional17']==17 and len(prior['rows'])==112 and all(rows[x['path']]['disposition']=='protected-prior-exclusion' and not rows[x['path']]['public_payload_proposed'] and rows[x['path']]['sha256']==x['sha256'] for x in prior['rows'])
 decoded=B.C.payload(B.C.read(here/'public-payload.snapshot'));selected={r['path']:r for r in selection['payload_files']}
 checks['public_payload_exact_member_and_byte_closure']=set(decoded)==set(selected)=={k for k,v in rows.items() if v['public_payload_proposed']} and all(B.C.sha(v)==selected[k]['sha256']==actual[k]['sha256'] and B.C.read(root/k)==v for k,v in decoded.items())
 checks['public_payload_has_no_inspector_private_fields_or_refusals']=all(not B.R.scan(v,k) for k,v in decoded.items())
 checks['protected_archives_and_test_cache_log_bodies_excluded']=all(not v['public_payload_proposed'] for v in rows.values() if v['disposition']!='candidate-public-code-schema-package')
 checks['native_exact_selected_hash_and_signed_locator_unchanged']=B.bind(B.NATIVE)['sha256']==B.NATIVE_SHA and native['original_binding']==B.bind(B.NATIVE) and native['signed_tmp_locator_changed'] is False
 n=B.C.payload(B.C.read(here/'protected-native-dependency.snapshot'));checks['native_protected_archive_keeps_original_bytes']=n['native/lab-context-native-reader']==B.C.read(B.NATIVE) and native['protected_archive_binding']==B.bind(here/'protected-native-dependency.snapshot')
 checks['actual_native_restore_and_retry_keep_nonexecutable_mode']=native['actual_original_bytes_equal'] and native['actual_restored_mode']=='0o600' and native['actual_exact_retry_observation']['idempotent'] and not native['native_executed'] and not native['native_executable_install_qualified']
 checks['all_omitted_schema_guard_dependencies_explicit']=set(x['path'] for x in selection['schema_execution_inputs_outside_public_payload'])=={x['path'] for x in s['files'] if x['path'] not in decoded}
 checks['proof_rows_retained_and_public_runtime_blockers_honest']=dispositions['source_proof_rows_removed']==0 and blocked['original_proof_rows_removed']==0 and not selection['public_payload_self_contained'] and not blocked['R06_complete'] and not native['locator_or_ABI_blocker_resolved']
 B.frozen(pin);passed=all(checks.values());report={'schema_version':'lab-R06-API12-candidate-payload-conformance/v1-candidate','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS-candidate-preparation' if passed else 'FAIL','checks':checks,'source_binding':B.bind(here/'source-manifest.json'),'api_source_binding':B.bind(B.API/'source-manifest.json'),'api_profile_binding':B.bind(B.API/'contract-profile.json'),'source_files_accounted':len(rows),'public_payload_files':len(decoded),'prior_exclusions':112,'original_source_rows_removed':0,'private_values_disclosed':False,'public_export_authorized':False,'native_executable_install_qualified':False,'public_payload_self_contained':False,'R06_complete':False,'task_complete':False,'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False}
 (here/'receipts').mkdir(mode=0o700);B.put(here/'receipts/conformance-0001.json',report)
 full={r['path']:r for r in source['files']}
 for q in [here/'source-manifest.json',*here.glob('*.json'),here/'public-payload.snapshot',here/'protected-native-dependency.snapshot',here/'receipts/conformance-0001.json']:
  full[B.bind(q)['path']]=B.bind(q)
 B.put(here/'receipts/proof-0001.json',{'schema_version':'lab-R06-API12-candidate-payload-proof/v1-candidate','result':report['result'],'files':[full[k] for k in sorted(full)],'conformance_binding':B.bind(here/'receipts/conformance-0001.json'),'payload_binding':B.bind(here/'public-payload.snapshot'),'native_archive_binding':B.bind(here/'protected-native-dependency.snapshot'),'all_original_proof_rows_retained':True,'candidate_preparation_only':True,'actual_private_scratch_restore_observed':True,'public_export_authorized':False,'public_payload_self_contained':False,'R06_complete':False,'task_complete':False,'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False})
 print(json.dumps({'result':report['result'],'checks':checks,'conformance_binding':B.bind(here/'receipts/conformance-0001.json'),'proof_binding':B.bind(here/'receipts/proof-0001.json')}),flush=True)
 raise SystemExit(0 if passed else 1)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);run(parser.parse_args().source_sha256)
