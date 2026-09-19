"""Import a source-qualified system model with explicit successor build evidence.
Open questions and claim limits: README.md.
"""
import hashlib,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STORE=ROOT/'.local/ontology-context-import-0068';PACKAGE=STORE/'package';BUILD=STORE/'build';PREFIX='cyberAlchemy-v2/essays/development/agent-runtime/domainspec';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0067-essays-architecture-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
r=tool.read
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 content=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=content:raise ValueError('Existing artifact differs: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def model_check(m):
 if m['authority_effect']!='none':raise ValueError('Authority escalation')
 for rows,key in [(m['system_nodes'],'id'),(m['relations'],'id'),(m['views'],'view_id')]:
  ids=[x[key] for x in rows]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate identity')
 ids={x['id'] for x in m['system_nodes']}
 for e in m['relations']:
  if e['source'] not in ids or e['target'] not in ids:raise ValueError('Unresolved relation')
 for v in m['views']:
  if len(v['node_ids'])!=len(set(v['node_ids'])) or not set(v['node_ids'])<=ids:raise ValueError('Unresolved view')
 if next(v for v in m['views'] if v['view_id']=='platform-process-and-deployment')['node_ids']:raise ValueError('Invented deployment model')
 if len(m['residue'])!=2:raise ValueError('Residue lost')
def build():
 for folder in [CAPS,PREV,HERE.parent/'0061-d65-revision2-context-import']:
  for b in r(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as a:a.extractall(PACKAGE,filter='data')
 for b in r(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 p=PACKAGE/PREFIX;pre=r(p/'PREDECESSORS.json');old=r(p/'generated/system-ontology.json');oldreceipt=r(p/'generated/compile-receipt.json');model_check(old)
 for key,b in r(HERE/'predecessor-bindings.json').items():
  h=hashlib.sha256()
  if 'material_root' in b:
   for name in b['files']:h.update(str(Path(name).relative_to(b['material_root'])).encode()+b'\0'+(PACKAGE/name).read_bytes()+b'\0')
  else:h.update((PACKAGE/b['files'][0]).read_bytes())
  if h.hexdigest()!=b['actual'] or b['actual']!=pre[key]:raise ValueError('Predecessor digest mismatch')
 if old['predecessor_digests']!=pre or oldreceipt['predecessor_digests']!=pre:raise ValueError('Generated predecessor drift')
 for key,name in [('compiled_graph_sha256','domain.graph.json'),('system_ontology_sha256','system-ontology.json')]:
  if oldreceipt[key]!=tool.sha(p/'generated'/name):raise ValueError('Historical receipt mismatch')
 oldgraph=r(p/'generated/domain.graph.json')
 for s in oldgraph['source_manifest']['sources']:
  file=p/'authored'/s['relative_path']
  if tool.sha(file)!=s['sha256'] or file.stat().st_size!=s['size_bytes']:raise ValueError('Authored manifest drift')
 shutil.copytree(PACKAGE,BUILD,dirs_exist_ok=True)
 script=BUILD/PREFIX/'scripts/compile_once.ts';loader=BUILD/'node_modules/tsx/dist/loader.mjs'
 runs=[];outputs=[]
 for _ in range(2):
  result=subprocess.run(['node','--import',str(loader),str(script)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  if result.returncode:raise ValueError(result.stderr)
  runs.append(json.loads(result.stdout));outputs.append({f.name:f.read_bytes() for f in (BUILD/PREFIX/'generated').iterdir()})
 if outputs[0]!=outputs[1]:raise ValueError('Successor rebuild drift')
 new=r(BUILD/PREFIX/'generated/system-ontology.json');model_check(new)
 if {k:v for k,v in old.items() if k!='source_graph_sha256'}!={k:v for k,v in new.items() if k!='source_graph_sha256'}:raise ValueError('System semantics changed')
 compiler='projects/domainspec-v2/impl/cli/src/input/project-model.ts'
 if (PACKAGE/compiler).read_bytes()!=(ROOT/'.local/ontology-context-import-0061/package'/compiler).read_bytes():raise ValueError('Pinned compiler differs from 0061')
 for name in outputs[0]:
  dump(HERE/'successor'/name,r(BUILD/PREFIX/'generated'/name));dump(STORE/'successor'/name,r(BUILD/PREFIX/'generated'/name))
 graph=r(BUILD/PREFIX/'generated/domain.graph.json');changed=sorted(k for k in oldgraph.keys()|graph.keys() if oldgraph.get(k)!=graph.get(k))
 evidence={'result':'PASS','runs':runs,'node_version':subprocess.check_output(['node','--version'],text=True).strip(),'original_compiler_sha256':oldreceipt['domainspec_compiler_sha256'],'successor_compiler':{'path':compiler,'sha256':tool.sha(PACKAGE/compiler)},'changed_graph_fields':changed,'system_semantics_unchanged':True,'reproduction_scope':'Two invocations, each compiling twice, at the pinned local build path; graph embeds absolute project_root, so byte identity is path-dependent.','authority_effect':'none'}
 dump(HERE/'construction-evidence.json',evidence)
 cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME')
 if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability changed')
 registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-system#ontology','name':'Essays Agent Runtime System Model','version':'source-qualified-0068','concept_refs':['successor/system-ontology.json#/system_nodes/'+str(i) for i in range(len(new['system_nodes']))],'relation_ids':['essays-system:'+e['id'] for e in new['relations']],'boundaries':['Authored operation and guard meanings preserved; generated compiler metadata is an explicit successor.','Construction evidence does not prove implemented behavior or independent conformance.','Deployment view is empty and source residue remains unchanged.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-system#context','purpose':'Trace Essays workspace state, proposal decisions and supervised browser actions through the authored system model.','identity_boundary':'Source-qualified system design and local construction evidence only.','profile_ref':'package/'+PREFIX+'/PREDECESSORS.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(PREV/'context.json')['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'counts':{'concepts':18,'relations':38,'views':9,'residue':2,'predecessor_digests':7},'contracts':contracts,'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'predecessors':bind(HERE/'predecessor-bindings.json'),'construction_evidence':bind(HERE/'construction-evidence.json'),'capability_binding':bind(CAPS/'imports.json'),'architecture_context':bind(PREV/'bundle.json'),'relation_bindings':[{'relation_id':'essays-system:'+e['id'],'source_ref':'successor/system-ontology.json#/relations/'+str(i)} for i,e in enumerate(new['relations'])],'authority_effect':'none','limitations':['Original compiler bytes have not been recovered; original receipt preserved as historical evidence.','Product and writing predecessor material fingerprints match; their full ontology validation and import remain separate.','Compiled graph embeds an absolute build path; byte reproducibility is limited to that path.','No runtime execution, independent conformance, ontology admission or external effect is established.']}
 for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle)
 return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
