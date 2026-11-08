"""Prove preparation separately from actual original-gate completion."""
import argparse
import json
import re
from pathlib import Path
from closure_api import HERE,ROOT,Ledger,read,check,binding,current_sources


def audit(*,prepared=False):
    plan=read(HERE/'execution/plan.json');check(plan['source_plan'])
    proposal=read(check(plan['source_plan']))
    expected={t['id']:t for t in proposal['tasks'] if t['id'].startswith('H')}
    assert set(expected)=={t['id'] for t in plan['tasks']}
    rows=[];refs=[]
    for task in plan['tasks']:
        if task['status']!='accepted':
            rows.append({'task':task['id'],'status':task['status']});continue
        receipt=read(check(task['receipt']))
        assert receipt['task']==task['id'] and receipt['result']=='accepted'
        assert receipt['criteria']==expected[task['id']]['exit_criteria']
        assert all(c['result']=='pass' for c in receipt.get('controls',[]))
        refs+=receipt['artifacts']+receipt['inputs']
        rows.append({'task':task['id'],'status':'accepted-current','receipt':task['receipt']})
    current_sources(refs)
    formal=read(HERE/'execution/h00/formal-evidence.json')
    assert formal['result']=='pass' and formal['theorems']==9
    current_sources([formal[k] for k in ['source','olean','toolchain_lock','compiler','kernel']])
    for record in formal['records']:
        log=check(record['log']).read_text()
        assert record['exit_code']==0 and 'sorryAx' not in log and 'warning:' not in log
        assert len(record['axioms'])==9 and all(set(a)<={'propext','Quot.sound','Classical.choice'} for a in record['axioms'].values())
    ledger=Ledger();view=ledger.resolve()
    for gate in ['R06','G4']:
        ledger.manifest(gate)
    packet=check(read(HERE/'review-challenges.json')['R06'])
    manifest=read(packet)
    links=0
    for key in ['packet']:
        text=check(manifest['artifacts'][key]).read_text()
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if target.startswith(('https://','http://','#')):continue
            assert Path(target).is_absolute() and Path(target).is_file(),target
            links+=1
    if prepared:
        assert all(next(t for t in plan['tasks'] if t['id']==id)['status']=='accepted' for id in ['H00','H01','H02','H04','H03'])
        result='machine-preparation-complete; actual original human gates pending'
    else:
        assert view['counts']=={'tasks':35,'working_units':40,'edges':56,'accepted':35},'original human gates not both accepted'
        assert view['overlay_accepted']==['R06','G4']
        assert all(t['status']=='accepted' for t in plan['tasks'] if t['id']!='H10'),'required closure unit incomplete'
        result='original-plan-complete-with-checked-overlay'
    return {'schema':'relational.gate-closure-completion-audit/v4','result':result,
            'prepared_only':prepared,'original_current_counts':view['counts'],'closure_units':rows,
            'formal_theorems':9,'packet_local_links_checked':links,
            'accepted_artifact_bindings_checked':len(refs),'review_challenges':read(HERE/'review-challenges.json'),
            'fresh_event':False,'authority_effect':'none','application_authorized':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepared',action='store_true');args=parser.parse_args()
    result=audit(prepared=args.prepared)
    name='preparation-audit.json' if args.prepared else 'final-complete-plan-audit.json'
    (HERE/'execution'/name).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='closure_units'},indent=2))
