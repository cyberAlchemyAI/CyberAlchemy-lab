"""Seal actual completed unit validation, preserving all upstream bytes."""
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];UNIT=Path(__file__).resolve().parent
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
import resolver as r


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    log=(UNIT/'test-output.txt').read_text();match=re.search(r'Ran (\d+) tests in ([\d.]+)s\n\nOK\s*$',log)
    if match is None:raise ValueError('Completed passing test suite required before sealing')
    cases=json.loads((UNIT/'worked-verifications.json').read_text());context=json.loads((UNIT/'context.json').read_text())
    source=r.verify(json.loads((BASE/'current-snapshot.json').read_text()),ROOT)
    inputs=[{key:row[key] for key in ['path','sha256']} for row in context['sources']]
    for row in inputs:
        if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Upstream/context input changed')
    outputs=[binding(path) for path in [IMPL/'verifier.py',IMPL/'tests/test_E03.py']]+[binding(path) for path in sorted(UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    receipt={'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'E03.1','authority_effect':'none','goal_status':'active','inputs':inputs,'outputs':outputs,'task_result':'PASS for independent required-set regeneration, explicit nominal typing and supplied finite-model checking with unresolved proof/review gates retained','test_result':'PASS','test_count':int(match[1]),'test_seconds':float(match[2]),'criterion_results':[{'criterion':'Regenerate required set independently; reject omitted or substituted logical/gate rows','result':'PASS','evidence':'Exact independent A06 generation and forged closed-package denominator controls.'},{'criterion':'Reject changed witness, substituted dependency, nominal source identity and provider build','result':'PASS','evidence':'Actual separate denotation evaluation plus rehashed-model, artifact, ownership, active provider and policy controls.'},{'criterion':'Keep historical captures available while rechecking selected live applicability','result':'PASS','evidence':'Historical replay survives fixture source change; separately selected live root rejects it. Actual Lab capture reverified.'},{'criterion':'Distinguish checker trust from mechanized proof and preserve pending evidence','result':'PASS','evidence':'All outputs remain false semantic-ready and false mechanized-proof; bounded reports and all gates retain pending rows.'}], 'worked_controls':{'retained_cases':len(cases['records']),'fresh_root_replays':len(cases['replays']),'checked_joint_population_witnesses':1,'rehashed_false_witnesses_rejected':1,'scope':'isolated synthetic fixtures; no canonical fixture installation'},'actual_source_validation':source,'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Accepted within the documented independent finite-witness checking boundary.','limitations':['Python checker/parser/type checker/resolver remain trusted; no generic correctness theorem.','Bounded exhaustion, solver and kernel evidence remain unverified.','Semantic dependency closure and owner source-fidelity review remain pending.','All worked evidence is synthetic, with zero current Lab whole-definition proofs.']},'full_project_completion':'not-established','next_ready_work':'A07 source-backed orthogonality pilot and its independent replay; E04 awaits A09 as well as E03.'}
    put(UNIT/'receipt.json',receipt)
    put(UNIT/'episode-status.json',{'authority_effect':'none','goal_status':'active','current_definitions':183,'admitted_source_versions':189,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'completed_candidate_unit':'E03.1','new_tests':int(match[1]),'new_retained_cases':3,'new_independent_replays':3,'definitions_first_priority':'Definition forms and roles; nominal sorts/signatures; selected logic and denotation; composition/orthogonality; required logical and review obligations.','remaining':'Source-backed pilot and replay, full-family translations, semantic dependency closure, solver/kernel profiles, independent extension semantics, change handling, global theory checks, owner review and final complete formalization episode review.'})
    rows=[binding(path) for directory in [BASE,IMPL] for path in sorted(directory.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    put(UNIT/'delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(rows,key=lambda row:row['path']),'claim_ceiling':'Exact candidate file preservation and delivery identity. No semantic or project completion claim.'})
    print(json.dumps({'result':'sealed-candidate','tests':int(match[1]),'delivery_files':len(rows),'source_files':source['files'],'goal_status':'active'}))


if __name__=='__main__':main()
