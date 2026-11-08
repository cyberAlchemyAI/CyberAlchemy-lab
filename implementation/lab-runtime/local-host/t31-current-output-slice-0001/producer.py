"""Produce a bounded, real report from the selected signed Source view."""

import hashlib
import json


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def produce(view, cut, work, source_binding, scope_ref):
    current = sorted(row['version_ref'] for row in view.subjects.values()
                     if row['effective_state'] in ('admitted-current', 'local-admitted-current'))
    report = {
        'schema_version': 'lab-T31-current-source-inspection/v1-candidate',
        'source_binding': source_binding,
        'source_cut': cut,
        'scope_ref': scope_ref,
        'work_version_ref': work['version_ref'],
        'current_subject_versions': current,
        'current_subject_count': len(current),
        'authority_effect': 'none',
    }
    report_raw = compact(report)
    identity = 'generated-output:t31-current-source-inspection'
    output = {
        'schema_version': 'cyberalchemy-lab-generated-output/v2',
        'node_id': identity,
        'kind': 'generated-output',
        'name': 'Current signed Source inspection report',
        'claim_ceiling': 'Local signed Source inspection output only; no original W08 transition, Work satisfaction or authority effect.',
        'scope_ref': scope_ref,
        'owner_ref': 'principal:repository-owner@candidate.1',
        'lifecycle_state': 'candidate',
        'challenge_route': 'protocol:isolated-workflow-review',
        'evidence_refs': ['source:' + source_binding['sha256']],
        'relation_refs': [{'relation_kind_ref': 'relation.derives-from',
                           'direction': 'target', 'counterpart_kind': 'source',
                           'counterpart_ref': source_binding['ref']}],
        'successor_refs': [],
        'payload': {
            'generator_ref': 'implementation/lab-runtime/local-host/t31-current-output-slice-0001/producer.py',
            'input_refs': [work['version_ref']],
            'output_digest': 'sha256:' + sha(report_raw),
            'reproducibility_receipt_ref': 'source:' + source_binding['sha256'],
        },
        'authority_effect': 'none',
    }
    body_raw = compact(output)
    header = {'scope_ref': scope_ref, 'identity_ref': identity,
              'version_ref': identity + '@candidate.1',
              'carrier_ref': 'cal.artifact-type.generated-output/v2',
              'byte_sha256': sha(body_raw)}
    return report_raw, body_raw, header
