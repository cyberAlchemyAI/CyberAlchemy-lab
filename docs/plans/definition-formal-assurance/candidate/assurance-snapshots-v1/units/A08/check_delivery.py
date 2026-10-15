"""Read-only candidate byte preservation and same-implementation smoke replay."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parent.parent;IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
loader=importlib.util.spec_from_file_location('governance_v2',IMPL/'pilot-v2.py');v=importlib.util.module_from_spec(loader);loader.loader.exec_module(v)


def bound(row):
    if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale candidate binding: '+row['path'])


def read(row):bound(row);return json.loads((ROOT/row['path']).read_bytes())


def main():
    counts={}
    for path in [BASE/'units/A07/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_bytes())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate delivery path')
        for row in rows:bound(row)
        counts[path.relative_to(ROOT).as_posix()]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_bytes())
    for row in receipt['inputs']+receipt['outputs']:bound(row)
    if receipt['unit_id']!='A08.1' or receipt['authority_effect']!='none' or receipt['goal_status']!='active' or receipt['test_count']!=42:raise ValueError('Unit/authority/completion mismatch')
    prepared=v.prepare();worked=json.loads((UNIT/'worked-controls.json').read_bytes());searches={}
    for row in worked['searches']:
        value=read(row['result_ref']);searches[row['case_id']]=value
        if value['authority_effect']!='none' or value['semantic_ready'] is not False or value['unbounded_conclusion'] is not None:raise ValueError('False semantic authority')
        if value['required_denominator_status']=='resolved':
            actual={entry['obligation_id'] for entry in value['query_results']};expected={entry['obligation_id'] for entry in prepared['required']['logical_manifest']['obligations']}
            if actual!=expected:raise ValueError('Required query identity mismatch')
            if value['input_bindings']['required_set_sha256']!=prepared['required']['required_set_sha256']:raise ValueError('Required set mismatch')
        if value['status']!=row['status'] or value['counts']!=row['counts']:raise ValueError('Control index mismatch')
    positive=searches['positive'];witnesses=0
    for row in positive['query_results']:
        witness=row['witness']
        if witness is None or row['strength']!='model-witness' or witness['model_sha256']!=v.ir.digest(witness['model']) or not v.r.same_json(v.point(witness['rank']),witness['model']):raise ValueError('Constructive witness binding mismatch')
        actual=v.assess(witness['model'],prepared,v.Control(v.f.load_limits()))
        if not actual['theory'] or not actual['queries'].get(row['obligation_id']) or not v.r.same_json(actual['projection_model'],witness['projection_model']) or witness['projection_model_sha256']!=v.ir.digest(witness['projection_model']):raise ValueError('Same-implementation smoke replay mismatch')
        witnesses+=1
    if positive['counts']['visited']!=79 or positive['exhaustion_complete']:raise ValueError('Positive range claim mismatch')
    for key in ['collapse','contradiction','missing-population']:
        if searches[key]['status']!='bounded-checked' or not searches[key]['exhaustion_complete']:raise ValueError('Bounded negative control mismatch')
    if searches['contradiction']['counts']['theory_models'] or searches['missing-population']['counts']['joint_models'] or not searches['missing-population']['counts']['theory_models']:raise ValueError('Vacuity/consistency distinction mismatch')
    difference=next(row for row in searches['collapse']['query_results'] if row['obligation_id']=='relation:TRACE-Position:left-difference')
    if difference['status']!='bounded-no-witness' or difference['witness'] is not None:raise ValueError('Collapse control mismatch')
    for key,status in [('full-range-budget-stop','resource-limit'),('one-configuration-limit','resource-limit'),('step-limit','resource-limit'),('output-limit','resource-limit'),('deadline','timeout'),('cancellation','cancelled')]:
        value=searches[key]
        if value['status']!=status or value['exhaustion_complete']:raise ValueError('Partial control promoted to exhaustion')
    controls=read(worked['record_transition_ref'])
    for row in controls['record_cases']:
        if not v.r.same_json(row['actual'],v.record_values(row['state'],v.Control(v.f.load_limits()))):raise ValueError('Record smoke replay mismatch')
    for row in controls['transition_cases']:
        if row['transition_holds']!=v.transition_holds(row['model']['transition'],row['model']['records'],v.Control(v.f.load_limits())):raise ValueError('Transition smoke replay mismatch')
    v.verify_bindings(prepared)
    print(json.dumps({'result':'PASS','authority_effect':'none','delivery_manifests':counts,'test_count':receipt['test_count'],'logical_witnesses':witnesses,'logical_denominator':11,'pending_gates':11,'actual_search_controls':len(searches),'record_controls':len(controls['record_cases']),'transition_controls':len(controls['transition_cases']),'live_source_binding':v.p.bind_sources(prepared['spec'],ROOT),'verification_scope':'Exact bytes, prior-file preservation and same-implementation smoke replay; independent A09 denotation/full-domain audit remains pending.','source_fidelity':'pending','semantic_dependency_closure':'unresolved','owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'goal_status':'active','next_unit':'A09.1'},indent=2,sort_keys=True))


if __name__=='__main__':main()
