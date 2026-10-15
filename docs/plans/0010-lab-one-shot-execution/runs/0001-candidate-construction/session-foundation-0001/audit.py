"""Independent byte, environment, source, custody transcript and scope audit."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
PACKAGE=ROOT/'implementation/lab-continuity/candidates/v2'
PARENT=ROOT/'product/lab/release-candidates/v1/interface/api-v12/receipts/R03-0008.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_bytes())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()

def main():
    checks=[]
    def check(value,name):
        if not value:raise ValueError(name)
        checks.append({'test':name,'result':'PASS'})
    for name in ['source-manifest.json','derived-manifest.json']:
        for row in load(PACKAGE/name)['files']:
            p=ROOT/row['path']
            check(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==row['sha256'],'exact '+row['path'])
    m=load(PACKAGE/'packages/0001/generator-manifest.json')
    check(sha((PACKAGE/'packages/0001/generator-manifest.json').read_bytes())=='4dd5907dc1269e2b0f15a217cd1e60a277554b69889ea76f1e2e571e3fd3010e','independent selected generator pin')
    check(m['environment']['python']==platform.python_version(),'selected Python environment')
    for name,version in m['environment']['packages'].items():check(importlib.metadata.version(name)==version,'selected '+name+' environment')
    check(m['environment']['packages']['jsonschema']=='4.23.0','selected R02 schema validator environment')
    check(m['implementation_version_ref']=='implementation:lab-committed-context-generator@candidate.2','new exact candidate Implementation revision')
    check(m['authority_effect']=='none','candidate generator has no authority effect')
    check(load(HERE/'build-terminal.json')['exit_code']==0,'actual generator build terminal')
    terminal=load(HERE/'tests-terminal.json')
    check(terminal['result']=='PASS' and terminal['tests_run']==25 and terminal['failures']==terminal['errors']==0,'complete selected integration/custody test terminal')
    process=load(HERE/'successor-0002/process-result.json')
    check(process['result']=='PASS' and process['actual_process_interruptions']==1 and process['API_calls_executed']==0,'actual custody process proof distinct from API claim')
    check(len(process['children'])==3 and [r['exit_code'] for r in process['children']]==[-9,0,0],'all three actual child terminals, including observed kill')
    check(process['owned_fixture_roots_removed'] and not process['Session_memory_exported'],'owned fixture cleanup and Session privacy observation')
    metadata=process['metadata'];scope=metadata['scope.json']
    check(scope['assignment_authority']=='unresolved' and scope['action_permission']=='none' and scope['authority_effect']=='none','unassigned read scope is never Agent permission')
    check(set(scope)=={'schema_version','principal_ref','scope_ref','source_cut_binding','consumer_control_binding','action_permission','assignment_authority','authority_effect','actual_owner_outcome'},'closed custody scope declaration')
    events={};allocations={};identity=set()
    for name,row in metadata.items():
        if name=='scope.json':continue
        if name.startswith('allocation-'):allocations[row['key_digest']]=(name,row);continue
        check(set(row)=={'schema_version','key_digest','sequence','previous_binding','session_ref','agent_instance_ref','principal_ref','scope_ref','source_cut_binding','posture','opened_at','ended_at','context_pack_digest','disposal_observed','authority_effect','assignment_authority','action_permission','short_memory_persisted','unresolved_action_refs'},'closed metadata keys '+name)
        check(row['short_memory_persisted'] is False and row['unresolved_action_refs']==[] and row['action_permission']=='none','metadata excludes Session memory and actions '+name)
        events.setdefault(row['key_digest'],[]).append((name,row))
    for key,rows in events.items():
        rows.sort(key=lambda r:r[1]['sequence']);name,allocation=allocations[key]
        previous={'ref':name,'sha256':sha(encoded(allocation))}
        check(rows[0][1]['session_ref'] not in identity,'fresh separate Session identity '+key);identity.add(rows[0][1]['session_ref'])
        for index,(name,row) in enumerate(rows):
            check(row['sequence']==index and row['previous_binding']==previous,'exact immutable metadata chain '+name)
            previous={'ref':name,'sha256':sha(encoded(row))}
    seen_active=[];seen_indeterminate=[];seen_closed=[]
    for frame in process['frames']:
        if frame['kind']!='result' or frame['operation']=='note':continue
        row=frame['result'];b=row['metadata_binding']
        check(b['ref'] in metadata and sha(encoded(metadata[b['ref']]))==b['sha256'],'exact original metadata frame binding '+frame['operation'])
        check(row['short_memory_in_response'] is False and row['assignment_authority']=='unresolved','inspection excludes memory and authority '+frame['operation'])
        if row['posture']=='active':seen_active.append(row)
        if row['posture']=='indeterminate':seen_indeterminate.append(row)
        if row['posture']=='closed':seen_closed.append(row)
    check(len({r['agent_instance_ref'] for r in seen_active})==2,'two fresh actual Machine instances')
    check(seen_indeterminate and all(not r['disposal_observed'] and r['ended_at'] is None for r in seen_indeterminate),'lost live process is never recorded as disposed')
    check(seen_closed and all(r['disposal_observed'] and r['ended_at'] for r in seen_closed),'verified disposal receipt remains visible cold')
    check(sha(PARENT.read_bytes())=='1b585859b300e5bb4e8087abbd5b23a233647aa47be15b096a17752513f111b4','previous real API evidence unchanged')
    for b in load(PARENT)['files']:check(sha((ROOT/b['path']).read_bytes())==b['sha256'],'retained predecessor '+b['path'])
    value={'schema_version':'lab-read-custody-independent-audit/v1-candidate','result':'PASS','checks':checks,
        'checks_count':len(checks),'authority_effect':'none','actual_owner_outcome':None,'API_operations_added':0,
        'claim_ceiling':'Exact source/environment and real read consumer observations; fresh assignment authority and full API Session integration remain R03.'}
    out=HERE/'audit-result.json'
    if out.exists():raise ValueError('audit evidence already exists')
    out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'result':'PASS','checks':len(checks)}),flush=True)

if __name__=='__main__':main()
