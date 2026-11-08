#!/usr/bin/env python3
"""Recapture the selected D74 registry and assess alignment with accepted F0."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'execution'))
import support as s


BASE = Path(__file__).resolve().parent
REGISTRY = s.ROOT / 'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'


def capture():
    registry = s.read(REGISTRY)
    admission = REGISTRY.parents[1]
    bundle = s.read(admission / 'bundle.json')
    application = s.read(admission / 'receipts/application.json')
    s.require(application['result'] == 'PASS', 'unapplied registry overlay')
    s.require(s.digest(REGISTRY) == application['outputs']['relation_kind_registry']['sha256'], 'stale registry output')
    declared = {entry['path']:entry['sha256'] for entry in bundle['files']}
    s.require(declared['registries/relation-kind-registry.json'] == s.digest(REGISTRY), 'registry not in exact admission bundle')
    for authorization in [bundle['authorization'], application['authorization']]:
        s.check_binding(authorization)
    d70 = s.ROOT / 'authority/admissions/definition-complete-lab-model/v1/bundle.json'
    previous = s.read(d70)
    s.check_binding(previous['authorization'])
    s.require(previous['decision_id'] == 'CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION', 'wrong predecessor overlay')
    decisions = set(bundle['decision_refs']) | {previous['decision_id']}
    records, sources, pair_count = [], [s.binding(REGISTRY), s.binding(admission/'bundle.json'),
        s.binding(admission/'receipts/application.json'), s.binding(d70), bundle['authorization'], previous['authorization']], 0
    for entry in registry['entries']:
        path = s.ROOT / entry['instance_path']
        s.require(s.digest(path) == entry['instance_sha256'], 'relation source drift')
        source = s.read(path)
        payload = source['payload']
        s.require(entry['admission_decision_ref'] in decisions, 'unresolved admission decision')
        s.require(entry['lifecycle_state'] == 'admitted-current', 'unsupported effective relation state')
        count = len(payload['allowed_endpoint_pairs'])
        s.require(count == entry['exact_endpoint_pair_count'], 'pair count mismatch')
        s.require(entry['required_qualifier_axes'] == payload['qualifier_contract']['required_axes'], 'qualifier axes drift')
        records.append({'entry':entry, 'source_posture':{'lifecycle_state':source['lifecycle_state'],
                       'authority_effect':source['authority_effect'], 'claim_ceiling':source['claim_ceiling']},
                        'payload':payload})
        sources.append(s.binding(path));pair_count += count
    # D75 changes the project head, but explicitly consumes the frozen D74 profile.
    current_path = s.ROOT/'authority/project-state-transitions/current.json'
    head = s.read(current_path)
    s.check_binding(head['admission_bundle']);s.check_binding(head['current_project_state'])
    current_bundle = s.read(s.ROOT/head['admission_bundle']['path'])
    s.require('frozen D74 source profile' in current_bundle['claim_ceiling'], 'current head profile must be reviewed')
    sources += [s.binding(current_path), head['admission_bundle'], head['current_project_state']]
    return {'schema':'relational.execution-baseline/v1','scope':'selected immutable D74 relation registry',
            'records':records,'counts':{'kinds':len(records),'ordered_pairs':pair_count},
            'source_bindings':sources,'current_project_head':head,'head_alignment':'D75 retains frozen D74 source profile',
            'implementation_owner':'Codex','reviewer':'Codex author self-review; no independent human admission',
            'authority_effect':'none'}


def main():
    s.context('B00',[(s.PLAN,'tasks[id=B00]'),(s.FORMAL/'proofs/l0/task-acceptance.json','accepted proof scope and dependencies'),
        (s.FORMAL/'core/source-slice.json','three exact source payloads'),(REGISTRY,'entries and effective lifecycle'),
        (REGISTRY.parents[1]/'receipts/application.json','outputs.relation_kind_registry'),
        (s.ROOT/'authority/admissions/definition-complete-lab-model/v1/bundle.json','decision_id and authorization'),
        (s.ROOT/'authority/project-state-transitions/current.json','current project lookup')],
        [{'choice':'retain D74 as explicit selected registry; record D75 head without rewriting D74',
          'classification':'non-blocking','basis':'D75 admits implementation using the frozen D74 profile'}])
    baseline = capture()
    formal = s.read(s.FORMAL/'core/source-slice.json')
    by_path = {r['entry']['instance_path']:r for r in baseline['records']}
    alignment = []
    for record in formal['records']:
        current = by_path[record['path']]
        s.require(record['sha256'] == current['entry']['instance_sha256'] and record['payload'] == current['payload'], 'formal model invalidated by source drift')
        alignment.append({'path':record['path'],'sha256':record['sha256'],'result':'unchanged'})
    parent = s.read(s.FORMAL/'proofs/l0/statement-and-axiom-audit.json')
    for item in parent['source_bindings'] + parent['relation_sources']:
        s.check_binding(item)
    s.require(baseline['counts'] == {'kinds':41,'ordered_pairs':550}, 'selected coverage changed')
    s.write(BASE/'baseline-manifest.json',baseline)
    s.write(BASE/'formal-model-alignment.json', {'result':'pass','records':alignment,
        'formal_source_bindings_verified':len(parent['source_bindings']+parent['relation_sources']),
        'supported_formal_kinds':3,'supported_formal_pairs':28,'registry_kinds':41,'registry_pairs':550,
        'parser_runtime_assumptions_retained':True,'earlier_proof_current_for_selected_scope':True})
    (BASE/'decision-record.md').write_text('# Execution baseline decision\n\nThe selected D74 registry remains 41 kinds and 550 exact ordered pairs. Its three F0 source records and accepted proof dependencies are unchanged. Source candidate posture remains separate from effective admitted-current state. The newer D75 project head explicitly consumes the frozen D74 source profile and is captured separately.\n\nCodex performs implementation and author self-review. This accepts only the candidate baseline alignment; it supplies no independent human review, runtime activation or authority admission. Parser, hashing and external evidence interpretation remain explicit trust boundaries.\n')
    s.accept('B00', {name:BASE/name for name in ['baseline-manifest.json','formal-model-alignment.json','decision-record.md']},
        ['All 41 exact sources, D70/D74 overlays and current D75 lookup are hash checked; both lifecycle postures and reviewer roles are recorded.',
         'Three reviewed relation payloads and all F0 source bindings remain byte-identical; D75 retains the selected D74 profile.'],
        ['Hash and overlay checks execute before any baseline receipt is accepted.',
         'Alignment reports only the unchanged three-kind formal scope and retains earlier trust boundaries; no independence is inferred from axis labels.'],
        [Path(__file__),s.FORMAL/'core/source-slice.json'])
    print(json.dumps({'task':'B00','result':'accepted','counts':baseline['counts']}))


if __name__ == '__main__':main()
