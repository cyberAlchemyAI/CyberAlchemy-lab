"""Retained engineering/research observation used by the installed workflow.

This is the consumer portion of the original observed replay. It has no test
fixture or synthetic plan dependency and never executes retained source code.
"""
from collections import Counter
import hashlib
import json
import math

sha = lambda raw: hashlib.sha256(raw).hexdigest()
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
