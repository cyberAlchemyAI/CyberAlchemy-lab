import json,hashlib,shutil
from pathlib import Path
root=Path.cwd();base=root/'evidence/migrations/cyberalchemy-v2-to-lab/executions';here=base/'0048-agent-reasoning-context-import';here.mkdir(exist_ok=True);workspace=root/'.local/agent-reasoning-package-0048';source=root.parent/'cyberAlchemy-v2';package=workspace/'cyberAlchemy-v2/agent-reasoning-engine'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
if not package.exists():shutil.copytree(source/'agent-reasoning-engine',package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
compiler=workspace/'projects/domainspec-v2/impl'
if not compiler.exists():shutil.copytree(root.parent/'domainspec-core/projects/domainspec-v2/impl',compiler,ignore=shutil.ignore_patterns('node_modules','.git','__pycache__'))
registry=read(source/'agent-reasoning-engine/sources.json');original=read(source/'agent-reasoning-engine/sources.json');recovery={r['id']:r for r in read(base/'0046-agent-reasoning-evidence-recovery/recovery.json')};previous={r['id']:r for r in read(base/'0045-agent-reasoning-context-preparation/evidence-recovery.json')};replacements={r['source_id']:r for r in read(base/'0047-agent-reasoning-runtime-evidence/replacement-bindings.json')['bindings']};changes=[]
for s in registry['sources']:
 target=workspace/s['path'];current=root.parent/s['path'];data=current.read_bytes()
 if s['id'] in replacements:
  data=(base/'0047-agent-reasoning-runtime-evidence'/replacements[s['id']]['snapshot']).read_bytes();s['sha256']=replacements[s['id']]['successor']['sha256']
 elif s['scope_kind']=='whole-file' and hashlib.sha256(data).hexdigest()!=s['sha256']:
  if s['id'] in recovery and recovery[s['id']]['matches']:data=(base/'0046-agent-reasoning-evidence-recovery'/recovery[s['id']]['matches'][0]['snapshot']).read_bytes()
  else:data=(base/'0045-agent-reasoning-context-preparation/evidence-selections'/(s['id']+'.txt')).read_bytes()
 if s['id']=='CAP-SEL-ARE-PRODUCT':
  s['path']='migration-evidence/original-agent-reasoning-product.json';target=workspace/s['path']
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 old=next(r for r in original['sources'] if r['id']==s['id'])
 if old!=s:changes.append({'id':s['id'],'before':old,'after':s})
# Keep current Product with both capabilities; original Product remains separate historical evidence.
shutil.copyfile(source/'agent-reasoning-engine/product.json',package/'product.json')
dump(package/'sources.json',registry)
shutil.copyfile(base/'0045-agent-reasoning-context-preparation/proposed-source-package.schema.json',package/'schemas/agent-reasoning-engine-ontology.schema.json')
# The projection builder hashes a small additional set of implementation files.
import re
for relative in re.findall(r'resolve\(repositoryRoot, "([^"]+)"\)',(package/'scripts/build.ts').read_text()):
 p=workspace/relative
 if not p.exists():
  q=root.parent/relative
  if not q.exists():raise ValueError(relative)
  p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,p)
dump(here/'repair-delta.json',{'source_registry_changes':changes,'product_schema':'0045 proposed-source-package.schema.json','ontology_schema':'0045 proposed-ontology.schema.json','authority_effect':'none','ontology_contract_admission':'not-granted; candidate schema used explicitly, existing admitted registry unchanged'})
dump(here/'package-inputs.json',[{'path':str(p.relative_to(workspace)),'sha256':sha(p)} for p in sorted(workspace.rglob('*')) if p.is_file() and '/domainspec/generated/' not in str(p)])
print(workspace)
