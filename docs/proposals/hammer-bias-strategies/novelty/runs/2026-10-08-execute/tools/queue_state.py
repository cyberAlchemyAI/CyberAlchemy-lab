#!/usr/bin/env python3
"""Read native-event state; never generate answers or infer terminal handles."""
import argparse,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--phase',default='discovery');a.add_argument('--case',default='D1');a.add_argument('--limit',type=int,default=8);q=a.parse_args()
events=[json.loads(s) for s in (R/'receipts/events.jsonl').read_text().splitlines()]
spawned={(e['unit_id'],e['role']):e for e in events if e['event']=='spawn'}
joined={(e['unit_id'],e['role']):e for e in events if e['event']=='join'}
schedule=json.loads((R/'schedule.json').read_text())
units=[u for u in schedule['units'] if u['phase']==q.phase and u['case_id']==q.case]
active=[e for k,e in spawned.items() if k not in joined]
complete=[];ready=[];invalid=[]
for u in units:
 uid=u['unit_id']
 if all((uid,rr) in joined and joined[(uid,rr)]['artifact_validation']['valid'] for rr in u['roles']):complete.append(uid)
 for role in u['roles']:
  key=(uid,role)
  if key in joined and not joined[key]['artifact_validation']['valid']:invalid.append({'unit':uid,'role':role,'validation':joined[key]['artifact_validation']})
  if key in spawned:continue
  dependencies=[] if role in ['Z','A'] else ['Z','A'] if role=='Q' else [rr for rr in u['roles'] if rr!='D']
  if all((uid,rr) in joined and joined[(uid,rr)]['artifact_validation']['valid'] for rr in dependencies):ready.append({'unit':uid,'role':role,'prompt_exists':(R/'prompts/jobs'/f'{uid}-{role}.txt').exists()})
print(json.dumps({'phase':q.phase,'case':q.case,'complete_units':complete,'required_units':len(units),'unjoined_native_handles':active,'invalid_joined':invalid,'ready_unstarted':ready[:q.limit]},indent=2))
