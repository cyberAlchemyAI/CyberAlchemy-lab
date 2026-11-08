"""Cold custody and later computation over exact retained original-producer outputs.

No producer is rerun. The coordination grant/evidence are synthetic fixtures;
original output bodies and original producer observations are never rewritten.
"""
import copy
from collections import Counter
import json
import math
from pathlib import Path
import tempfile

from output_store import J, O, ROOT, OutputJournal, sha
from template_fixture import F, plan_for

RUN = ROOT / 'implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001'
RESULT_SHA = 'c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445'
EXTRA_INPUTS = {
    'engineering/assessment.json': 'ee6a7234eb63ed2cddf76241b12b967b05ff0e3f5cb49014d946d3238d18a780',
    'engineering/evidence/default-regression-complete.json': 'b0276d8a7b41268199f3fe1529e1bea558b8afcbdd10be8344962da69af1e782',
    'engineering/evidence/expired-authority-denied.json': 'fce71ef10c5f7f9b2c8fc79979bb7c4cbf884f3f3187f6ecfd306f2746d44380',
    'engineering/evidence/revoked-authority-denied.json': '42277e9bbfadbb887da1a3e874cd73930e4c27068057a61e075e6f1f51e9ed4a',
    'engineering/evidence/selected-interface-permitted.json': '363139c5b29f0e7bad38b5017024d882726fcb671bd0ce444569baf86a83df7d',
    'engineering/evidence/source-bytes-exact.json': '5382fd33a255a5186b1f442b61ff018f9ed9ec7c7cc99547c3a4a7c2114ebc3f',
    'engineering/evidence/unselected-interface-denied.json': 'f4e46f42a962f1f05995c34c3b4267525526e2eaac8211fda280e3513e7e9b07',
    'engineering/evidence/wrong-action-denied.json': '4d7336c82ded604833e2f02fabff1763d8bb7513c81a701f758e5bb2b83417dc',
    'research/assessment.json': '2fbbc54cb40a916355c4b0871afd7d449cb2bda81a5826c23a911e2df1d93247',
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def witness(original_run, scope):
    """A new coordination fixture, explicitly distinct from historical source authority."""
    message, facts = F.F.build()
    # The retained producer emits a workflow-design-run, not a native Run.
    # Build a new closed coordination fixture from shared fields; never relabel
    # or overwrite the original producer record as native execution evidence.
    run = json.loads(facts['run_raw'])
    for key in ('actor', 'source_cut', 'intent', 'intent_resolution', 'work', 'coordination_context'):
        run[key] = copy.deepcopy(original_run[key])
    run.update(run_ref=original_run['run_ref'] + ':durable-byte-replay', event_bindings=[], outcome_assessment=None)
    cut, actor = run['source_cut'], run['actor']
    message.update(actor=copy.deepcopy(actor), source_cut=copy.deepcopy(cut))
    facts.update(run_raw=J.K.encoded(run), authenticated_actor=copy.deepcopy(actor), current_cut=copy.deepcopy(cut))
    facts['host_grant'].update(principal_ref=actor['principal_ref'], source_cut=copy.deepcopy(cut), scope_ref=scope)
    for key in ('authority_raw', 'satisfaction_raw'):
        body = json.loads(facts[key]);body['source_cut'] = copy.deepcopy(cut)
        facts[key] = J.K.encoded(body)
    return message, facts


def consume_observed(kind, consumed, producer_root):
    for path, expected in EXTRA_INPUTS.items():
        if path.startswith(kind + '/'):
            need(sha((producer_root / path).read_bytes()) == expected, 'selected retained input bytes differ')
    bodies = {h['carrier_ref']: json.loads(raw) for h, raw in consumed}
    if kind == 'engineering':
        generated = bodies['cal.artifact-type.generated-output/v2']
        evidence = bodies['cal.artifact-type.evidence-set/v1']
        corrected = (producer_root / 'engineering/workflow/tool/registered_evaluator.py').read_bytes()
        need(generated['payload']['output_digest'] == 'sha256:' + sha(corrected), 'consumed source body differs')
        compile(corrected, 'verified-retained-correction', 'exec')  # Compile only; never execute retained code.
        checks = json.loads((producer_root / 'engineering/assessment.json').read_bytes())['checks']
        need(len(checks) == len(evidence['payload']['item_refs']) == 7, 'observed evidence count differs')
        for name, check in checks.items():
            need('protocol:W03-' + name in evidence['payload']['item_refs']
                 and sha((producer_root / 'engineering/evidence' / check['evidence_path']).read_bytes()) == check['evidence_sha256'],
                 'consumed observed check bytes differ')
        need(checks['default-regression-complete']['result'] == 'FLAG', 'retained engineering limitation changed')
        return {'consumer': 'compile-correction-and-check-seven-evidence-bodies',
                'source_sha256': sha(corrected), 'observed_default_regression': 'FLAG',
                'engineering_assessment': 'unsupported', 'retained_code_executed': False}
    experiment = bodies['cal.artifact-type.experiment-run/v1']
    measurement = bodies['cal.artifact-type.measurement-result/v1']
    headers = {h['carrier_ref']: h for h, _ in consumed}
    need(experiment['run_state'] == 'completed'
         and measurement['subject_ref'] == headers['cal.artifact-type.experiment-run/v1']['version_ref']
         and headers['cal.artifact-type.measurement-result/v1']['version_ref'] in experiment['measurement_result_refs'],
         'observed experiment/measurement lineage differs')
    assessment = json.loads((producer_root / 'research/assessment.json').read_bytes())
    need(assessment['disposition'] == 'inconclusive', 'retained research limitation changed')
    labels = assessment['labels']; need(len(labels) == 3, 'bounded label sample differs')
    entropy = -sum((count / len(labels)) * math.log(count / len(labels)) for count in Counter(labels).values())
    need(math.isclose(entropy, measurement['value'], rel_tol=1e-12, abs_tol=1e-12)
         and math.isclose(entropy, assessment['residue_entropy_nats'], rel_tol=1e-12, abs_tol=1e-12),
         'consumed measurement does not reproduce observed label entropy')
    return {'consumer': 'recompute-finite-observed-label-entropy', 'sample_size': len(labels),
            'entropy_nats': entropy, 'research_assessment': assessment['disposition']}


def run(producer_root=RUN):
    raw = (producer_root / 'RESULT.json').read_bytes()
    need(sha(raw) == RESULT_SHA, 'selected original producer receipt differs')
    for path, expected in EXTRA_INPUTS.items():
        need(sha((producer_root / path).read_bytes()) == expected, 'selected retained input bytes differ')
    result = json.loads(raw); reports = []
    with tempfile.TemporaryDirectory(prefix='t31-retained-output-custody-') as temp:
        for row in result['new_output_transitions']:
            kind = row['transition_ref'].split(':')[1]
            run_raw = (producer_root / kind / 'workflow-run.json').read_bytes()
            need(sha(run_raw) == row['workflow_run_sha256'], 'retained original WorkflowRun differs')
            for consumer in row['later_consumers']:
                need(sha((producer_root / consumer['path']).read_bytes()) == consumer['sha256'],
                     'retained original consumer differs')
            outputs = []
            for header, path in zip(row['output_artifact_refs'], row['output_original_paths'], strict=True):
                body = (producer_root / path).read_bytes()
                need(sha(body) == header['byte_sha256'], 'retained original output differs')
                outputs.append((header, body))
            definition_path = ROOT / ('docs/proposals/0007-lab-integrated-schema-package/workflows/' + kind + '.json')
            definition = json.loads(definition_path.read_bytes())
            transition = next(t for t in definition['transitions'] if t['transition_ref'] == row['transition_ref'])
            scope = outputs[0][0]['scope_ref']
            plan, before, originals = plan_for(definition_path, transition,
                build_witness=lambda: witness(json.loads(run_raw), scope), selected_outputs=outputs)
            # Exact retained source-run/producer receipt bytes are linked as observed producer evidence.
            plan['producer_receipt_bindings'] = [F.binding('retained-producer:RESULT', raw),
                                                  F.binding('retained-producer:WorkflowRun', run_raw)]
            def fixture_data_guard():
                need(sha((producer_root / 'RESULT.json').read_bytes()) == RESULT_SHA,
                     'retained producer selection changed')
            store = OutputJournal.initialize(Path(temp) / kind, before, scope, plan['next_run']['actor']['principal_ref'])
            tx = store.apply(plan, originals=originals, request_binding=F.binding('fixture:retained-output', J.K.encoded(row)),
                             host_guard=fixture_data_guard)
            cold = OutputJournal(store.root, store.journal.config_sha256)
            consumed = cold.consume(1)
            need({h['version_ref']: body for h, body in consumed} == originals, 'cold output bytes differ')
            observation = consume_observed(kind, consumed, producer_root)
            reports.append({'transition_ref': row['transition_ref'], 'original_output_shas': [sha(body) for _, body in consumed],
                            'sequence': tx['sequence'], 'later_consumer': observation})
    return {'result': 'PASS-retained-original-output-custody-and-later-computation', 'transitions': reports,
            'original_producer_rerun': False, 'original_output_bytes_unchanged': True,
            'retained_producer_run_schema': 'lab-workflow-design-run/v1-candidate',
            'new_coordination_run_uses_synthetic_witnesses': True,
            'synthetic_coordination_grant_and_obligations': True, 'current_native_source_qualified': False,
            'T31_complete': False, 'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
