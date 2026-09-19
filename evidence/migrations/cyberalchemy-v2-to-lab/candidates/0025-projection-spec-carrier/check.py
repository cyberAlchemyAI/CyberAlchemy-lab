"""Verify exact projection bytes against a bound candidate specification."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator
from support import ROOT, LAB, PACKAGE, load, sha, need
from generate import read, project, encoded

def assess(spec_path,view_path):
    artifact=load(PACKAGE/'artifact.json')
    need(sha(PACKAGE/'schema.json')==artifact['schema_digest'],'Contract drift')
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']:
        need(sha(LAB/ref['path'])==ref['sha256'],'Contract or Definition drift')
    spec=read(spec_path); Draft202012Validator(load(PACKAGE/'schema.json')).validate(spec)
    need(view_path.resolve()!=spec_path.resolve() and view_path.resolve()!=(LAB/spec['source']['path']).resolve(),'View must be separate from source and specification')
    expected=project(spec_path)
    need(view_path.read_bytes()==encoded(expected),'View differs from deterministic projection')
    return {'projection_id':spec['projection_id'],'view_matches':True,'selected_fields':len(spec['fields']),'omitted_fields':len(spec['omissions']),'authority_effect':'none','view_authority':'none','source_modified':False,'view_activated':False,'semantic_fidelity_proven':False,'claim_ceiling':'Exact selected-field projection only; no semantic completeness, authority transfer or activation.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'Usage: check.py projection-spec-record.json view.json')
        result=assess(Path(sys.argv[1]),Path(sys.argv[2])); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
