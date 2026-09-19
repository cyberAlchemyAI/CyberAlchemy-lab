import json,sys,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';STORE=ROOT/'.local/ontology-context-import-0049';CAPS=HERE.parent/'0035-definition-card-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
PREFIX='cyberAlchemy-v2/agent-reasoning-engine/framings/'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_graph(nodes,relations):
 ids={n['id']:n for n in nodes['nodes']};types={t['type']:t for t in relations['relation_types']}
 if len(ids)!=len(nodes['nodes']) or len(types)!=len(relations['relation_types']):raise ValueError('Duplicate identity')
 rs=relations['relations']
 if len({r['id'] for r in rs})!=len(rs):raise ValueError('Duplicate relation')
 for n in ids.values():
  if n['authority_effect']!='none':raise ValueError('Concept authority escalation')
 for r in rs:
  if r['source'] not in ids or r['target'] not in ids:raise ValueError('Dangling endpoint')
  if r['type'] not in types:raise ValueError('Unknown relation type')
  t=types[r['type']]
  if ids[r['source']]['kind'] not in t['source_kinds'] or ids[r['target']]['kind'] not in t['target_kinds']:raise ValueError('Wrong endpoint kind')
  if r['authority_effect']!='none':raise ValueError('Relation authority escalation')
def source_validation(root):
 spec=importlib.util.spec_from_file_location('framings_source',root/PREFIX/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 result=v.validate();result.pop('validated_at')
 if result['status']!='PASS':raise ValueError(result)
 return result

def build():
 for folder in [CAPS,HERE.parent/'0048-agent-reasoning-context-import']:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();snapshots=[]
 for b in tool.read(HERE/'plan.json')['sources']:
  src=SOURCE/b['path']
  if tool.sha(src)!=b['sha256']:raise ValueError('Source drift')
  for folder in [HERE/'source-root',STORE/'source-root']:
   p=folder/'cyberAlchemy-v2'/b['path'];p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists() and p.read_bytes()!=src.read_bytes():raise ValueError('Snapshot drift')
   p.write_bytes(src.read_bytes())
  snapshots.append(bind(HERE/'source-root/cyberAlchemy-v2'/b['path']))
 p=HERE/'source-root'/PREFIX;r=tool.read
 validation=source_validation(HERE/'source-root');dump(HERE/'source-validation.json',validation)
 nodes=r(p/'nodes.json');relations=r(p/'relations.json');profile=r(p/'profile.json');validate_graph(nodes,relations)
 cap=next(c for c in r(CAPS/'imports.json') if c['id']==profile['product_capability_ref'])
 parent=next(c for c in r(CAPS/'imports.json') if c['id']==profile['parent_capability_ref'])
 if cap['source_record']!=r(p/'product-capability.json') or parent['source_record']!=r(HERE/'source-root/cyberAlchemy-v2/agent-reasoning-engine/product-capability.json'):raise ValueError('Capability source mismatch')
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':profile['package_owner']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/contextual-framings#ontology','name':'Contextual Framings','version':'source-snapshot-0049','concept_refs':['source-root/'+PREFIX+'nodes.json#/nodes/'+str(i) for i in range(len(nodes['nodes']))],'relation_ids':[r['id'] for r in relations['relations']],'boundaries':['Source-qualified business model for perspectives and bounded analogies.','No runtime or measured cognitive improvement claim; four source residue items remain.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/contextual-framings#context','purpose':cap['capability']['outcome'],'identity_boundary':'Context-appropriate explanations retain source limits, provenance, uncertainty, exclusions and expiry.','profile_ref':'source-root/'+PREFIX+'profile.json','relevance':[cap['capability']['node_id'],parent['capability']['node_id'],ontology['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'source_graph':{'nodes':nodes['nodes'],**relations},'source_validation':validation,'counts':validation['counts'],'snapshots':snapshots,'contracts':contracts,'capability_binding':bind(CAPS/'imports.json'),'parent_capability_id':parent['id'],'authority_effect':'none','limitations':['Uses existing admitted migration-scoped header contracts; model remains candidate-unadmitted.','No measured reduction in cognitive effort or runtime implementation is established.','Historical source receipt remains evidence only.']}
 for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle)
 return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
