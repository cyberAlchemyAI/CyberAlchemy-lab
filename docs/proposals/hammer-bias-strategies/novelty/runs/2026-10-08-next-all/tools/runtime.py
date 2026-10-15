"""Run-local native-role receipt mechanics. Host spawn/terminal claims are root-observed."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def event(e):
 e={'dispatch_id':'hammer-novelty-next-all-2026-10-08','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**e}
 with (R/'receipts/events.jsonl').open('a') as f:f.write(json.dumps(e)+'\n')
 return e
def jobs():
 all_jobs=read(R/'schedule.json')['jobs']
 if (R/'review-schedule.json').exists():all_jobs+=read(R/'review-schedule.json')['jobs']
 return {j['job_id']:j for j in all_jobs}
def events():return [json.loads(s) for s in (R/'receipts/events.jsonl').read_text().splitlines()]
def status():
 out={k:'pending' for k in jobs()}
 for e in events():
  k=e.get('job_id')
  if k not in out:continue
  if e['event_kind']=='job_prepared':out[k]='ready'
  if e['event_kind']=='native_spawn':out[k]='running'
  if e['event_kind']=='native_terminal_join':out[k]='valid' if e['validation']['valid'] else 'invalid'
  if e['event_kind']=='dependency_disposition':out[k]=e['status']
 return out
def prepare(k):
 j=jobs()[k];assert status()[k]=='pending'
 st=status();assert all(st.get(x)=='valid' for x in j.get('depends_on',[])),j.get('depends_on')
 for gate in j.get('requires_gates',[]):
  gp=R/'receipts/gates'/f'{gate}.json';assert gp.exists() and read(gp).get('status')=='pass',f'gate not passed: {gate}'
 inputs=[{'path':n,'sha256':digest(R/n)} for n in j['input_refs']]
 prompt=R/j['prompt_ref'];assert prompt.exists();output=R/j['output_ref'];assert not output.exists(),'first save already exists'
 text=prompt.read_text()+ '\nAssigned exact inputs: '+', '.join(str((R/x['path']).resolve()) for x in inputs)+'\nWrite only '+str(output.resolve())+'. Read only these named inputs and the instruction. No other files or siblings.\n'
 q=R/'prompts/jobs'/f'{k}.txt';q.parent.mkdir(exist_ok=True);assert not q.exists();q.write_text(text)
 return event({'event_kind':'job_prepared','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'input_bindings':inputs,'prompt_ref':str(q.relative_to(R)),'prompt_sha256':digest(q),'output_ref':j['output_ref']})
def spawn(k,handle):
 j=jobs()[k];assert status()[k]=='ready'
 return event({'event_kind':'native_spawn','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'agent_handle':handle,'turn':1,'fresh_context':True,'host_spawn_observed':True})
def validate(j):
 p=R/j['output_ref'];errors=[]
 if not p.exists():return {'valid':False,'errors':['missing output']}
 try:d=read(p)
 except Exception as exc:return {'valid':False,'errors':['invalid JSON: '+str(exc)],'output_sha256':digest(p)}
 if j['output_type']=='compression':
  src=read(R/j['input_refs'][0]);raw=src['raw_candidates'];known={c['id'] for c in raw}
  if d.get('case_id')!=src['case_id']:errors.append('case ID mismatch')
  op=d.get('openings');lin=d.get('lineage')
  if not isinstance(op,list) or not isinstance(lin,list):errors.append('openings/lineage not lists')
  else:
   ids=[o.get('id') for o in op];seen=[l.get('source_id') for l in lin]
   if len(ids)!=len(set(ids)) or any(not isinstance(x,str) for x in ids):errors.append('invalid post IDs')
   if set(seen)!=known or len(seen)!=len(known):errors.append('raw lineage coverage mismatch')
   for o in op:
    if not isinstance(o.get('source_ids'),list) or not o['source_ids'] or not set(o['source_ids'])<=known:errors.append('invalid post sources')
    if o.get('fit') not in ['preserves','uncertain','conditional','violates']:errors.append('invalid fit')
    for x in ['claim','discriminator','probe','uncertainty']:
     if not isinstance(o.get(x),str):errors.append('missing/nonstring '+x)
   for l in lin:
    if l.get('disposition') not in ['retained','merged','parked','rejected']:errors.append('invalid disposition')
    if not isinstance(l.get('target_ids'),list) or not set(l['target_ids'])<=set(ids):errors.append('invalid targets')
    if l.get('disposition') in ['parked','rejected'] and l.get('target_ids'):errors.append('parked/rejected has targets')
    if not isinstance(l.get('reason'),str):errors.append('missing lineage reason')
 elif j['output_type']=='anchors':
  expected={x['id'] for x in read(R/j['input_refs'][0])['items']};a=d.get('answers',[]);got=[x.get('item_id') for x in a]
  if set(got)!=expected or len(got)!=len(expected):errors.append('anchor exact coverage mismatch')
 elif j['output_type']=='review':
  if not isinstance(d.get('units'),list):errors.append('review units missing')
  else:
   packet=read(R/j['input_refs'][0]);expected={u['unit_id']:u for u in packet['units']};got=[u.get('unit_id') for u in d['units']]
   if set(got)!=set(expected) or len(got)!=len(expected):errors.append('review exact unit coverage mismatch')
   for u in d['units']:
    if u.get('unit_id') not in expected:continue
    src=packet['source_cases'][expected[u['unit_id']]['case_id']];raw_ids={x['id'] for x in src['raw_candidates']};rows=u.get('rows',[]);row_ids=[x.get('raw_id') for x in rows]
    if set(row_ids)!=raw_ids or len(row_ids)!=len(raw_ids):errors.append('review raw row coverage mismatch')
    for row in rows:
     for field in ['relation','discriminator','uncertainty']:
      if row.get(field) not in ['retained','lost','uncertain','unobservable']:errors.append('invalid retention enum')
     for field in ['lineage_consistent','fit_preserved','complete_protected_fields']:
      if not isinstance(row.get(field),bool):errors.append('invalid review boolean')
 else:errors.append('unknown output type')
 return {'valid':not errors,'errors':errors,'output_sha256':digest(p),'saved_words':len(p.read_text().split())}
def join(k,handle):
 j=jobs()[k];assert status()[k]=='running'
 spawn_events=[e for e in events() if e.get('job_id')==k and e['event_kind']=='native_spawn'];assert spawn_events[-1]['agent_handle']==handle
 prepared=[e for e in events() if e.get('job_id')==k and e['event_kind']=='job_prepared'][-1]
 assert all(digest(R/x['path'])==x['sha256'] for x in prepared['input_bindings']),'source drift'
 return event({'event_kind':'native_terminal_join','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'agent_handle':handle,'turn':1,'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':validate(j),'output_ref':j['output_ref']})
if __name__=='__main__':
 a=sys.argv[1:];cmd=a.pop(0)
 if cmd=='status':print(json.dumps(status(),indent=2))
 elif cmd=='prepare':print(json.dumps(prepare(a[0])))
 elif cmd=='spawn':print(json.dumps(spawn(*a)))
 elif cmd=='join':print(json.dumps(join(*a)))
 else:raise SystemExit('unknown command')
