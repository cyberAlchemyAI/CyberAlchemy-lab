"""Seal A08 actual implementation evidence within its authorized candidate scope."""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parent.parent;IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
loader=importlib.util.spec_from_file_location('governance_v2',IMPL/'pilot-v2.py');v=importlib.util.module_from_spec(loader);loader.loader.exec_module(v)


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    log=(UNIT/'test-output.txt').read_text();match=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK\s*$',log)
    if match is None or int(match[1])!=42:raise ValueError('Final 42 passing test output required')
    context=json.loads((UNIT/'context.json').read_bytes());inputs=[{key:row[key] for key in ['path','sha256']} for row in context['sources']]
    for row in inputs:
        if binding(ROOT/row['path'])!=row:raise ValueError('Changed context input')
    prepared=v.prepare();v.verify_bindings(prepared);source=v.p.bind_sources(prepared['spec'],ROOT)
    worked=json.loads((UNIT/'worked-controls.json').read_bytes());statuses={row['case_id']:row['status'] for row in worked['searches']}
    if len(worked['searches'])!=10 or statuses['positive']!='witnesses-found' or statuses['full-range-budget-stop']!='resource-limit':raise ValueError('Actual control denominator/outcome mismatch')
    episode={'authority_effect':'none','goal_status':'active','current_definitions':183,'admitted_source_versions':189,'new_candidate_unit':'A08.1','new_tests':42,'selected_partial_source_definitions':7,'required_logical_queries':11,'positive_model_witnesses':11,'required_pending_gates':11,'finite_configurations':8640,'positive_search_configurations_examined':79,'full_configuration_audit':'incomplete-budget-stop; independent A09 audit pending','owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'next_ready_unit':'A09.1','remaining':'Independent record/projection replay and bounded full-domain audit, source-owner fidelity, full-family translations, semantic closure, solver/kernel and extension profiles, revision handling, combined global theory checks, owner review and complete final episode explanation.'}
    put(UNIT/'episode-status.json',episode)
    outputs=[binding(IMPL/'pilot-v2.py'),binding(IMPL/'tests/test_A08.py')]+[binding(path) for path in sorted(UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    receipt={'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'A08.1','authority_effect':'none','goal_status':'active','inputs':inputs,'outputs':outputs,'task_result':'PASS for isolated independently implemented finite record/projection search, within the exact declared conditional candidate profile','test_result':'PASS','test_count':int(match[1]),'test_seconds':float(match[2]),'actual_source_binding_check':source,'required_set_sha256':prepared['required']['required_set_sha256'],'criterion_results':[{'criterion':'Create isolated successor and preserve v1/prior candidate bytes','result':'PASS','evidence':'New A08 paths and exact A07 prior delivery preservation; no prior candidate/source rewrite.'},{'criterion':'Independent record and transition predicates against sealed signatures','result':'PASS','evidence':'A07 only supplies closed types/currentness; A08 never calls inspect_state/check_move. Selected nominal static projection, exact frame/assignment delta checks and independent A06 query denominator.'},{'criterion':'Positive permitted distinction and authorized overlap','result':'PASS within conditional finite scope','evidence':'Generated 79 configurations; actual models for eleven independently required existential queries, including both intersections and forward differences.'},{'criterion':'Claim without grant, incomplete claim, unrelated subject move','result':'PASS','evidence':'Explicit record/transition controls and unit checks; assertion fields cannot supply permission; mismatched subject/context/state fails.'},{'criterion':'Keep targets outside T and avoid vacuous/partial proof claims','result':'PASS','evidence':'Sealed two-assertion T, separately bound stress requests, substituted-theory rejection, consistency vs joint-population controls and exact interval/budget scope.'},{'criterion':'Failure/currentness handling and complete query denominator','result':'PASS','evidence':'Cancellation/deadline/step/configuration/output limits, malformed inputs, stale binding closeout and all eleven required identities retained after input preparation.'}],'worked_controls':{'searches':10,'record_cases':7,'transition_cases':4,'required_logical_queries':11,'required_pending_gates':11,'finite_product':8640,'full_product_audit':'not-complete; budget-stop retained','scope':'Hypothetical selected local-use record profile; no actual grants, actual source-owner decisions, deontic fulfillment, or temporal theorem.'},'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Accepted as bounded A08 candidate implementation for independent A09 verification, within declared limitations.','limitations':['Whole-definition natural-language fidelity and owner precedence remain pending.','All source-owner, closure and admission gates remain pending.','Opaque unary static projection is not full deontic/temporal lowering or a generic translation theorem.','Root and principal legitimacy are hypothetical external premises.','Global claim scenarios and three transition forms are an explicit finite restriction.','Default success is existential, not exhaustive; full product hit the step cap.','Budget enforcement is cooperative, not hard process isolation.','No owner-accepted whole-definition translation, whole-definition proof or full183 combined proof established.']},'full_project_completion':'not-established','independent_A09_replay':'pending','next_ready_unit':'A09.1'}
    put(UNIT/'receipt.json',receipt)
    files=[binding(path) for folder in [BASE,IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    put(UNIT/'delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda row:row['path']),'claim_ceiling':'Exact candidate bytes and prior preservation only; no source-owner acceptance or whole-project completion.'})
    print(json.dumps({'result':'sealed-candidate','test_count':42,'delivery_files':len(files),'logical_queries':11,'pending_gates':11,'source_definitions':7,'goal_status':'active','next_unit':'A09.1'}))


if __name__=='__main__':main()
