"""Import the bounded implementation binding; preserve partial runtime evidence. See README.md."""
import json,os,subprocess,sys,tarfile
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0070-essays-implementation-binding-preparation';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0071';PACKAGE=STORE/'package';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';PREFIX=BASE+'conformance/implementation-binding';IMPL=BASE+'implementation'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
r=tool.read
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 s=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=s:raise ValueError('Artifact drift: '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def build():
 for folder in [PREV,CAPS]:
  for b in r(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as a:a.extractall(PACKAGE,filter='data')
 for b in r(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 p=PACKAGE/PREFIX;b=r(p/'BINDING.json');t=r(p/'TRACEABILITY.json');surfaces=b['implementation_surfaces'];entries=t['entries'];manifest=r(p/'IMPLEMENTATION-MANIFEST.json');mapped=r(HERE/'mapping-evidence.json')
 if len(surfaces)!=len({s['surface_id'] for s in surfaces}) or any('unmapped' in s['surface_id'] or 'unassigned' in s['surface_id'] for s in surfaces):raise ValueError('Invalid surface inventory')
 if len(entries)!=20 or any(e['posture']!='partial' for e in entries):raise ValueError('Proof state escalation')
 for e in mapped['new_model_mappings']:
  file=PACKAGE/IMPL/e['file']
  if tool.sha(file)!=e['sha256'] or e['selector'] not in file.read_text():raise ValueError('Mapping evidence drift')
  surface=next(s for s in surfaces if s['surface_id']==e['surface_id'])
  if e['file'] not in surface['files'] or e['system_node'] not in surface['system_nodes']:raise ValueError('Mapping endpoint mismatch')
 result=subprocess.run([sys.executable,str(p/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 if result.returncode or result.stdout!=r(HERE/'source-validation.json')['stdout']:raise ValueError('Source validator drift')
 for e in r(PREV/'package-inputs.json'):
  if e['path'].startswith(IMPL+'/') and tool.sha(PACKAGE/e['path'])!=e['sha256']:raise ValueError('Implementation changed')
 cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ESSAYS-AGENT-RUNTIME');registry=tool.load_registry()
 if cap['source_record']!=r(PACKAGE/'cyberAlchemy-v2/essays/capabilities/essays-agent-runtime.product-capability.json'):raise ValueError('Capability drift')
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
 refs=['package/'+PREFIX+'/BINDING.json#/implementation_surfaces/'+str(i) for i in range(len(surfaces))]+['package/'+PREFIX+'/TRACEABILITY.json#/entries/'+str(i) for i in range(len(entries))]
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/essays-implementation#ontology','name':'Essays Exact Implementation Binding','version':'source-qualified-0071','concept_refs':refs,'relation_ids':[],'boundaries':['Source implementation surfaces and obligation trace rows are records, not newly invented graph relations.','Source-inspected mappings and local checks remain partial evidence, not independent conformance.','Historical residue and separate Windows adapter binding retain their original provenance.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/essays-implementation#context','purpose':'Bind Essays runtime design and obligations to exact implementation files and bounded local evidence.','identity_boundary':'Candidate exact implementation binding with partial realization and explicit remaining evidence gaps.','profile_ref':'package/'+PREFIX+'/PROFILE.json','relevance':[cap['capability']['node_id'],ontology['node_id'],r(HERE.parent/'0069-essays-conformance-bridge-import/context.json')['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'contracts':contracts,'counts':{'implementation_files':manifest['file_count'],'surfaces':len(surfaces),'obligations':20,'system_nodes':18,'partial_trace_rows':20,'historical_residue':14},'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'source_validation':bind(HERE/'source-validation.json'),'mapping_evidence':bind(HERE/'mapping-evidence.json'),'local_checks':[bind(f) for f in sorted((HERE/'checks').glob('*.json'))],'authority_effect':'none','limitations':['Local checks do not establish cross-client parity, crash recovery coverage or independent conformance.','Desktop compilation timed out after missing pkg-config/DBus prerequisite diagnostics; native Windows and live browser/Wasmtime execution remain unverified.','Historical residue is retained, not asserted as current fact; current check receipts supersede obsolete environment statements.','Nested Windows adapter binding is preserved source material and has not been validated or imported as a separate context.']}
 for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
