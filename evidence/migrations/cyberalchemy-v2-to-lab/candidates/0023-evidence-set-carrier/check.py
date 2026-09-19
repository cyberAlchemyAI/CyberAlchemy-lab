"""Inspect an exact evidence inventory without deriving a conclusion."""
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
    for ref in artifact['semantic_definition_bindings']+load(ROOT/'contracts.json')['schemas']: resolve(ref)
    Draft202012Validator(load(PACKAGE/'schema.json')).validate(record)
    questions={x['question_id']:x for x in record['questions']}
    need(len(questions)==len(record['questions']),'Duplicate question')
    ids=set(); paths=set(); digests=set()
    coverage={ident:{'supporting':[],'counterevidence':[],'context':[],'gaps':[]} for ident in questions}
    for member in record['members']:
        need(member['member_id'] not in ids,'Duplicate member identity'); ids.add(member['member_id'])
        path=resolve(member['binding']); digest=member['binding']['sha256']
        need(path not in paths and digest not in digests,'Repeated file or content is not distinct evidence'); paths.add(path); digests.add(digest)
        seen=set()
        for contribution in member['contributions']:
            question=contribution['question_ref']; need(question in questions,'Unknown contribution question')
            need(question not in seen,'A member needs one unambiguous role per question'); seen.add(question)
            coverage[question][contribution['role']].append(member['member_id'])
    gaps=set()
    for gap in record['gaps']:
        question=gap['question_ref']; need(question in questions,'Unknown gap question')
        key=(question,gap['missing']); need(key not in gaps,'Duplicate gap'); gaps.add(key)
        coverage[question]['gaps'].append(gap)
    need(all(any(parts.values()) for parts in coverage.values()),'Question lacks evidence or an explicit gap')
    return {'set_id':record['set_id'],'inventory_valid':True,'members_verified':len(ids),'question_coverage':coverage,'authority_effect':'none','evidence_sufficiency_proven':False,'roles_independently_verified':False,'conclusion_established':False,'experiment_execution_proven':False,'claim_ceiling':'Exact inventory and declared coverage only; no relevance, truth, sufficiency or conclusion proof.'}

if __name__=='__main__':
    try:
        need(len(sys.argv)==2,'Usage: check.py evidence-set-record.json')
        result=assess(read_input(Path(sys.argv[1]))); code=0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none'}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); sys.exit(code)
