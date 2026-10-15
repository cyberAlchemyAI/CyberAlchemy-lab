import sys,json,importlib.util
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-08-process-all')
def mod(n):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f'{n}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rt,ev=mod('runtime'),mod('evaluation');assert mod('integrity').verify()['valid']
def once(path,value):
 assert not path.exists(),path;path.write_text(json.dumps(value,indent=2)+'\n')
action,stem,*args=sys.argv[1:];kind='main' if stem.startswith('main-') else stem
prompt=R/'prompts/jobs'/f'adjudicate-{stem}.txt';output=R/'reviews'/f'{stem}-adjudication.json';disputes=R/'reports'/f'{stem}-disputes.json'
if action=='prepare':
 packet_paths=[R/'blinded'/f'{stem}-J{i}.json' for i in (1,2)];review_paths=[R/'reviews'/f'{stem}-J{i}.json' for i in (1,2)]
 events=rt.events();valid=all(any(e.get('event')=='review_join' and e.get('review_id')==f'{stem}-J{i}' and e.get('terminal_observed') is True and e['validation']['valid'] for e in events) for i in (1,2))
 if valid:comp=ev.compare(kind,*[ev.read_json(p) for p in [packet_paths[0],review_paths[0],packet_paths[1],review_paths[1]]])
 else:comp={'kind':kind,'status':'incomplete','disputes':[],'errors':['one or both native reviews missing/invalid'],'families':{}}
 once(disputes,comp)
 allowed=set(ev.MAIN_SCALARS)|{'presence'} if kind=='main' else set(ev.P08_SCALARS) if kind=='p08' else set(ev.P09_SCALARS)|{'fit','presence'}
 actionable=[d for d in comp['disputes'] if d['field'] in allowed]
 if comp['status']=='compared' and actionable:
  sources=[*packet_paths,*review_paths,disputes,R/'criteria.json',R/'review-contract.json']
  assert not prompt.exists();prompt.write_text((R/'prompts/adjudicate.txt').read_text()+'\nRuntime file contract:\nRead only:\n'+'\n'.join(str(p) for p in sources)+'\nAllowed scalar fields: '+', '.join(sorted(allowed))+'. Archive correspondences and family relations remain unresolved.\nSave first substantive JSON only at: '+str(output)+'\n')
  rt.append({'event':'adjudication_prepare','adjudication_id':stem,'native':True,'prompt':rt.file_record(prompt),'sources':[rt.file_record(p) for p in sources],'output_path':str(output)})
 print(json.dumps({'prepared':stem,'status':comp['status'],'disputes':len(comp['disputes']),'actionable':len(actionable),'family_clusters':len(comp.get('families',{}).get('clusters',[]))}))
elif action=='spawn':
 agent=args[0];events=rt.events();assert not output.exists();assert not any(e.get('event')=='adjudication_spawn' and e.get('adjudication_id')==stem for e in events)
 prep=next(e for e in events if e.get('event')=='adjudication_prepare' and e.get('adjudication_id')==stem)
 for rec in [prep['prompt'],*prep['sources']]:assert rt.file_record(Path(rec['path']))==rec
 rt.append({'event':'adjudication_spawn','adjudication_id':stem,'agent':agent,'native':True,'parent_recorded':True,'os_isolation':False,'input_word_proxy':sum(s['word_proxy'] for s in prep['sources'])+prep['prompt']['word_proxy'],'actual_tokens':None});print(json.dumps({'spawn':stem}))
elif action=='join':
 agent=args[0];events=rt.events();assert any(e.get('event')=='adjudication_spawn' and e.get('adjudication_id')==stem and e.get('agent')==agent for e in events);assert not any(e.get('event')=='adjudication_join' and e.get('adjudication_id')==stem for e in events)
 try:
  data=rt.decode(output.read_bytes());overrides,errors=ev._adjudicate(kind,ev.read_json(disputes),data)
 except Exception as e:errors=[type(e).__name__+': '+str(e)];overrides={}
 rec=rt.file_record(output) if output.exists() else {'sha256':None,'word_proxy':None}
 validation={'valid':not errors,'errors':errors};once(R/'reports'/f'{stem}-adjudication-check.json',validation)
 rt.append({'event':'adjudication_join','adjudication_id':stem,'agent':agent,'native':True,'terminal_observed':True,'observation':'parent-recorded terminal observation','parent_recorded':True,'os_isolation':False,'output_path':str(output),'sha256':rec['sha256'],'known_words':rec['word_proxy'],'actual_tokens':None,'validation':validation});print(json.dumps({'joined':stem,'valid':not errors,'errors':errors[:5],'resolved':len(overrides),'words':rec['word_proxy']}))
else:raise ValueError(action)
