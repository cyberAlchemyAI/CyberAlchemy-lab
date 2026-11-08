"""Later behavioral consumer of the exact output body and underlying report."""

import hashlib
import json


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def consume(view, cut, source_binding, work, report_raw, body_raw, header):
    if sha(body_raw) != header['byte_sha256']:
        raise ValueError('later consumer output body bytes changed')
    body = json.loads(body_raw)
    report = json.loads(report_raw)
    if (body['payload']['output_digest'] != 'sha256:' + sha(report_raw)
            or body['node_id'] != header['identity_ref']
            or body['scope_ref'] != header['scope_ref']):
        raise ValueError('later consumer output/report lineage changed')
    current = sorted(row['version_ref'] for row in view.subjects.values()
                     if row['effective_state'] in ('admitted-current', 'local-admitted-current'))
    if (report['source_binding'] != source_binding or report['source_cut'] != cut
            or report['work_version_ref'] != work['version_ref']
            or report['scope_ref'] != header['scope_ref']
            or report['current_subject_versions'] != current
            or report['current_subject_count'] != len(current)):
        raise ValueError('later consumer selected Source comparison failed')
    return {'schema_version': 'lab-T31-current-output-consumption/v1-candidate',
            'output_version_ref': header['version_ref'],
            'output_body_sha256': sha(body_raw), 'report_sha256': sha(report_raw),
            'source_binding': source_binding, 'source_cut': cut,
            'current_subject_count': len(current),
            'discrepancy_count': 0,
            'authority_effect': 'none'}
