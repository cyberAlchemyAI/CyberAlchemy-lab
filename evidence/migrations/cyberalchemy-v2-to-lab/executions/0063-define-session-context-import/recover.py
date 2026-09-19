import json,hashlib,subprocess
from pathlib import Path
rows=json.loads(Path('../cyberAlchemy-v2/define/system-ontology/SOURCES.json').read_text())['sources'];wanted={r['sha256']:r for r in rows if r['source_id'] in ['reasoning.semantic-evaluator-witness','domainspec.current-implementation','domainspec.supported-profiles','ontology-vault.type-catalog']};out=Path('/tmp/define-system-recovery');out.mkdir(exist_ok=True);found=[]
for sha,r in list(wanted.items()):
 if r['source_id']=='ontology-vault.type-catalog':
  p=Path('../domainspec-core/.agents/skills/ontology-vault/catalogs/ontology-types.json')
  if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==sha:(out/sha).write_bytes(p.read_bytes());found.append({'id':r['source_id'],'sha256':sha,'from':str(p)});del wanted[sha]
for repo in ['../domainspec-core','../cya-orquestrator']:
 result=subprocess.run(['git','-C',repo,'cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)'],capture_output=True,text=True,check=True)
 sizes={str(r['size_bytes']) for r in wanted.values()}
 ids=[x.split()[0] for x in result.stdout.splitlines() if x.split()[1]=='blob' and x.split()[2] in sizes]
 for oid in ids:
  data=subprocess.run(['git','-C',repo,'cat-file','blob',oid],capture_output=True,check=True).stdout;sha=hashlib.sha256(data).hexdigest()
  if sha in wanted:(out/sha).write_bytes(data);found.append({'id':wanted[sha]['source_id'],'sha256':sha,'from':repo,'git_blob':oid});del wanted[sha]
(out/'recovery.json').write_text(json.dumps({'found':found,'missing':list(wanted.values())},indent=2)+'\n');print((out/'recovery.json').read_text())
