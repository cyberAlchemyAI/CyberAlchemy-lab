"""Cold code/claim check for the retained bounded T31 run receipt.

The private Source and journal were intentionally removed; this is not a cold
replay of their bytes. It checks the retained claim ceiling and code identity.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKS = ['current-signed-source-and-actor', 'native-kernel-output-contract',
          'changed-output-refused-without-effect', 'native-output-bearing-journal-replay',
          'later-consumer-processed-output-body-and-report',
          'changed-report-refused-without-new-effect']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(path=HERE / 'RUN-0001.json'):
    receipt = json.loads(Path(path).read_bytes())
    observed = receipt['observed']
    if (receipt['schema_version'] != 'lab-T31-current-output-slice/v1-candidate'
            or receipt['result'] != 'PASS' or receipt['failure'] is not None
            or receipt['checks'] != CHECKS or receipt['authority_effect'] != 'none'
            or receipt['owned_fixture_removed'] is not True
            or receipt['code_unchanged'] is not True
            or observed['journal_sequence'] != 1
            or observed['original_w08_transitions_observed'] != 0
            or observed['output_version_ref'] != 'generated-output:t31-current-source-inspection@candidate.1'
            or any(len(observed[key]) != 64 for key in ('source_manifest_sha256', 'source_cut_sha256',
                   'output_body_sha256', 'report_sha256', 'consumer_sha256',
                   'event_sha256', 'transaction_sha256', 'next_run_sha256'))
            or 'not the selected API49 workflow.transition route' not in receipt['claim_ceiling']):
        raise ValueError('retained T31 output claim differs')
    if set(receipt['code_sha256']) != {'fixture.py', 'producer.py', 'consumer.py', 'run.py'}:
        raise ValueError('retained T31 code inventory differs')
    for name, expected in receipt['code_sha256'].items():
        if sha((HERE / name).read_bytes()) != expected:
            raise ValueError('retained T31 executed code bytes changed')
    return {'result': 'PASS', 'receipt_sha256': sha(Path(path).read_bytes()),
            'output_body_sha256': observed['output_body_sha256'],
            'report_sha256': observed['report_sha256'],
            'original_w08_transitions_observed': 0,
            'claim_ceiling': 'Cold receipt/code check only; private journal and producer body are not retained for independent replay.'}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
