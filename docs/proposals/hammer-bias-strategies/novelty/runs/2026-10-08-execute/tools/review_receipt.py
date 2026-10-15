#!/usr/bin/env python3
"""Record an orchestrator-observed native review event, never infer completion."""
import argparse,datetime,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('event',choices=['spawn','join']);a.add_argument('phase');a.add_argument('case');a.add_argument('role',choices=['J1','J2','adjudicator']);a.add_argument('agent');a.add_argument('--native-terminal-observed',action='store_true');q=a.parse_args()
adju=q.role=='adjudicator';suffix='adjudication' if adju else q.role
out=R/'reviews'/f'{q.phase}-{q.case}-{suffix}.json'
row={'event':q.event,'phase':q.phase,'case_id':q.case,'agent_id':q.agent,'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output':str(out),'parent_reported_native_event':True}
row['role' if adju else 'judge_id']=q.role
log=R/'receipts/review-events.jsonl';events=[json.loads(x) for x in log.read_text().splitlines()]
assert not any(e['event']==q.event and e['agent_id']==q.agent for e in events),'Event already recorded'
if q.event=='spawn':
 prompt=R/'prompts/jobs'/(f'adjudicate-{q.phase}-{q.case}.txt' if adju else f'judge-{q.phase}-{q.case}-{q.role}.txt')
 row.update(fork_turns='none',prompt=str(prompt),prompt_sha256=sha(prompt))
 if adju:
  manifest=prompt.with_suffix('.manifest.json');m=json.loads(manifest.read_text());row.update(prompt_manifest_sha256=sha(manifest),disputed_pairs=m['disputed_pairs'],raw_resolutions=m['raw_resolutions'],agreed_raw=m['agreed_raw'],post_disputes=len(m['post_disputes']))
 else:
  manifest=R/'blinded'/q.phase/q.case/'manifest.json';m=json.loads(manifest.read_text());row.update(blinded_manifest_sha256=sha(manifest),pair_assessments=len(m['packets']))
else:
 assert q.native_terminal_observed,'Caller must have observed actual terminal completion'
 assert any(e['event']=='spawn' and e['agent_id']==q.agent for e in events),'Missing observed spawn receipt'
 row.update(output_sha256=sha(out),output_words=len(out.read_text().split()),native_terminal_observed=True,actual_tokens=None)
 lock=R/'receipts'/(f'adjudication-{q.phase}-{q.case}-lock.json' if adju else f'review-{q.phase}-{q.case}-{q.role}-lock.json')
 assert not lock.exists();lock.write_text(json.dumps(row,indent=2)+'\n')
with log.open('a') as f:f.write(json.dumps(row)+'\n')
print(json.dumps(row,indent=2))
