"""Freeze complete coherence selection before native or query effects."""
from base import *

def run():
 require(not (HERE/'manifest.json').exists(),'refuse frozen selection overwrite');ctx=original(CONTEXT);files={}
 def add(b):
  bound(b,external=True);require(b['path'] not in files or files[b['path']]==b['sha256'],'original source epoch conflict');files[b['path']]=b['sha256']
 add(CONTEXT)
 for b in ctx['source_bindings']:add(b)
 lookup={b['path']:b for b in ctx['source_bindings']}
 for path in RECEIPTS:
  value=original(lookup[path]);require(value['result']=='PASS' and value.get('task_complete',True) and value['actual_owner_outcome'] is None,'complete scoped prerequisite required')
  for b in value['files']:add({k:b[k] for k in ['path','sha256']})
 for p in HERE.iterdir():
  if p.is_file():add(binding(p))
 result={'schema_version':'lab-O07-source-closure/v1-candidate','task':'O07','authority_effect':'none','actual_owner_outcome':None,'source_context_binding':CONTEXT,
  'files':[{'path':p,'sha256':h} for p,h in sorted(files.items())],'execution_locator_binding':ctx['execution_locator_binding'],
  'write_roots':ctx['allowed_candidate_roots'],'operational_adoption':False,'private_body_exports':False,'original_owner_obligation_route':'A03'}
 emit(HERE/'manifest.json',result);print(json.dumps({'result':'PASS','manifest_binding':binding(HERE/'manifest.json'),'files':len(files)}))

if __name__=='__main__':run()
