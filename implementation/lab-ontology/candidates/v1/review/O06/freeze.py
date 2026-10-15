"""Freeze complete original-byte prerequisite and local code closure before proof."""
from package import *

def freeze():
 require(not (HERE/'manifest.json').exists(),'refuse source closure overwrite')
 selected=pins();files={}
 def add(b):
  bound(b,allow_external=True)
  require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting original source epochs')
  files[b['path']]=b['sha256']
 add(CONTEXT)
 for b in original(CONTEXT)['source_bindings']:add(b)
 for b in selected.values():
  add(b)
  for f in original(b)['files']:add({k:f[k] for k in ['path','sha256']})
 for p in HERE.rglob('*'):
  if p.is_file() and not any(x in p.parts for x in ['__pycache__','packages','receipts','proof','guards']) and p.suffix!='.pyc':add(binding(p))
 value={'schema_version':'lab-O06-source-closure/v1-candidate','task':'O06','authority_effect':'none','actual_owner_outcome':None,
  'files':[{'path':p,'sha256':h} for p,h in sorted(files.items())],
  'external_evidence_is_read_only':True,'operational_permission_granted':False}
 put(HERE/'manifest.json',value);print(encoded({'result':'PASS','files':len(files),'manifest_binding':binding(HERE/'manifest.json')}).decode(),end='')

if __name__=='__main__':freeze()
