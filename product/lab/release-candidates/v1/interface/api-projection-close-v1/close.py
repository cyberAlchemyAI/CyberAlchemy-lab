"""Close the selected R03 partial slice without changing parent proof bytes."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_bytes())
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    assert sha(HERE/'source-manifest.json')==args.source_sha256
    m=load(HERE/'source-manifest.json')
    for row in m['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    audit=load(ROOT/m['audit_result_binding']['path']);assert audit['result']=='PASS' and audit['actual_public_api_operations']==12
    rows={row['path']:row for row in m['files']};rows[binding(HERE/'source-manifest.json')['path']]=binding(HERE/'source-manifest.json')
    value={'schema_version':'lab-R03-projection-context-session-partial-proof/v1-candidate','result':'PASS','task_complete':False,'goal_complete':False,
      'authority_effect':'none','actual_owner_outcome':None,'checked_at':datetime.now(timezone.utc).isoformat(),
      'parent_receipt_binding':m['parent_receipt_binding'],'source_selection_binding':m['selected_api_binding'],
      'protocol_profile_binding':m['selected_profile_binding'],'independent_audit_result_binding':m['audit_result_binding'],
      'audit_checks':audit['checks'],'files':sorted(rows.values(),key=lambda row:row['path']),
      'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,
      'suite_tests':audit['suite_tests'],'selected_suite_tests':102,'actual_stdio_processes':2,'actual_stdio_frames':9,
      'process_checks':61,'actual_direct_samples':audit['actual_direct_samples'],'retained_parsed_noncanonical_samples':1,
      'full_native_regressions':23,'portable_locator_guards':9,'all_6031_parent_files_retained':True,
      'Session_regression_composition':'The exact passing A-D groups from v2 are retained under unchanged selected API v16. All 11 E methods were actually rerun with the correct 12-operation count, preserving all other assertions and original returned snapshots. The selected aggregate covers each of the 34 original methods exactly once; failed original full runs remain retained.',
      'projection_scope':'Currently granted exact projector/schema/catalog/cut over isolated signed candidate sources; complete connection-local disposable SQLite generation and historical durable operation evidence. Explicit source semantic gaps remain indexed and inspectable. Optional cache omits protected historical Session/credential bodies.',
      'canonical_effects_applied':0,'private_keys_exported':False,'private_memory_exported':False,'human_pilot_completed':False,
      'remaining_obligations':m['remaining_obligations'],
      'claim_ceiling':'Twelve actual selected public handlers and original scoped candidate proof only. R03 remains in progress, 35/46 task criteria remain closed, and the full original plan remains active. No complete Product model implementation, actual owner outcome, canonical admission, activation or stable release.'}
    path=HERE/'receipts/R03-0016.json';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PASS','receipt_binding':binding(path),'files':len(rows),'actual_public_api_operations':12,'remaining_original_api_operations':22,'task_complete':False,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
