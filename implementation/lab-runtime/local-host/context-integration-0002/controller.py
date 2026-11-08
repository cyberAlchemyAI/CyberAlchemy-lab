"""Read-only Context integration preflight. There is no launch implementation."""
import argparse
import datetime as dt
import json
from pathlib import Path

import admission
import closure
import emit_adapter


def preflight():
    now = dt.datetime.now(dt.timezone.utc)
    selected = admission.verify(now)
    mapped = closure.plan(now)
    adapted, proof = emit_adapter.adapt()
    admission.require(adapted == (Path(__file__).resolve().parent / 'adapted-build-inert.py').read_bytes(),
                      'inert adapted emitted code differs')
    admission.require(mapped['mapper_package'] == 'UNSELECTED' and
                      mapped['context_source_manifest'] == 'REFUSED' and
                      mapped['context_launch'] == 'REFUSED', 'Context effect gate differs')
    return {
        'schema_version': 'lab-context-inert-integration-preflight/v1',
        'status': 'HOLD_MAPPER', 'observed_at': now.isoformat(),
        'source_reader_metadata': selected['status'],
        'source_package_sha256': selected['source_package_sha256'],
        'reader_receipt_sha256': selected['reader_receipt_sha256'],
        'inert_adapted_build_sha256': proof['adapted_sha256'],
        'historical_context_rows': mapped['historical_context_rows'],
        'development_authorization': mapped['development_authorization'],
        'mapper_package': 'UNSELECTED', 'context_source_manifest': 'REFUSED',
        'context_launch': 'REFUSED', 'authority_effect': 'none',
        'actual_owner_outcome': None, 'archive_body_read': False, 'effect': 'NOT_RUN',
    }


def main():
    parser = argparse.ArgumentParser()
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument('--preflight', action='store_true')
    choices.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    try:
        if args.launch:
            admission.launch_context()
        else:
            print(json.dumps(preflight(), sort_keys=True, separators=(',', ':')))
            return 2  # a valid read-only inspection is still a launch HOLD
    except admission.Refused as error:
        print(json.dumps({'status': 'REFUSED', 'reason': str(error), 'effect': 'NOT_RUN'},
                         sort_keys=True, separators=(',', ':')))
        return 2
    raise RuntimeError('unreachable inert controller branch')


if __name__ == '__main__':
    raise SystemExit(main())
