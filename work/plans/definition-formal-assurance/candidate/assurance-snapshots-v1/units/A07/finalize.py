"""Bind actual A07 unit completion evidence; do not admit source meanings."""
import hashlib
import json
import re
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;sys.path.insert(0,str(UNIT));import pilot_spec as p
ROOT=p.ROOT;BASE=UNIT.parent.parent;IMPL=p.IMPL


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    log=(UNIT/'test-output.txt').read_text();match=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK\s*$',log)
    if match is None:raise ValueError('Final passing test output required')
    context=json.loads((UNIT/'context.json').read_text());spec=json.loads((BASE/'pilot-v2/interpretation.json').read_text());source=p.bind_sources(spec);inputs=[{key:row[key] for key in ['path','sha256']} for row in context['sources']]
    for row in inputs:
        if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source/context input changed: '+row['path'])
    outputs=[binding(BASE/'pilot-v2/interpretation.json'),binding(IMPL/'tests/test_A07.py')]+[binding(path) for path in sorted(UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    receipt={'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'A07.1','authority_effect':'none','goal_status':'active','inputs':inputs,'outputs':outputs,'task_result':'PASS for source-backed partial record semantics, explicit alternatives and exact move/assignment binding; whole-definition fidelity remains pending','test_result':'PASS','test_count':int(match[1]),'test_seconds':float(match[2]),'actual_source_binding_check':source,'criterion_results':[{'criterion':'Separate independent owner grants, claims and rights/responsibilities','result':'PASS','evidence':'Candidate record types and denotation; ungranted assertions, unclaimed grants, assigned duties without permission and tagged overlap controls.'},{'criterion':'Define empty, unknown, deferred, local and incomplete provenance','result':'PASS','evidence':'Distinct information/trail states, source-star interpretation alternative, routed gaps and exact local admission-use profile checks.'},{'criterion':'Bind each move to exact subject, before/after states and active assignments','result':'PASS','evidence':'Full state revision/digest binding and exact intended/recorded component changes plus complete permit/duty delta denominators.'},{'criterion':'Source-backed alternatives and realistic instances/counterexamples','result':'PASS within partial candidate scope','evidence':'Seven exact current sources; 166 units accounted; retained FID-RESP-001 and FID-PROV-EMPTY-001; eleven hypothetical worked states.'},{'criterion':'Reject move/record mismatch and unrecorded grant changes','result':'PASS','evidence':'Stale snapshot/control bindings, silent frame changes, missing assignment-delta records and outside-profile boundary mutation controls.'}], 'worked_controls':{'states':11,'moves':1,'source_packets':7,'source_units_accounted':166,'scope':'Hypothetical local records; no actual owner acts or fulfilled obligations asserted.'},'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Accepted as source-backed partial successor specification for A08, within the explicit conditional record semantics.','limitations':['Whole-definition natural-language fidelity and owner precedence decisions remain pending.','Normative/deontic fulfillment, full temporal behavior, delegation/revocation and arbitrary lineage composition remain unsupported.','Root and principal binding legitimacy are hypothetical defeasible premises.','Seven selected sources do not establish complete semantic dependency closure.','No full183 combined proof, actual grant/admission or project completion established.']},'full_project_completion':'not-established','next_ready_unit':'A08.1'}
    put(UNIT/'receipt.json',receipt)
    put(UNIT/'episode-status.json',{'authority_effect':'none','goal_status':'active','current_definitions':183,'admitted_source_versions':189,'new_candidate_unit':'A07.1','new_tests':int(match[1]),'new_source_backed_partial_definition_rules':7,'new_source_units_accounted':166,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'next_ready_unit':'A08.1','remaining':'Bounded pilot search/checker and independent replay, whole-source fidelity, full-family translations, semantic closure, solver/kernel and extension profiles, revision handling, combined global theory checks, owner review and final complete episode review.'})
    files=[binding(path) for folder in [BASE,IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    put(UNIT/'delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda row:row['path']),'claim_ceiling':'Exact candidate bytes and prior-file preservation only; no admitted semantics or completion claim.'})
    print(json.dumps({'result':'sealed-candidate','test_count':int(match[1]),'delivery_files':len(files),'source_definitions':7,'source_units':166,'goal_status':'active'}))


if __name__=='__main__':main()
