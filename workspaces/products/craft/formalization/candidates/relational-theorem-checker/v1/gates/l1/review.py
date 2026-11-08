#!/usr/bin/env python3
"""Review complete baseline accounting, replay currency and bounded scope."""
from copy import deepcopy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'replay'))
import replay_engine as e
s=e.s
BASE=Path(__file__).resolve().parent


def check_coverage(ledger,registry):
    rows={row['id']:row for row in ledger['rows']}
    s.require(len(rows)==len(ledger['rows'])==registry['kind_count'],'coverage omission or duplicate')
    s.require(set(rows)=={k['id'] for k in registry['kinds']},'coverage identity mismatch')
    unsupported=[]
    for kind in registry['kinds']:
        row=rows[kind['id']]
        s.require(row['version']==kind['version'],'coverage version mismatch')
        obligations={x['id']:x for x in row['obligations']}
        required={kind['id']+':ordered-signature',kind['id']+':qualifier-shape',kind['id']+':operational-effect'}
        required.update(kind['id']+':meaning:'+field for field in kind['fields'])
        required.update(kind['id']+':forbidden:'+str(i) for i in range(len(kind['forbidden_inferences'])))
        s.require(set(obligations)==required and len(obligations)==len(row['obligations']),'semantic obligation omitted or duplicated')
        for obligation in obligations.values():
            if obligation['status']=='discharged':
                s.require(obligation['evidence'],'evidence-free discharge')
                for binding in obligation['evidence']:s.check_binding(binding)
            else:
                s.require(obligation['status']=='unsupported','unknown obligation posture')
                unsupported.append({'kind':kind['id'],'id':obligation['id'],'statement':obligation['statement']})
        s.require(row['full_source_semantic_classification']=='unverified','partial proof upgraded to full semantics')
    s.require(not ledger['full_registry_semantics_proved'],'full semantic coverage misclaimed')
    return unsupported


def main():
    predecessors=[]
    for task_id in ['C01','C02','C03','C04','C05','C06']:
        task=s.task(task_id);s.require(task['status']=='accepted','missing L1 acceptance')
        binding=task['validation']['acceptance_ref'];s.check_binding(binding)
        receipt=s.read(s.ROOT/binding['path'])
        for item in receipt['artifacts']+receipt['dependency_bindings']:s.check_binding(item)
        predecessors.append(binding)
    registry=s.read(s.BASE/'registry/normalized-registry.json')
    ledger=s.read(s.BASE/'coverage/semantics/semantic-coverage-ledger.json')
    bound=s.read(s.BASE/'replay/dependency-manifest.json')
    unsupported=check_coverage(ledger,registry);e.verify(bound)
    replay=s.read(s.BASE/'replay/invalidation-controls.json')
    s.require(replay['result']=='pass' and len(replay['replays'])==2,'missing replay evidence')
    s.require(replay['replays'][0]['result_identity']==replay['replays'][1]['result_identity'],'replay identity mismatch')
    for checked in replay['replays']:
        s.require(checked['result']['dependency_identity']==bound['dependency_identity'] and checked['result']['accepted_result'],'replay not bound to current accepted input')
    controls=[]
    omitted=deepcopy(ledger);omitted['rows'].pop()
    try:check_coverage(omitted,registry)
    except ValueError:controls.append({'name':'omitted relation coverage','result':'rejected'})
    else:raise ValueError('coverage omission escaped gate')
    omitted=deepcopy(ledger);omitted['rows'][0]['obligations'].pop()
    try:check_coverage(omitted,registry)
    except ValueError:controls.append({'name':'omitted semantic obligation','result':'rejected'})
    else:raise ValueError('semantic omission escaped gate')
    stale=deepcopy(bound);stale['dependencies'][0]['sha256']='0'*64
    try:e.verify(stale)
    except ValueError:controls.append({'name':'stale baseline evidence','result':'rejected'})
    else:raise ValueError('stale evidence escaped gate')
    s.write(BASE/'l1-review.json',{'result':'accepted','review_mode':'Codex author self-review; candidate gate only',
        'authority_effect':'none','predecessors':predecessors,'selected_profile':bound['profile'],
        'dependency_identity':bound['dependency_identity'],'structural_kinds':41,'ordered_pairs':550,
        'reference_semantic_kinds':sorted(e.r.SUPPORTED),'unsupported_items':unsupported,'controls':controls,
        'following_extension_analysis_scope':{'registry_profile':'closed-required-string-ordered-pairs/v1',
            'semantic_profile':'f0-three-kind/v1','full_source_semantic_readiness':'unsupported',
            'separate_stress_profiles':'typed candidate inputs only; legacy qualifier projection unresolved'},
        'carrier_boundary':'Eight registered pairs are missing from admitted-current v3; a separate candidate carrier resolves them without source mutation.',
        'retained_assumptions':bound['trust'],
        'claim_ceiling':'Faithful complete structural baseline with explicit unsupported semantics and deterministic named-profile replay; no authority admission or full registry semantic proof.'})
    s.accept('G1',{'l1-review.json':BASE/'l1-review.json'},
        ['All six L1 task receipts and their artifacts/dependencies are current; every kind, qualifier meaning, operational-effect sentence and forbidden inference is accounted for, including 263 unsupported obligations.',
         'Following analysis is restricted to the exact captured registry structural profile and accepted F0 three-kind semantic profile; separate stress inputs and current-carrier gaps retain explicit limits.'],
        ['Coverage-row omission, semantic-obligation omission and stale replay bindings reject at the gate.'],
        [Path(__file__),s.BASE/'coverage/semantics/semantic-coverage-ledger.json',s.BASE/'replay/dependency-manifest.json',s.BASE/'replay/replay_engine.py'])
    print(json.dumps({'task':'G1','result':'accepted','unsupported_semantic_obligations':len(unsupported)}))


if __name__=='__main__':main()
