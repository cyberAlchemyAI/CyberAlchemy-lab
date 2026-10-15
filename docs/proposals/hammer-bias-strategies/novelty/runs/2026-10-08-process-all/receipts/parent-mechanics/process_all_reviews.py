import sys,json,importlib.util
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-08-process-all')
def mod(n):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f'{n}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rt,ev=mod('runtime'),mod('evaluation')
assert mod('integrity').verify()['valid']
def write(path,data):
 assert not path.exists(),path
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n')
def kindcase(stem):return ('main',stem.split('-')[1]) if stem.startswith('main-') else (stem,None)
def locations(rid):
 return R/'prompts/jobs'/f'review-{rid}.txt',R/'blinded'/f'{rid}.json',R/'reviews'/f'{rid}.json'
action,rid,*args=sys.argv[1:]
if action=='prepare':
 states=rt.status()['jobs'];assert all(states[j['job_id']]['status'] in ('valid','failed','skipped') for j in rt.schedule()[0].values() if j['stage']!='preflight')
 kind,case=kindcase(rid);packets=ev.prepare(kind,case,R)
 for packet in packets:
  name=packet.stem;prompt,_,output=locations(name);assert not prompt.exists()
  sources=[packet,R/'criteria.json',R/'review-contract.json']
  prompt.write_text((R/'prompts'/f'review-{kind}.txt').read_text()+'\nRuntime file contract:\nRead only these sources:\n'+'\n'.join(str(p) for p in sources)+'\nAssigned reviewer_id: '+name+'\nSave first substantive JSON only at: '+str(output)+'\n')
  rt.append({'event':'review_prepare','review_id':name,'prompt':rt.file_record(prompt),'sources':[rt.file_record(p) for p in sources],'output_path':str(output),'native':True})
 print(json.dumps({'prepared':rid,'packets':[str(p) for p in packets]}))
elif action in ('spawn','join'):
 agent=args[0];prompt,packet,output=locations(rid);kind,_=kindcase(rid.rsplit('-J',1)[0]);events=rt.events()
 if action=='spawn':
  assert not output.exists();assert not any(e.get('event')=='review_spawn' and e.get('review_id')==rid for e in events)
  prep=next(e for e in events if e.get('event')=='review_prepare' and e.get('review_id')==rid)
  for row in [prep['prompt'],*prep['sources']]:assert rt.file_record(Path(row['path']))==row
  rt.append({'event':'review_spawn','review_id':rid,'agent':agent,'native':True,'parent_recorded':True,'os_isolation':False,'input_word_proxy':sum(s['word_proxy'] for s in prep['sources'])+prep['prompt']['word_proxy'],'actual_tokens':None})
  print(json.dumps({'event':'review_spawn','review_id':rid}))
 else:
  assert any(e.get('event')=='review_spawn' and e.get('review_id')==rid and e.get('agent')==agent for e in events)
  assert not any(e.get('event')=='review_join' and e.get('review_id')==rid for e in events)
  try:review=rt.decode(output.read_bytes());errors=ev.check(kind,ev.read_json(packet),review)
  except Exception as e:errors=[type(e).__name__+': '+str(e)]
  rec=rt.file_record(output) if output.exists() else {'sha256':None,'word_proxy':None}
  validation={'valid':not errors,'errors':errors};write(R/'reports'/f'{rid}-check.json',validation)
  rt.append({'event':'review_join','review_id':rid,'agent':agent,'native':True,'terminal_observed':True,'observation':'parent-recorded terminal observation','parent_recorded':True,'os_isolation':False,'output_path':str(output),'sha256':rec['sha256'],'known_words':rec['word_proxy'],'actual_tokens':None,'validation':validation})
  print(json.dumps({'event':'review_join','review_id':rid,'valid':not errors,'errors':errors[:5],'words':rec['word_proxy']}))
else:raise ValueError(action)
