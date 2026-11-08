"""Validate generated candidate Definition records against the local source cut."""
from pathlib import Path
import hashlib, importlib.util, json, os
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
LAB=Path(os.environ.get('CYBERALCHEMY_LAB_ROOT',str(ROOT.parent/'CyberAlchemy-lab')))
TYPE=LAB/'authority/artifact-types/definition/v1'
SOURCE=ROOT/'model/definitions.json'
OUT=ROOT/'model/definition-records'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads(SOURCE.read_text(encoding='utf-8'))['definitions']
index=json.loads((OUT/'index.json').read_text(encoding='utf-8'))
assert index['count']==len(source)==len(index['records'])==86
assert index['source_sha256']==sha(SOURCE)
assert index['artifact_type_ref']=='cal.artifact-type.definition/v1'
assert len({x['definition_id'] for x in index['records']})==86
spec=importlib.util.spec_from_file_location('ea_definition_generator',TYPE/'generator.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
schema=json.loads((TYPE/'schema.json').read_text())
validator=Draft202012Validator(schema)
for i,(d,entry) in enumerate(zip(source,index['records'])):
 assert entry['definition_id']==d['id'] and entry['source_selector']=='/definitions/'+str(i)
 path=ROOT/entry['record_ref'];record=json.loads(path.read_text(encoding='utf-8'))
 errors=list(validator.iter_errors(record))
 assert not errors,(d['id'],[e.message for e in errors])
 assert record['definition_id']==d['id'] and record['term']==d['term']
 assert record['voices']['scientific_formal']['normative_statement']==d['statement']
 assert record['voices']['scientific_formal']['formal_expression']==d.get('formal_expression')
 assert record['voices']['scientific_formal']['notation']==[{'symbol':k,'meaning':v} for k,v in d.get('notation',{}).items()]
 assert record['boundaries']==record['voices']['scientific_formal']['boundary_conditions']==d['boundaries']
 assert record['scope']['applicability']==d['scope']
 assert record['source_refs'][0]['content_sha256']==index['source_sha256']
 assert record['source_refs'][0]['selector']==entry['source_selector']
 assert record['schema_digest']==sha(TYPE/'schema.json')
 assert record['source_direction']['generator_sha256']==sha(TYPE/'generator.py')
 assert record['index_entry']=={'index_ref':'model/definition-records/index.json','entry_id':d['id']}
 assert record['voices']['plain_language']['normative'] is False
 assert record['voices']['domain_context']['normative'] is False
 assert (ROOT/entry['projection_ref']).read_text(encoding='utf-8')==module.render(record)
 assert entry['status']=='candidate-unadmitted' and entry['authority_effect']=='none'
assert sum(x['review_route']=='lab-reuse-semantic-review' for x in index['records'])==36
assert sum(x['review_route']=='project-local-semantic-review' for x in index['records'])==50
print('PASS: 86 project-scoped Definition/v1 candidates match local source, selected schema and generated projections; index and review routes close')
