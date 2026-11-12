from pathlib import Path
import json,hashlib,importlib.util,sys,tarfile,gzip,io,copy
import jsonschema
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'implementation/artifact-runtime'));from exact_io import pointer,leaves
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
mapping=load(P/'MAPPING.json');layout=load(P/'LAYOUT-VERIFICATION.json');archive=load(P/'PACKAGES.json')
compressed=(R/archive['archive']['path']).read_bytes();assert sha(compressed)==archive['archive']['sha256']
payload=gzip.decompress(compressed);assert len(payload)<128*1024*1024
t=tarfile.open(fileobj=io.BytesIO(payload))
schema=load(R/'authority/artifact-types/definition/v2/schema.json');v=jsonschema.Draft202012Validator(schema)
spec=importlib.util.spec_from_file_location('original_definition_v2_generator',R/'authority/artifact-types/definition/v2/generator.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
registry=load(R/'authority/admissions/shared-definitions-records-0076/registry.json')
for original in registry['entries']:assert sha((R/original['body']['path']).read_bytes())==original['body']['sha256']
assert len(layout['entries'])==len(mapping['entries'])==188
assert len({x['definition_id']for x in layout['entries']})==188
rows=[];total_fields=0
for e in layout['entries']:
 row=next(x for x in mapping['entries']if x['definition_id']==e['definition_id']);file=R/e['path'];raw=file.read_bytes();d=json.loads(raw);old=load(R/row['source']['body']['path'])
 v.validate(d);assert d['schema_version']=='cyberalchemy-lab-definition/v2'
 assert row['folder_name']==file.parent.parent.name and d['version']==file.parent.name
 assert str(file.relative_to(R))==str(Path(row['workspace_home'])/'authority/definitions'/row['folder_name']/d['version']/'definition.json')
 assert sha(raw)==e['sha256']
 assert (file.parent/'DEFINITION.md').read_text()==g.render(d)
 assert {f.name for f in file.parent.iterdir()}=={'definition.json','DEFINITION.md','field-lineage.json','evidence.json'}
 for key in ['voices','scope','boundaries','term','aliases','semantic_owner_ref','typed_relations','primary_consumer_refs','evidence_refs','residue_refs','claim_ceiling']:assert d[key]==old[key],(d['definition_id'],key)
 if row['converted']:
  assert d['definition_id']==old['definition_id'] and d['version']!=old['version']
  assert d['source_refs'][:-1]==old['source_refs'] and d['source_refs'][-1]['content_sha256']==row['source']['body']['sha256']
 else:assert raw==(R/row['source']['body']['path']).read_bytes()
 lineage=load(file.parent/'field-lineage.json');observed=[x['target_selector']for x in lineage['fields']]
 assert len(observed)==len(set(observed)) and set(observed)==set(leaves(d))
 prefix=d['definition_id']+'/pack/inputs/'
 for f in lineage['fields']:
  binding=f['source_binding'];source=t.extractfile(prefix+binding['path']).read()
  assert sha(source)==binding['sha256'] and len(source)==binding['bytes']
  assert pointer(d,f['target_selector'])==pointer(json.loads(source),f['source_selector'])
 assert t.extractfile(prefix+'definition.json').read()==raw
 total_fields+=len(observed);rows.append({'definition_id':d['definition_id'],'fields_verified':len(observed),'status':'PASS'})
bad=copy.deepcopy(d);bad.pop('voices');assert list(v.iter_errors(bad))
bad=copy.deepcopy(d);bad['voices']['plain_language']['normative']=True;assert list(v.iter_errors(bad))
bad=copy.deepcopy(d);bad['schema_version']='cyberalchemy-lab-definition/v1';assert list(v.iter_errors(bad))
bad=copy.deepcopy(d);bad['typed_relations'].append({'relation_kind_ref':'relation.unsupported','from_ref':'x','to_ref':'y','owner_ref':'z'});assert list(v.iter_errors(bad))
result={'status':'PASS','definitions':188,'v2_successors':183,'existing_v2_exact':5,'original_admitted_bodies_unchanged':len(registry['entries']),'exact_field_lineages_verified':total_fields,'independent_renderer_checks':188,'schema_negative_regressions':4,'placement_checks':load(P/'PLACEMENT-VERIFICATION.json')['check_count'],'empty_lineage_regression':load(P/'EMPTY-LINEAGE-REGRESSION.json'),'workspace_counts':layout['workspaces'],'generation_complete':True,'canonical_registry_changed':False,'activation_complete':False,'activation_blockers':['Current native store source profile still references removed ontology-lifecycle path.','Previously selected implementation manifest differs from staged runtime source.','183 newly generated exact representations require their own review/disposition before canonical successor publication.'],'rows':rows}
(P/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:value for k,value in result.items()if k!='rows'}))
