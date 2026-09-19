"""Evaluate one pinned revision-2 prototype; return evidence without granting effects."""
import hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
GOV='cyberAlchemy-v2/ontology/governance/'
def read(path):return json.loads(path.read_text())
def evaluate(root,subject):
    binding=read(HERE/'successor-binding.json')
    result={'schema_version':'lab-d65-r2-candidate-evaluation/v1','subject':subject,'status':'NOT_EVALUABLE','scope':'prototype-consistency-and-request-eligibility','full_construction_conformance':'not_evaluable','product_approved':False,'authority_granted':False,'effect_authorized':False,'authority_effect':'none','errors':[]}
    if subject!=binding['subject_ref']:
        result['errors']=['SUBJECT_NOT_BOUND'];return result
    for artifact in binding['artifacts']:
        path=root/artifact['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']:
            result['errors']=['BOUND_INPUT_DRIFT:'+artifact['path']];return result
    constructions=read(root/GOV/'prototype-constructions.json');scaffolds=read(root/GOV/'ontology-scaffolds.json')
    if len(constructions['constructions'])!=1 or constructions['constructions'][0]['construction_id']!=subject:
        result['errors']=['EXACT_SINGLE_SUBJECT_REQUIRED'];return result
    path=root/GOV/'scripts/validate-prototype-construction.py'
    spec=importlib.util.spec_from_file_location('pinned_d65_r2',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    evidence=module.evaluate_registry(constructions,scaffolds,repository_root=root,check_files=True)
    result['status']=evidence['status'];result['source_evaluation']=evidence;result['errors']=evidence['errors']
    return result
