"""Independent exact read-only validation; preserve prior check exit143 as observed."""
import argparse,collections,datetime,json,stat
from pathlib import Path
import build as B
P=Path(__file__).resolve()

def run(args):
 assert B.bind(P)['sha256']==args.verifier_sha256
 source=B.frozen(args.source_sha256);here=B.HERE;root=B.ROOT
 proof_path=here/'receipts/proof-0001.json';conformance_path=here/'receipts/conformance-0001.json';terminal=B.RUN/'R06-api12-selection-terminal-0173.json'
 assert B.bind(proof_path)['sha256']==args.proof_sha256 and B.bind(conformance_path)['sha256']==args.conformance_sha256 and B.bind(terminal)['sha256']==args.prior_terminal_sha256
 controls=[P,here/'source-manifest.json',proof_path,conformance_path,terminal,B.RUN/'ARE-R06-terminal-verification-boundary-0192.json']
 before={str(p):B.bind(p) for p in controls};proof=B.load(proof_path);original_report=B.load(conformance_path);previous=B.load(terminal)
 assert previous['proposal_actual_exit_code']==0 and previous['conformance_actual_exit_code']==143 and not previous['conformance_clean_terminal_observed']
 assert original_report['result']==proof['result']=='PASS-candidate-preparation' and len(original_report['checks'])==14 and all(original_report['checks'].values())
 for row in proof['files']:assert B.bind(root/row['path'])==row,row['path']
 actual,profile,runtime=B.check_api_controls();ledger=B.load(here/'dependency-dispositions.json');rows={r['path']:r for r in ledger['rows']};expected={r['path']:r for r in actual['files']}
 assert len(rows)==len(ledger['rows'])==len(expected)==23062 and all(rows[k]['sha256']==v['sha256'] for k,v in expected.items())
 assert all(rows[r['path']]['sha256']==r['sha256'] for r in profile['files']+runtime['files'])
 selection=B.load(here/'payload-selection.json');raw=B.C.read(here/'public-payload.snapshot');assert B.bind(here/'public-payload.snapshot')==selection['payload_binding'];payload=B.C.payload(raw);members={r['path']:r for r in selection['payload_files']}
 assert len(payload)==len(members)==909 and set(payload)==set(members)=={k for k,v in rows.items() if v['public_payload_proposed']}
 for name,body in payload.items():
  assert B.C.sha(body)==members[name]['sha256']==expected[name]['sha256'] and B.C.read(root/name)==body
  assert not B.R.scan(body,name)
 excluded=B.load(here/'prior-exclusions.json');assert len(excluded['rows'])==112 and excluded['original95']==95 and excluded['additional17']==17
 assert all(rows[r['path']]['sha256']==r['sha256'] and not rows[r['path']]['public_payload_proposed'] for r in excluded['rows'])
 migration=B.load(here/'migration-dispositions.json');original_migration=B.load(root/'implementation/lab-ontology/candidates/v1/migration/source-selection.json');items=[r for r in original_migration['items'] if not r['public_body_export_allowed']]
 assert migration['original_items']==items and len(items)==140 and sum(r['source_binding'] is None for r in items)==9
 assert collections.Counter(r['privacy'] for r in items)=={'private':138,'public-scoped-source':2}
 native=B.load(here/'native-remediation.json');host=B.bind(B.NATIVE);assert host['sha256']==B.NATIVE_SHA and native['original_binding']==native['host_provided_native_binding']==host
 archive=B.C.payload(B.C.read(here/'protected-native-dependency.snapshot'));assert archive['native/lab-context-native-reader']==B.C.read(B.NATIVE)
 assert stat.S_IMODE(B.NATIVE.stat().st_mode)==0o755 and native['host_provided_native_mode']=='0o755' and native['actual_restored_mode']=='0o600' and native['actual_exact_retry_observation']['idempotent'] and not native['native_executed']
 assert native['selected_environment']==native['expected_R02_environment']==B.C.environment() and native['selected_local_host_dependency_satisfied']
 for row in native['host_ABI_library_bindings']:assert B.bind(Path(row['path']))==row
 for row in proof['files']:assert B.bind(root/row['path'])==row,row['path']
 B.frozen(args.source_sha256);assert all(B.bind(Path(k))==v for k,v in before.items())
 report={'schema_version':'lab-R06-independent-terminal-verification/v1-candidate','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS-independent-read-only-closure','independently_pinned_verifier_binding':B.bind(P),'source_bindings':list(before.values()),'prior_exit143_retained':True,'prior_PASS_report_and_proof_bytes_unchanged':True,'original23062_API12_dependencies_accounted':True,'actual909_public_payload_members_verified':True,'actual112_prior_exclusions_verified':True,'actual140_original_migration_records_including9_null_bindings_verified':True,'native_original_bytes_and_0755_host_dependency_verified':True,'actual_archive_restore_evidence_remains_nonexecutable_0600':True,'full_immutable_proof_entry_exit_guards_completed':True,'host_ABI_and_R02_environment_exact_current_bindings_verified':True,'originals_or_permissions_changed':False,'public_export_authorized':False,'native_executed':False,'portable_runtime_required':False,'complete_API_or_installation_scenarios_qualified':False,'R06_complete':False,'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False}
 out=here/'receipts/terminal-verification-0001.json';B.put(out,report)
 print(json.dumps({'result':report['result'],'report_binding':B.bind(out),'verifier_binding':B.bind(P)}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ['verifier-sha256','source-sha256','proof-sha256','conformance-sha256','prior-terminal-sha256']:p.add_argument('--'+name,required=True)
 run(p.parse_args())
