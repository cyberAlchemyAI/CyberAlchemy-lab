"""Inspect exact directed artifact-to-Definition bindings."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PREVIOUS, PACKAGE, load, sha, need

def read_input(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'Duplicate JSON key: '+key); result[key]=value
        return result
    def invalid(value): raise ValueError('Invalid JSON constant: '+value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=invalid)

def resolve(ref):
    path=(LAB/ref['path']).resolve()
    need(path.is_relative_to(LAB.resolve()),'Binding escapes Lab')
    need(sha(path)==ref['sha256'],'Bound bytes changed: '+ref['path'])
    return path

def assess(record):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']+load(PREVIOUS/'manifest.json')['materials']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    source_path=resolve(record['source']['binding']); target_path=resolve(record['target']['binding'])
    need(source_path!=target_path,'Endpoints must be distinct')
    source=read_input(source_path); target=read_input(target_path)
    need(source.get('classification',{}).get('artifact_type_ref')=='cal.artifact-type.artifact-type/v2','Source must be an Artifact Type/v2 record')
    need(source['artifact_type_ref']==record['source']['object_ref'],'Source identity mismatch')
    root=resolve(source['artifact_type_root_binding'])
    need(root==LAB/'authority/artifact-types/artifact-type/v2/artifact.json','Unsupported Artifact Type root')
    schema_path=LAB/'authority/artifact-types/definition/v1/schema.json'
    need(target.get('schema_digest')==sha(schema_path),'Target Definition contract mismatch')
    Draft202012Validator(load(schema_path)).validate(target)
    target_ref=target['definition_id']+'@'+target['version']
    need(target_ref==record['target']['object_ref'],'Target identity mismatch')
    need(record['relation_id'] not in [record['source']['object_ref'],target_ref],'Relation identity collapses into endpoint')
    matches=[x for x in source['semantic_definition_bindings'] if x['definition_ref']==target_ref]
    need(len(matches)==1 and source['semantic_definition_refs'].count(target_ref)==1,'Source must declare exactly one matching Definition binding')
    need(resolve(matches[0])==target_path and matches[0]['sha256']==record['target']['binding']['sha256'],'Source binding disagrees with target')
    evidence=set()
    for ref in record['evidence']:
        path=resolve(ref); need(path not in evidence,'Duplicate evidence'); evidence.add(path)
    return {'relation_id':record['relation_id'],'binding_conforms':True,'source':record['source'],'target':record['target'],'direction':record['direction'],'relation_kind_ref':record['relation_kind_ref'],'owner_route':record['owner_route'],'declared_effect':record['declared_effect'],'authority_effect':'none','owner_authenticated':False,'owner_local_semantics_interpreted':False,'relation_kind_admitted':False,'effect_executed':False,'claim_ceiling':'Exact directed binding evidence only; no owner-local meaning, relation-kind admission or endpoint promotion.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py typed-relation-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
