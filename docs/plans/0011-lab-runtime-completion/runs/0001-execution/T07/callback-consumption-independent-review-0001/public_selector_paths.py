from pathlib import Path
import json,hashlib,posixpath
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');base=Path('product/lab/release-candidates/v1/interface/custody-correction-v4');manifest=json.loads((ROOT/base/'engine-manifest.json').read_bytes());profile=json.loads((ROOT/manifest['profile_binding']['path']).read_bytes());names=set();docs={};reads={}
def read(name,expected=None):
 name=posixpath.normpath(name);assert not name.startswith('../')and not Path(name).is_absolute();assert not name.endswith('.snapshot');names.add(name)
 if name.endswith('.json')and name not in docs:
  raw=(ROOT/name).read_bytes();docs[name]=json.loads(raw);reads[name]=hashlib.sha256(raw).hexdigest()
 if expected is not None and name in reads:assert reads[name]==expected,('public selector metadata changed',name)
 return docs.get(name)
def schema(name,expected=None):
 name=posixpath.normpath(name)
 if name in names:
  if expected is not None and name in reads:assert reads[name]==expected
  return
 doc=read(name,expected)
 def walk(v):
  if isinstance(v,dict):
   ref=v.get('$ref','')
   if ref and not ref.startswith('#'):
    assert '://'not in ref;schema(posixpath.join(posixpath.dirname(name),ref.split('#')[0]))
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(doc)
roots=[];operational=[]
for key,target in [('roots',roots),('operational_roots',operational)]:
 for binding in profile[key]:
  bundle=read(binding['path'],binding['sha256']);parent=posixpath.dirname(binding['path']);target.append((parent,bundle))
  for row in bundle['files']:read(posixpath.join(parent,row['path']),row['sha256'])
BASE='authority/admissions/governance-transaction-surface/v1';types=docs[BASE+'/registries/artifact-type-registry.json'];definitions=docs[BASE+'/registries/definition-registry.json'];relations=docs[BASE+'/registries/relation-kind-registry.json'];read('authority/definitions/registry.json',reads[BASE+'/registries/definition-registry.json'])
for row in types['admitted_contracts']:read(row['artifact_path'],row['artifact_sha256']);schema(row['schema_path'],row['schema_sha256'])
for row in definitions['entries']:read(row['path'],row['sha256'])
for row in relations['entries']:read(row['instance_path'],row['instance_sha256'])
for parent,bundle in roots[:-1]+operational:
 for leaf in ['artifact-instance-admission.json','typed-relation-admission.json']:
  for row in docs[parent+'/'+leaf]['entries']:read(row['admitted_instance_path'],row.get('admitted_instance_sha256',row.get('sha256')))
selection=profile['current_selection'];read(selection['lookup']['path'],selection['lookup']['sha256'])
for path,doc in list(docs.items()):
 binding=doc.get('authorization')if isinstance(doc,dict)else None
 if isinstance(binding,dict)and 'path'in binding and 'sha256'in binding:
  name=binding['path']
  if not(ROOT/name).exists():name=posixpath.join(posixpath.dirname(path),name)
  read(name,binding['sha256'])
for kind in ['project-semantic-event-history','project-governance-event-history']:
 history=docs[selection['history_base']+'/'+kind+'.json']
 for event in history['payload']['events']:
  for row in event.get('material_refs',[]):read(row['path'],row['sha256'])
  if 'authorization_ref'in event:read(event['authorization_ref'],event['authorization_sha256'])
  name=event.get('record_ref')
  if name and(ROOT/name).is_file():read(name)
for row in profile['implementation_bindings']:read(row['path'])
for name in profile.get('runtime_materials',[]):read(name)
(Path(__file__).absolute().parent/'baseline-selector-paths.json').open('x').write(json.dumps({'profile_binding':manifest['profile_binding'],'names':sorted(names),'metadata_documents':reads,'capture_source':'product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/sources.py','actual_capture_or_freshness_called':False},sort_keys=True))
print(json.dumps({'selected_logical_paths':len(names),'public_JSON_metadata_read':len(reads),'API17_names':[p for p in names if p.startswith('product/lab/release-candidates/v1/interface/api-integration-v17/')]}))
