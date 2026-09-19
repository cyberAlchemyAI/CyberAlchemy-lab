"""Pin original inputs and a separate compiler successor. Open questions: README.md."""
import ast, hashlib, json, shutil, tarfile
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0068-essays-system-context-import';W=R/'.local/essays-system-package-0068';PREFIX='cyberAlchemy-v2/essays/development/agent-runtime/domainspec'
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def read(p):return json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(R.parent/PREFIX,W/PREFIX,dirs_exist_ok=True)
shutil.copytree('/home/vrondelli/.cache/auth-completion/build-tools/node_modules',W/'node_modules',dirs_exist_ok=True)
base='cyberAlchemy-v2/';groups={}
for key,rel in [('agent_runtime_business_ontology_material_digest','essays/capabilities/agent-runtime/ontology'),('authority_ontology_material_digest','essays/capabilities/agent-runtime/authority-ontology'),('architecture_properties_material_digest','essays/development/agent-runtime/architecture-properties')]:
 p=R.parent/base/rel;profile=read(p/'PROFILE.json');names=profile.get('material_files') or profile['inventory_contract']['core_files'];groups[key]=[base+rel+'/'+n for n in names]
for key,rel in [('product_ontology_material_digest','essays/ontology/product'),('writing_ontology_material_digest','essays/capabilities/writing/ontology')]:
 p=R.parent/base/rel
 if 'writing' in rel:
  tree=ast.parse((p/'scripts/materialize.py').read_text());names=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STATIC_FILES' for t in n.targets))
 else:names=['PROFILE.json','TYPE-SELECTION.json','MATERIALIZATION-DECISION.json','SCHEMA-BINDINGS.json','README.md','schemas/product-ontology.schema.json']
 groups[key]=[base+rel+'/'+n for n in names+['NODES.json','RELATIONS.json','VIEWS.json','SOURCES.json','RESIDUE.json']]
p=R.parent/base/'essays/capabilities/agent-runtime';tree=ast.parse((p/'scripts/validate-capability-records.py').read_text());records=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECORDS' for t in n.targets));groups['capability_records_material_digest']=[base+'essays/capabilities/agent-runtime/'+n for n in records]
roots={k:str(Path(v[0]).parent) for k,v in groups.items()}
roots['capability_records_material_digest']=base+'essays/capabilities/agent-runtime'
cap=base+'essays/capabilities/essays-agent-runtime.product-capability.json'
for name in {cap}|{n for rows in groups.values() for n in rows}:
 dst=W/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R.parent/name,dst)
bindings={}
for key,names in groups.items():
 h=hashlib.sha256();root=Path(roots[key])
 for name in sorted(names):h.update(str(Path(name).relative_to(root)).encode()+b'\0'+(W/name).read_bytes()+b'\0')
 bindings[key]={'material_root':str(root),'files':sorted(names),'actual':h.hexdigest()}
bindings['product_capability_sha256']={'files':[cap],'actual':sha(W/cap)}
pre=read(W/PREFIX/'PREDECESSORS.json')
for key,b in bindings.items():assert b['actual']==pre[key],(key,b['actual'],pre[key])
dump(H/'predecessor-bindings.json',bindings)
files=sorted(p for p in W.rglob('*') if p.is_file());dump(H/'package-inputs.json',[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files])
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('Pinned',len(files),'files; all seven predecessor digests match.')
