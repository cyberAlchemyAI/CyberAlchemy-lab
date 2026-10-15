from pathlib import Path
import json,hashlib,datetime,argparse
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('mode',choices=['spawn','final']);p.add_argument('agent');p.add_argument('job');p.add_argument('--role',default='constructor');p.add_argument('--artifact');a=p.parse_args()
ledger=R/'receipts/NATIVE-INVOCATIONS.v1.json';d=json.loads(ledger.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
if a.mode=='spawn':
 if any(x.get('job_id')==a.job for x in d['agents']):raise SystemExit('Already registered')
 q=R/'preparation/jobs'/a.job
 row={'agent_id':a.agent,'job_id':a.job,'role_id':a.role,'phase':'native-investigation','spawn_status':'spawned','join_status':'pending','close_status':'pending','fork_turns':'none','root_observation_recorded_utc':now,'evidence':'Actual collaboration.spawn_agent response observed by root; timestamp records this witness, not native platform spawn time.'}
 for name in ['PROMPT.md','PAYLOAD.json']:
  f=q/name
  if f.exists():row[name.lower().replace('.','_')]={'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 d['agents'].append(row)
else:
 hits=[x for x in d['agents'] if x.get('job_id')==a.job and x['agent_id']==a.agent]
 if len(hits)!=1:raise SystemExit('Expected one recorded spawn')
 row=hits[0]
 if row['join_status']!='pending':raise SystemExit('Already joined')
 f=R/(a.artifact or ('raw/'+a.job+'.json'))
 if not f.exists():raise SystemExit('Missing substantive output')
 raw=f.read_bytes();body=raw.decode();data=json.loads(body) if f.suffix=='.json' else None
 if len(body)<250:raise SystemExit('Empty/save-summary output')
 row.update(join_status='completed',close_status='closed',final_observed_utc=now,root_observed_actual_FINAL=True,artifacts=[{'path':str(f.relative_to(R)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'saved_body_words_proxy':len(body.split())}])
 if isinstance(data,dict) and isinstance(data.get('rows'),list):row['actual_row_ids']=[x.get('strategy_id') for x in data['rows']]
 row['validation']='Substantive body present and parseable; semantic fidelity remains independent review obligation'
d['actual_role_turns']=len(d['agents']);ledger.write_text(json.dumps(d,indent=2)+'\n');print(a.mode,a.job)
