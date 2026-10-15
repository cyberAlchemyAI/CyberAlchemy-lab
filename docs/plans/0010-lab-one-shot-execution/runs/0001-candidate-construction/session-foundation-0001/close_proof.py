"""Close scoped observations only after all selected producers actually finish."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
PACKAGE=ROOT/'implementation/lab-continuity/candidates/v2'
PARENT=ROOT/'product/lab/release-candidates/v1/interface/api-v12/receipts/R03-0008.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_bytes())
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def require(value,message):
    if not value:raise ValueError(message)

def main():
    require(sha(PARENT.read_bytes())=='1b585859b300e5bb4e8087abbd5b23a233647aa47be15b096a17752513f111b4','parent evidence differs')
    parent=load(PARENT)
    tests=load(HERE/'tests-terminal.json');process=load(HERE/'successor-0003/process-result.json');audit=load(HERE/'audit-result.json')
    require(tests['result']==process['result']==audit['result']=='PASS','scoped validation incomplete')
    require(tests['tests_run']==25 and len(process['children'])==3 and process['actual_process_interruptions']==1,'selected observation scope differs')
    require(load(HERE/'tests-tool-terminal.json')['exit_code']==0 and load(HERE/'successor-0003/process-terminal.json')['exit_code']==0,'actual selected producer terminal absent')
    files={}
    def add(row):
        b={'path':row['path'],'sha256':row['sha256']};p=ROOT/b['path']
        require(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==b['sha256'],'evidence byte drift '+b['path'])
        require(b['path'] not in files or files[b['path']]==b,'contradictory binding')
        files[b['path']]=b
    for row in parent['files']:add(row)
    add(binding(PARENT))
    for name in ['source-manifest.json','derived-manifest.json']:
        add(binding(PACKAGE/name))
        for row in load(PACKAGE/name)['files']:add(row)
    # Retain all actual failed controllers. Exclude the currently running closer.
    for tree in [HERE,PACKAGE]:
        for path in sorted(tree.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:continue
            if path.name in ['close.stdout','close.stderr','R03-0009.json']:continue
            add(binding(path))
    supported=parent['supported_operations'];remaining=parent['remaining_operations']
    require(len(supported)==7 and len(remaining)==27,'original API scope narrowed')
    receipt={**{k:v for k,v in parent.items() if k not in ['files','checks','recorded_at','claim_ceiling','observed_checks']},
        'schema_version':'lab-R03-context-custody-foundation-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'parent_binding':binding(PARENT),'selected_context_root':PACKAGE.relative_to(ROOT).as_posix(),
        'selected_generator_binding':binding(PACKAGE/'packages/0001/generator-manifest.json'),
        'read_custody_protocol_binding':binding(PACKAGE/'custody.py'),'context_design_binding':binding(PACKAGE/'DESIGN.md'),
        'context_foundation_tests':25,'context_process_checks':len(process['checks']),'context_independent_audit_checks':len(audit['checks']),
        'context_terminal_real_processes':3,'context_actual_process_interruptions':1,'context_API_operations_added':0,
        'actual_process_read_consumers_created':2,'read_consumer_assignment_authority':'unresolved','active_Agent_Sessions_created':0,
        'checks':[*parent['checks'],{'suite':'selected-environment-context-and-read-custody','test_count':25,'result':'PASS'},*process['checks'],*audit['checks']],
        'observed_checks':parent['observed_checks']+25+len(process['checks'])+len(audit['checks']),
        'Session_memory_exported':False,'actual_owner_outcome':None,'human_pilot_outcome':None,'authority_effect':'none','goal_complete':False,
        'remaining_obligations':parent['remaining_obligations'],
        'claim_ceiling':'Partial candidate API evidence plus exact selected-environment signed Project State/native context and unassigned read consumer custody. Fresh assignment/capability/authority and full API Session contracts remain R03; no admission, human pilot or complete plan.',
        'files':sorted(files.values(),key=lambda b:b['path']),'recorded_at':datetime.now(timezone.utc).isoformat()}
    destination=PACKAGE/'receipts';destination.mkdir(exist_ok=True);out=destination/'R03-0009.json'
    require(not out.exists(),'scoped receipt already exists');out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'PASS','task_complete':False,'receipt':binding(out),'new_API_operations':0,'files':len(files)}),flush=True)

if __name__=='__main__':main()
