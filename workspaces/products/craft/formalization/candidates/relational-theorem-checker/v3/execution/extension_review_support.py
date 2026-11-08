"""Sequential extension author review; no implementation acceptance by file presence alone."""
from pathlib import Path
from . import support as s

def finish(id,findings,review):
 h=s.BASE/id.lower();r=s.read(h/'controls.json')
 s.require(r['result']=='pass' and all(c['result']=='pass' for c in r['controls']),'failed controls')
 roots=[];fresh=[]
 for case in r.get('cases',[]):
  s.check(case['input']);a=s.read(s.check(case['answer']))
  if a.get('supervised_run',{}).get('job'):roots.append(Path(a['supervised_run']['job']))
  if a['status']=='fresh-extension-candidate':
   s.check(a['completion']);v=a['value']
   for ref in v['imports']+v['worker_sources']:s.check(ref)
   for m in v['kernel']:
    s.check(m['source']);s.check(m['olean']);s.require('sorryAx' not in m['output'],'admitted witness')
   fresh.append(v)
 s.require(len(fresh)>=r.get('full_witnesses_required',1),'complete witness criterion')
 (h/review[0]).write_text(review[1])
 extra=[p for p in h.iterdir() if p.is_file() and p.name not in ['task-acceptance.json','control-progress.json']]
 for sub in ['formal-build','evidence','store-controls']:
  extra += [p for p in (h/sub).rglob('*') if p.is_file()]
 for root in roots:extra += [p for p in root.rglob('*') if p.is_file()]
 extra += [s.BASE/'execution'/('E'+id[1:]+'-implementation-plan.md'),Path(__file__)]
 s.accept(id,findings,r['controls'],extra=list({str(p.resolve()):p for p in extra}.values()))
 print(id,'accepted;',len(r['controls']),'controls;',len(fresh),'full witnesses.',flush=True)
