"""Coordinator metadata acceptance of the observed T06 startup; no runtime replay."""
import fcntl, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).absolute().parents[6]
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
T06=RUN/'T06'
checked=[]
def exact(path,sha256):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    raw=p.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha256,str(p)
    checked.append({'path':str(p.relative_to(ROOT)),'sha256':sha256})
    return json.loads(raw) if p.suffix=='.json' else raw

terminal=exact(T06/'branch-fixtures-0001/actual-terminal-0001.json','c5b7e1224110e807bbf947ad7af9ebbda0a2fff738024a0277358c169829f29b')
attempt=exact(**terminal['actual_report_binding'])
postcheck=exact(**terminal['postcheck_binding'])
for row in terminal['observation_code_bindings']:exact(**row)
for obj in (terminal,attempt,postcheck):
    assert obj['authority_effect']=='none' and obj['actual_owner_outcome'] is None
    assert obj['task_complete'] is False and obj['whole_API_qualified'] is False
assert terminal['dispatch_operations_executed']==0
assert terminal['outer_process_exit_code']==terminal['SDK_child_exit_code']==0
assert terminal['actual_catalog_operation_count']==34 and terminal['actual_composition']=='Base28+Action3+Governance3'
assert attempt['SDK_result']['process_exit_code']==0 and attempt['SDK_result']['dispatch_operations_executed']==0
assert attempt['elapsed_seconds']<terminal['startup_seconds_limit']==300
assert attempt['same_preparation_Schemas_instance'] and attempt['original_preparation_lease_closed']
for field in ('dependencies_entry','dependencies_exit'):assert attempt[field]['status']=='PASS' and attempt[field]['installed_files']==1010
assert attempt['source_exit']=={'current_files':27080,'historical_physical_closure':'REFUSED','status':'PASS'}
for key,value in postcheck['checks'].items():
    assert value is True or key=='dispatch_operations_executed' and value==0 or key=='actual_fixed_startup_budget_seconds' and value==300,key

source=exact(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json',terminal['selected_source_sha256'])
exact(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/contract-profile.json',terminal['selected_profile_sha256'])
members={(x['path'],x['sha256']) for x in source['files']}
assert len(source['files'])==27080
for path,pin in (
 ('product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/source-manifest.json',terminal['frozen_SDK_source_sha256']),
 ('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-0001/revision-0003/driver-selection.json',terminal['frozen_driver_selection_sha256']),
):
    selection=exact(path,pin)
    for row in selection['files']:
        exact(row['path'],row['sha256'])
        assert (row['path'],row['sha256']) in members,row['path']
for row in terminal['observation_code_bindings']:
    assert (row['path'],row['sha256']) not in members
with (RUN/'lease-sensitive-runtime.lock').open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    fcntl.flock(lock,fcntl.LOCK_UN)

receipt={
 'schema_version':'lab-T06-root-startup-acceptance/v1-candidate',
 'status':'ACCEPT-scoped-startup-only', 'authority_effect':'none', 'task_complete':False,
 'whole_API_qualified':False,'actual_owner_outcome':None,
 'accepted_evidence':terminal['actual_report_binding'],
 'checked_bindings':checked, 'actual_catalog_operation_count':34,
 'dispatch_operations_executed':0,'source_rows':27080,'installed_rows':1010,
 'runtime_slot_free_at_acceptance':True,
 'observer_origins_in_source2':False,
 'claim_ceiling':'Observed original three-branch authentication, shared Schemas, actual sealed SDK child fresh Action lease handoff and normal exit only; observation harness outside source2 prevents whole observed-software closure. No dispatcher operation, human/governing authority, or final qualification.',
 'checked_at':datetime.now(timezone.utc).isoformat(),
}
out=T06/'root-startup-acceptance-0001.json'
with out.open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':receipt['status'],'bindings':len(checked),'path':str(out)}))
