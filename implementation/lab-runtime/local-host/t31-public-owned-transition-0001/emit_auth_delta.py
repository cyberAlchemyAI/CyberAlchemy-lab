"""Narrow maintained current-family owned-workflow authorization postimage."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

def sha(raw):return hashlib.sha256(raw).hexdigest()
def emit(base,out):
    raw=base.read_bytes();text=raw.decode()
    old="""        if transition:
            from .workflow_transition import validate_control as validate_transition
            source.require(value['workflow_source_control']==source.workflow_bindings(),'independent workflow source pins differ')
            validate_transition(value,self.schemas)
"""
    new="""        if transition:
            if value['source_name']==source.CURRENT_LEGACY_NAME:
                from .owned_workflow_transition import validate_control as validate_owned_transition
                validate_owned_transition(value,self.schemas)
            else:
                from .workflow_transition import validate_control as validate_transition
                source.require(value['workflow_source_control']==source.workflow_bindings(),'independent workflow source pins differ')
                validate_transition(value,self.schemas)
"""
    if text.count(old)!=1:raise ValueError('exact original workflow control branch required')
    text=text.replace(old,new,1)
    old_guard="source.require(not integrated and not transition,'current metadata cannot retarget integrated/workflow history policies')"
    if text.count(old_guard)!=1:raise ValueError('exact current metadata historical-source guard required')
    text=text.replace(old_guard,"source.require(not integrated,'current metadata cannot retarget integrated history policies')",1)
    ast.parse(text);out.mkdir(mode=0o700,parents=True,exist_ok=False)
    changed=text.encode();(out/'auth.py').write_bytes(changed)
    pins={'base_auth':{'path':str(base),'sha256':sha(raw)},'postimage_auth_sha256':sha(changed),
      'unchanged_predicates':['closed authenticated policy/schema fields','actual current metadata Source/period/principal permission','purpose and operations','independent technical authorization','strict historical workflow control/source branches','integrated history prohibition'],
      'new_branch':'Only current-family transition metadata validates independently selected private owned control. Reader policy authentication cannot install the Python Selection. Service requires actual separately installed typed selection or original strict handler refuses before claim.',
      'common_Service_positive_qualification':False,'authority_effect':'none'}
    (out/'DELTA-PINS.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n');return pins
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('base_auth',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args();print(json.dumps(emit(a.base_auth,a.output),sort_keys=True))
