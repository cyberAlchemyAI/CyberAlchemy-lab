#!/usr/bin/env python3
"""Evaluate stated synthetic outcomes, not real-world efficacy or agent agreement."""
import json, itertools, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def evaluate_case(case, action):
    cid=case['case_id']; a=action['id']; cost=action['cost_units']
    feasible=True; benefit=0; explanation=''
    if cid in ('C01','C02'):
        x=case['context']; summary=x['summary_capacity']; approval=x['approval_capacity']
        if a=='automate': summary*=2 if cid=='C01' else 3
        if a=='delegate': approval+=4
        if a=='remove': feasible=False
        benefit=min(x['arrivals_per_day'],summary,approval)
        explanation=f'completed/day={benefit}; summary_capacity={summary}; approval_capacity={approval}'
    elif cid=='C03':
        benefit=int(a=='ask'); feasible=a=='ask'; explanation='Only asking supplies the missing recipient acceptance information.'
    elif cid=='C04':
        feasible=a in ('direct','investigate'); benefit=int(feasible); explanation='Direct and investigate produce the exact label; cost distinguishes them.'
    elif cid=='C05':
        feasible=a in ('measure','repeat'); benefit=int(a=='measure'); explanation='Separate stage waits distinguish the two hypotheses; total delay alone does not.'
    elif cid=='C06':
        feasible=a=='delegate'; benefit=int(feasible); explanation='Only delegated accountable ownership supplies a feasible improvement under the stipulated assurance rule.'
    elif cid=='C07':
        feasible=a in ('local','report'); benefit=int(a=='local'); explanation='Local sum produces the aggregate without moving rows; report does not produce it.'
    elif cid=='C08':
        feasible=a=='bounded'; benefit=int(feasible); explanation='Only bounded retains the positive toy observation and its transfer limitation with next evidence.'
    elif cid=='C09':
        feasible=a in ('reseat','debate'); benefit=int(feasible); explanation='Both reseat the belt; extra debate costs more without additional stipulated outcome.'
    elif cid=='C10':
        benefit=1; explanation='Coverage is stipulated equal; compare ten-cycle total cost.'
    elif cid=='C11':
        feasible=a=='add_owner'; benefit=int(feasible); explanation='Only add_owner makes the owner available to the declared machine consumer.'
    elif cid=='C12':
        formula={'inverse':lambda p,q:p or not q,'converse':lambda p,q:not q or p,'contrapositive':lambda p,q:q or not p,'negate':lambda p,q:not q}[a]
        counterexamples=[{'P':p,'Q':q} for p,q in itertools.product([False,True],repeat=2) if (not p or q) and not formula(p,q)]
        feasible=not counterexamples; benefit=int(feasible); explanation='Truth-table counterexamples='+json.dumps(counterexamples)
    return {'feasible':feasible,'benefit':benefit,'cost_units':cost,'explanation':explanation}

def run():
    case_doc=json.loads((ROOT/'cases.json').read_text()); cases={x['case_id']:x for x in case_doc['cases']}; oracle={}
    for cid,c in cases.items():
        outcomes={a['id']:evaluate_case(c,a) for a in c['actions']}
        candidates={a:o for a,o in outcomes.items() if o['feasible']}
        best_benefit=max(o['benefit'] for o in candidates.values())
        best_cost=min(o['cost_units'] for o in candidates.values() if o['benefit']==best_benefit)
        best=[a for a,o in candidates.items() if o['benefit']==best_benefit and o['cost_units']==best_cost]
        oracle[cid]={'outcomes':outcomes,'best_actions':best,'method':'constraint feasibility, then stated benefit, then cost tie-break'}
    (ROOT/'scenario-outcomes.json').write_text(json.dumps(oracle,indent=2)+'\n')
    results=[]
    for f in sorted((ROOT/'outputs').glob('*.json')):
        d=json.loads(f.read_text()); decisions=d['decisions']; ids=[x['case_id'] for x in decisions]
        errors=[]
        if len(ids)!=len(set(ids)): errors.append('duplicate case IDs')
        if set(ids)!=set(cases): errors.append('missing or extra case IDs')
        evaluated=[]
        for row in decisions:
            cid=row['case_id']; act=row['chosen_action']
            if cid not in cases or act not in oracle[cid]['outcomes']:
                errors.append(f'invalid selection {cid}:{act}'); continue
            for field in ['causal_rationale','fixed_constraints','rejected_alternative','evidence_limit']:
                if not row.get(field): errors.append(f'{cid}: missing {field}')
            evaluated.append({'case_id':cid,'chosen_action':act,**oracle[cid]['outcomes'][act],'best_under_stipulated_model':act in oracle[cid]['best_actions']})
        results.append({'arm':d['arm'],'output':str(f.relative_to(ROOT)),'output_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'errors':errors,'evaluated':evaluated,'constraint_feasible':sum(x['feasible'] for x in evaluated),'best_actions':sum(x['best_under_stipulated_model'] for x in evaluated),'total_cases':len(cases)})
    report={'kind':'controlled-synthetic-decision-results','case_sha256':hashlib.sha256((ROOT/'cases.json').read_bytes()).hexdigest(),'evaluator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'arms':results,'limits':['One native output per arm; no randomized replication.','Truth is stipulated by transparent scenario models, not production measurements.','A fixed action menu tests selection more than open-ended creative expansion.','Matching outcomes do not prove methods equivalent or ineffective.']}
    (ROOT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{'arm':x['arm'],'feasible':x['constraint_feasible'],'best':x['best_actions'],'cases':x['total_cases'],'errors':x['errors']} for x in results],indent=2))
if __name__=='__main__':run()
