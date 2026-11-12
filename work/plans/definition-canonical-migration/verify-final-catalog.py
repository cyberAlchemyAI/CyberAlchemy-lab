from pathlib import Path
import json,hashlib,tarfile,subprocess,tempfile
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
load=lambda p:json.loads((R/p).read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
mapping=load('work/plans/definition-catalog-v2-layout/MAPPING.json')
selection=load('authority/definitions/current.json')
def exact(b):
 raw=(R/b.get('path',b.get('ref'))).read_bytes()
 assert sha(raw)==b['sha256'] and len(raw)==int(b['bytes']),b
 return raw
registry=json.loads(exact(selection['registry']));source=json.loads(exact(selection['source']))
assert len(registry['entries'])==377 and len(registry['current_lookup'])==188
original=load('authority/admissions/shared-definitions-records-0076/registry.json')
for e in original['entries']:
 exact(e['body'])
 retained=next(n for n in registry['entries'] if (n['definition_id'],n['version'])==(e['definition_id'],e['version']))
 assert retained['body']==e['body']
auth=load('docs/decisions/0077-definition-v2-canonical-migration/authorization.json')
assert len(auth['accepted_definitions'])==183
for a in auth['accepted_definitions']:
 exact(a['source'])
 entry=next(e for e in registry['entries'] if e['definition_id']+'@'+e['version']==a['version'])
 assert entry['body']==a['source']
 decision=json.loads(exact(entry['owner_disposition']))
 assert decision['outcome']=='Accepted' and decision['original']==a['source']
schema=load('authority/artifact-types/definition/v2/schema.json');validator=Draft202012Validator(schema)
def pointer(value,p):
 for part in p.lstrip('/').split('/') if p else []:
  key=part.replace('~1','/').replace('~0','~');value=value[int(key)] if isinstance(value,list) else value[key]
 return value
def leaves(v,p=''):
 if isinstance(v,dict) and v:
  for k,w in v.items():yield from leaves(w,p+'/'+k.replace('~','~0').replace('/','~1'))
 elif isinstance(v,list) and v:
  for i,w in enumerate(v):yield from leaves(w,p+'/'+str(i))
 else:yield p
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
lineages=0;homes={}
with tarfile.open(R/'evidence/definitions/full-v2-layout/define-packages.tar.gz','r:gz') as archive,tempfile.TemporaryDirectory(prefix='canonical-all-definitions-') as temp:
 for row in mapping['entries']:
  directory=R/row['target'];raw=(directory/'definition.json').read_bytes();body=json.loads(raw);validator.validate(body)
  current=registry['current_lookup'][row['definition_id']];assert current==row['definition_id']+'@'+row['version']
  entry=next(e for e in registry['entries'] if e['definition_id']+'@'+e['version']==current);assert entry['body']['sha256']==sha(raw)
  location=source['locations'][current];assert location['body'].get('ref',location['body'].get('path'))==row['target']+'/definition.json';assert location['body']['sha256']==sha(raw)
  fields=json.loads((directory/'field-lineage.json').read_bytes())['fields'];selectors=[f['target_selector'] for f in fields]
  assert len(set(selectors))==len(selectors) and set(selectors)==set(leaves(body))
  for f in fields:
   b=f['source_binding'];origin=archive.extractfile(row['definition_id']+'/pack/inputs/'+b['path']).read()
   assert sha(origin)==b['sha256'] and len(origin)==int(b['bytes'])
   assert canon(pointer(json.loads(origin),f['source_selector']))==canon(pointer(body,f['target_selector']))
   lineages+=1
  output=Path(temp)/'DEFINITION.md'
  rendered=subprocess.run(['python3','-B',str(R/'authority/artifact-types/definition/v2/generator.py'),str(directory/'definition.json'),'--output',str(output)],capture_output=True)
  assert rendered.returncode==0,rendered.stderr
  assert output.read_bytes()==(directory/'DEFINITION.md').read_bytes()
  homes[row['workspace_home']]=homes.get(row['workspace_home'],0)+1
assert lineages==13536,lineages
receipt={'status':'PASS','admitted_conversions':183,'current_full_v2':188,'admitted_versions':377,'original_bodies_exact':194,'independent_renderer_checks':188,'exact_leaf_lineages':lineages,'workspace_counts':homes,'registry':selection['registry'],'source':selection['source']}
(P/'CATALOG-VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
