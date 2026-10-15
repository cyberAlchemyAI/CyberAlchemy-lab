import sys,json,importlib.util
from pathlib import Path
from collections import Counter
R=Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-08-process-all')
def mod(n):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f'{n}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rt=mod('runtime');rows=rt.events();jobs=rt.schedule()[0];errors=[]
known_external={'prep_spawn','prep_join','prep_revision_join','prep_preflight_extension_spawn','prep_preflight_extension_join','prep_review_preflight_spawn','prep_review_preflight_join','contracts_frozen','review_prepare','review_spawn','review_join','adjudication_prepare','adjudication_spawn','adjudication_join','audit_prepare','audit_spawn','audit_join'}
scheduled=[];external=[]
for i,e in enumerate(rows):
 if e.get('job_id') in jobs and e.get('event') in {'prepare','spawn','join','skip','validate'}:scheduled.append((i,e))
 elif e.get('event') in known_external and e.get('job_id') not in jobs:external.append((i,e))
 else:errors.append('unrecognized ledger row '+str(i))
raw=rt.audit();original_events=rt.events
try:
 rt.events=lambda:[e for _,e in scheduled]
 scoped=rt.audit()
finally:rt.events=original_events
integrity=mod('integrity').verify();errors.extend(integrity['errors']);errors.extend(scoped['errors'])
freeze=json.loads((R/'freeze-manifest.json').read_text())
first_scored=min(e['timestamp'] for _,e in scheduled if e['event']=='spawn' and e['stage']!='preflight')
assert first_scored>integrity['frozen_at']
prep_agents={e.get('agent_id') for _,e in external if e['event']=='prep_spawn'}
terminal_prep={e.get('agent_id') for _,e in external if e['event'] in ('prep_join','prep_revision_join') and e.get('native_terminal_observed') is True}
if prep_agents-terminal_prep:errors.append('preparation helpers without observed terminal '+str(sorted(prep_agents-terminal_prep)))
unwitnessed=[i for i,e in external if e['event'] in ('prep_join','prep_revision_join') and e.get('native_terminal_observed') is not True]
native_external=[]
for prefix,key in [('review','review_id'),('adjudication','adjudication_id'),('audit','audit_id')]:
 identifiers={e.get(key) for _,e in external if e['event']==prefix+'_spawn'}
 for identifier in sorted(identifiers):
  spawns=[e for _,e in external if e['event']==prefix+'_spawn' and e.get(key)==identifier];joins=[e for _,e in external if e['event']==prefix+'_join' and e.get(key)==identifier]
  if len(spawns)!=1 or len(joins)>1:errors.append('duplicate external spawn/join '+str(identifier))
  state='running'
  if joins:
   s,j=spawns[0],joins[0]
   if j.get('agent')!=s.get('agent') or j.get('native') is not True or j.get('terminal_observed') is not True:errors.append('invalid external native witness '+str(identifier))
   path=Path(j['output_path']);current=rt.sha(path.read_bytes()) if path.exists() else None
   if current!=j.get('sha256'):errors.append('external saved output changed '+str(identifier))
   state='valid' if j.get('validation',{}).get('valid') is True else 'failed'
  native_external.append({'kind':prefix,'id':identifier,'status':state,'agent':spawns[0].get('agent')})
for prefix in ['prep_preflight_extension','prep_review_preflight']:
 spawns=[e for _,e in external if e['event']==prefix+'_spawn'];joins=[e for _,e in external if e['event']==prefix+'_join']
 for s in spawns:
  matching=[e for e in joins if e.get('agent_id')==s.get('agent_id')]
  if len(matching)!=1 or matching[0].get('native_terminal_observed') is not True:errors.append('unscored native terminal missing '+s['agent_id'])
report={'status':'pass' if not errors else 'block','errors':errors,'receipt_log_snapshot':rt.file_record(R/'receipts/events.jsonl'),'partition_complete':len(scheduled)+len(external)==len(rows),'scheduled_receipt_indices':[i for i,_ in scheduled],'external_receipt_indices':[i for i,_ in external],'external_event_counts':dict(Counter(e['event'] for _,e in external)),'scheduled_audit':scoped,'raw_mixed_ledger_audit':raw,'freeze_integrity':integrity,'first_scored_spawn':first_scored,'preparation_unique_handles':len(prep_agents),'preparation_observed_terminal_handles':len(prep_agents&terminal_prep),'unwitnessed_preparation_progress_indices':unwitnessed,'external_native_dispositions':native_external,'limit':'Frozen runtime.audit expects only scheduled receipt types. It rejects sanctioned preparation/review events in the mixed ledger. Original failure retained; exact in-memory partition invokes unchanged frozen checks on every scheduled row and separately checks all recognized external native groups. No ledger, frozen code, criteria or score output altered. Preparation revision hashes may refer to pre-freeze versions; unwitnessed progress rows are not counted as native terminal completions.'}
path=R/'reports'/('receipt-partition-'+sys.argv[1]+'.json');assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'errors':errors,'scheduled':scoped['counts'],'external_native':native_external,'unwitnessed_preparation_progress':unwitnessed}))
