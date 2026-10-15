import sys,json,importlib.util,hashlib
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-08-process-all')
def mod(n):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f'{n}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rt=mod('runtime');assert mod('integrity').verify()['valid']
def once(p,v):
 assert not p.exists(),p;p.write_text(json.dumps(v,indent=2)+'\n')
action,*args=sys.argv[1:];aid='process-all-completion';out=R/'reviews/completion-audit.json';prompt=R/'prompts/jobs/completion-audit.txt'
if action=='prepare':
 assert (R/'RESULTS.md').exists()
 es=rt.events()
 assert sum(e['event']=='review_join' for e in es)==8
 assert not any(e.get('event')=='audit_prepare' for e in es)
 # The independent auditor gets an exact allowlist, not ambient repository context.
 selected=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file() or p.name=='CONTINUATION.json':continue
  if p.parts[-2]=='__pycache__' or p.suffix=='.pyc':continue
  if p.relative_to(R).parts[0] in {'outputs','reviews','reports','blinded','receipts','tools','cases','archives','fixtures','inputs','dispatches','design','prompts'} or p.parent==R:
   selected.append(rt.file_record(p))
 index=R/'reports/completion-audit-inputs.json'
 once(index,{'scope':'P01-P10','sources':selected,'limit':'A pre-audit snapshot. The live append-only receipt log and mutable execution-accounting summaries may later include the explicitly recorded auditor itself; verify the named snapshot prefix and all immutable first saves.'})
 sources=[index,*[Path(x['path']) for x in selected]]
 assert not prompt.exists()
 prompt.write_text((R/'prompts/completion-audit.txt').read_text()+'\nRuntime file contract:\nRead only these exact files:\n'+'\n'.join(str(p) for p in sources)+'\nUse complete mechanical coverage and independently verify the source-linked conclusions without rewriting every assessment. Check the preserved failed mixed-ledger audit and explicit index partition against unchanged frozen runtime checks and every recognized external group. Preparation revision index30 is a progress record, not a native completion; the later terminal witness is separate. A root-recorded live-agent snapshot is an observation, not OS isolation. Your own running audit is the sole expected helper at audit time; its final native join will be recorded afterward. Do not retry reviews, revise scores, merge disputed families, use other agents, or access outside context. Execute only read-only checks; do not invoke report-writing CLIs. Save the first substantive JSON only at: '+str(out)+'\n')
 rt.append({'event':'audit_prepare','audit_id':aid,'native':True,'prompt':rt.file_record(prompt),'sources_manifest':rt.file_record(index),'output_path':str(out)})
 print(json.dumps({'prepared':aid,'sources':len(selected),'prompt_words':len(prompt.read_text().split())}))
elif action=='spawn':
 agent=args[0];es=rt.events();assert not out.exists();assert not any(e.get('event')=='audit_spawn' for e in es)
 prep=next(e for e in es if e.get('event')=='audit_prepare' and e.get('audit_id')==aid)
 for x in [prep['prompt'],prep['sources_manifest']]:assert rt.file_record(Path(x['path']))==x
 rt.append({'event':'audit_spawn','audit_id':aid,'agent':agent,'native':True,'parent_recorded':True,'os_isolation':False,'actual_tokens':None});print(json.dumps({'spawn':aid}))
elif action=='join':
 agent=args[0];es=rt.events();assert any(e.get('event')=='audit_spawn' and e.get('agent')==agent for e in es);assert not any(e.get('event')=='audit_join' for e in es)
 errors=[]
 try:
  d=rt.decode(out.read_bytes())
  if d.get('status') not in {'pass','pass_with_limits','block'}:errors.append('invalid audit status')
  if not isinstance(d.get('requirements'),list) or not d['requirements']:errors.append('missing requirement coverage')
  if not isinstance(d.get('counts'),dict):errors.append('missing counts')
  if not isinstance(d.get('repairs'),list) or not isinstance(d.get('limits'),list):errors.append('missing repairs or limits')
 except Exception as e:d={};errors.append(type(e).__name__+': '+str(e))
 rec=rt.file_record(out) if out.exists() else {'sha256':None,'word_proxy':None}
 v={'valid':not errors,'errors':errors,'audit_status':d.get('status')}
 once(R/'reports/completion-audit-check.json',v)
 rt.append({'event':'audit_join','audit_id':aid,'agent':agent,'native':True,'terminal_observed':True,'observation':'parent-recorded terminal observation','parent_recorded':True,'os_isolation':False,'output_path':str(out),'sha256':rec['sha256'],'known_words':rec['word_proxy'],'actual_tokens':None,'validation':v})
 print(json.dumps({'joined':aid,**v,'words':rec['word_proxy']}))
else:raise ValueError(action)
