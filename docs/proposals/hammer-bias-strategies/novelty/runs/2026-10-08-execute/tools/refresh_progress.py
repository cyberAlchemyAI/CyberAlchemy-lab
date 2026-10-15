#!/usr/bin/env python3
"""Refresh descriptive status from observed receipts; never infer native completion."""
import json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def rows(p):return [json.loads(x) for x in (R/p).read_text().splitlines()]
def save(p,d):(R/p).write_text(json.dumps(d,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
events=rows('receipts/events.jsonl');reviews=rows('receipts/review-events.jsonl')
joined={(e['unit_id'],e['role']):e for e in events if e['event']=='join'}
failed={e['unit_id']:e for e in rows('reports/execution-failures.jsonl')}
schedule=read('schedule.json')['units']+read('confirmation-schedule.json')['units']
conditions={}
for u in schedule:
 uid=u['unit_id'];valid=[r for r in u['roles'] if (uid,r) in joined and joined[(uid,r)]['artifact_validation']['valid']]
 complete=set(valid)==set(u['roles']);failure=uid in failed;phase=u['phase'];case=u['case_id'];status='pending'
 if (R/f'reports/{phase}-{case}-resolved.json').exists():status='Both judges and adjudication locked; explicit uncertainty preserved'
 elif all((R/f'receipts/review-{phase}-{case}-{j}-lock.json').exists() for j in ['J1','J2']):status='Both judges locked; adjudication/normalization pending'
 row={'unit_id':uid,'phase':phase,'case_id':case,'repetition':u['repetition'],'joined_valid_roles':valid,'required_roles':u['roles'],'generation_complete':complete,'terminal_attempt':complete or failure,'generation_disposition':'completed_valid' if complete else ('execution_failed' if failure else 'pending'),'independent_review':status}
 if failure:row.update(failed_roles=[failed[uid]['failed_role']],skipped_roles=[x['role'] for x in failed[uid]['skipped_roles']])
 conditions.setdefault(u['condition'],[]).append(row)
allrows=[x for rr in conditions.values() for x in rr]
active=[{k:e[k] for k in ['unit_id','role','agent_id']} for e in events if e['event']=='spawn' and (e['unit_id'],e['role']) not in joined]
reviewjoins={e['agent_id'] for e in reviews if e['event']=='join'}
reviewactive=[e['agent_id'] for e in reviews if e['event']=='spawn' and e['agent_id'] not in reviewjoins]
confirmation=sum(x['generation_complete'] for x in allrows if x['phase']=='confirmation')
d=read('completion-matrix.json');d.update(conditions=conditions,updated_utc=now,confirmation={'required':48,'finalists':read('finalist-freeze.json')['finalists'],'schedule':'confirmation-schedule.json','completed':confirmation},blind_reviews={f'{phase}/{case}':'resolved' if (R/f'reports/{phase}-{case}-resolved.json').exists() else 'pending' for phase,cases in [('discovery',['D1','D2']),('bundle',['D1','D2']),('confirmation',['H1','H2','H3','H4'])] for case in cases});save('completion-matrix.json',d)
progress={'scored_generation_units_complete_valid':sum(x['generation_complete'] for x in allrows),'scored_units_terminal_execution_failed':len(failed),'scored_units_required':len(schedule),'discovery_valid_complete':sum(x['generation_complete'] for x in allrows if x['phase']=='discovery'),'bundle_valid_complete':sum(x['generation_complete'] for x in allrows if x['phase']=='bundle'),'failed_units':sorted(failed),'scored_roles_joined_valid':sum(e['artifact_validation']['valid'] for e in joined.values() if e['unit_id']!='P000'),'spawned_not_joined':active,'review_handles':{'locked':sorted(reviewjoins),'running':reviewactive},'finalists':read('finalist-freeze.json')['finalists'],'confirmation_prepared_units':48,'confirmation_completed_units':confirmation,'orchestrator':'root'}
d=read('CONTINUATION.json');d.update(updated_utc=now,current_progress=progress)
d['running']=[{'handle':x['agent_id'],'scope':x['unit_id']+' '+x['role'],'status':'Native spawned; join only after terminal observation'} for x in active]+[{'handle':a,'scope':'Independent review/adjudication','status':'Native spawned; no terminal observed'} for a in reviewactive]
save('CONTINUATION.json',d);print(json.dumps(progress,indent=2))
