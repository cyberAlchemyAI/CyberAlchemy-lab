"""Generate a deterministic selected-field view without modifying its source."""
import json
from support import ROOT, LAB, load, sha, binding, need

def read(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'Duplicate JSON key: '+key); result[key]=value
        return result
    def invalid(value): raise ValueError('Invalid JSON constant: '+value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=invalid)

def project(spec_path):
    spec=read(spec_path); source_path=(LAB/spec['source']['path']).resolve()
    need(source_path.is_relative_to(LAB.resolve()),'Source escapes Lab')
    need(sha(source_path)==spec['source']['sha256'],'Source bytes changed')
    source=read(source_path); need(isinstance(source,dict),'Source must be a JSON object')
    selected=[x['source_field'] for x in spec['fields']]; outputs=[x['view_field'] for x in spec['fields']]; omitted=[x['source_field'] for x in spec['omissions']]
    need(len(selected)==len(set(selected)) and len(outputs)==len(set(outputs)),'Duplicate field mapping')
    need(len(omitted)==len(set(omitted)),'Duplicate omission')
    need(not set(selected)&set(omitted) and set(selected)|set(omitted)==set(source),'Fields must partition the exact source')
    return {'schema_version':'cal-generated-field-view/v1','projection_id':spec['projection_id'],'specification':binding(spec_path.resolve()),'source':spec['source'],'authority_effect':'none','status':'derived-non-authoritative','data':{x['view_field']:source[x['source_field']] for x in spec['fields']}}

def encoded(value): return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
