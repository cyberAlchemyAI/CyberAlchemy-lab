import json,hashlib,subprocess
from pathlib import Path
rows=json.loads(Path('../cyberAlchemy-v2/define/sources.json').read_text())['sources'];wanted={r['sha256']:r for r in rows if r['id'] in ['SRC-CAV2-SOURCE-MAP','SRC-ARCANUM-INVOKE-ONTOLOGY-PROFILE','SRC-ARCANUM-INVOKE-BUSINESS','SRC-ARCANUM-INVOKE-SYSTEM','SRC-ARCANUM-INVOKE-BRIDGE']};out=Path('/tmp/define-bridge-recovery');out.mkdir(exist_ok=True);found=[]
for repo in ['../domainspec-core','../cya-orquestrator']:
 result=subprocess.run(['git','-C',repo,'cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)'],capture_output=True,text=True,check=True);sizes={str(r['size']) for r in wanted.values()}
 for line in result.stdout.splitlines():
  oid,kind,size=line.split()
  if kind!='blob' or size not in sizes:continue
  data=subprocess.run(['git','-C',repo,'cat-file','blob',oid],capture_output=True,check=True).stdout;sha=hashlib.sha256(data).hexdigest()
  if sha in wanted:(out/sha).write_bytes(data);found.append({'id':wanted[sha]['id'],'sha256':sha,'repository':repo,'git_blob':oid});del wanted[sha]
(out/'recovery.json').write_text(json.dumps({'found':found,'missing':list(wanted.values())},indent=2)+'\n');print((out/'recovery.json').read_text())
