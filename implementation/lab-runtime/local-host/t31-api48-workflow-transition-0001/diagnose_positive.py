"""Read-only/preflight diagnosis of the refused current transition."""

import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import traceback


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'fixture.py'
RECEIPT = HERE / 'DIAGNOSTIC-0002.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if RECEIPT.exists():
        raise ValueError('versioned diagnostic already exists')
    spec = importlib.util.spec_from_file_location('_cal_t31_api48_diagnostic_fixture', FIXTURE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {}
    owned = None
    try:
        with module.current_fixture() as f:
            owned = f['workspace']
            service = f['service']
            reply = service.call(f['protocol'].compact(f['call']))
            head, _ = f['store'].replay()
            result.update(public_reply_kind=reply['kind'],
                          public_reply_code=reply['message'].get('code'),
                          public_reply_description=reply['message'].get('description'),
                          journal_sequence_after_public=head['sequence'])
            if reply['kind'] == 'error' and head['sequence'] == 0:
                workflow = importlib.import_module(type(service).__module__.rsplit('.', 1)[0] + '.workflow_transition')
                try:
                    builder = workflow.WorkflowTransition(service, output_reader=None)
                    builder.preflight(f['message'], f['source_cut'], f['message']['idempotency_key'])
                    result['direct_preflight'] = 'PASS'
                except Exception:
                    result['direct_preflight'] = traceback.format_exc()
    except Exception:
        result['constructor_or_diagnostic_error'] = traceback.format_exc()
    result.update(schema_version='lab-T31-API48-transition-diagnostic/v2-candidate',
                  fixture_sha256=digest(FIXTURE), api_source_sha256=module.SOURCE_SHA,
                  api_profile_sha256=module.PROFILE_SHA,
                  owned_fixture_removed=owned is not None and not owned.exists(),
                  actual_output_bearing_transitions=0,
                  claim_ceiling='Diagnostic only; no qualified workflow transition or owner effect.')
    with RECEIPT.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k in
                      ('public_reply_kind', 'public_reply_code', 'public_reply_description',
                       'journal_sequence_after_public', 'owned_fixture_removed')}, sort_keys=True), flush=True)
    print('DIAGNOSTIC_SHA', digest(RECEIPT), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
