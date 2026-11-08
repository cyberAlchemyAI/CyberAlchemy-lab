"""One native no-output transition, causal refusal, and cold owned replay."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import traceback


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'fixture_api49.py'
RECEIPT = HERE / 'RUN-POSITIVE-0004.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if RECEIPT.exists():
        raise ValueError('versioned no-replace T31 receipt exists')
    before_fixture = sha(FIXTURE)
    before_runner = sha(__file__)
    spec = importlib.util.spec_from_file_location('_cal_t31_api49_fixture_runner', FIXTURE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    failure = None
    returned = {}
    workspace = None
    try:
        with module.current_fixture() as fixture:
            service = fixture['service']
            workspace = fixture['workspace']
            protocol = fixture['protocol']
            call = fixture['call']
            if fixture['policy']['workflow_source_control'] != service.channel.policy_guard()['workflow_source_control']:
                raise ValueError('authenticated current workflow source changed')
            if fixture['source_cut'] != fixture['view'].legacy_signed_sources.source_cut:
                raise ValueError('current Source cut differs')
            checks.append('current-signed-Source-authenticated-owned-Service')
            print('AUTHENTICATED', flush=True)
            before = module.owned_snapshot(workspace)
            wrong = copy.deepcopy(call)
            wrong['call_id'] = 'call:t31-workflow-wrong-actor'
            wrong['message']['actor']['principal_ref'] = 'principal:foreign'
            refusal = service.call(protocol.compact(wrong))
            if refusal['kind'] != 'error' or refusal['message']['code'] != 'unauthorized' or module.owned_snapshot(workspace) != before:
                raise ValueError('same-channel wrong Actor was not causally refused without effect')
            checks.append('same-channel-wrong-Actor-unauthorized-no-effect')
            print('WRONG_ACTOR_REFUSED', flush=True)
            reply = service.call(protocol.compact(call))
            if not fixture['schemas'].valid('api-reply', reply) or reply['kind'] != 'result':
                raise ValueError('native no-output workflow transition refused: ' +
                                 repr({'kind': reply.get('kind'), 'message': reply.get('message')}))
            result = reply['message']
            print('POSITIVE_REPLY', reply['kind'], flush=True)
            if result['posture'] != 'applied' or result['from_state'] != 'prepared' or result['to_state'] != 'inspected' or result['output_artifact_refs'] != []:
                raise ValueError('native no-output transition result differs')
            head, current_raw = fixture['journal'].Journal(workspace / 'workflows/source-inspection',
                                                           fixture['store'].config_sha256).replay()
            if head['sequence'] != 1 or json.loads(current_raw)['state'] != 'inspected':
                raise ValueError('native owned workflow journal did not replay observed transition')
            checks.append('native-transition-owned-journal-replay')
            print('JOURNAL_REPLAY_PASS', head['sequence'], flush=True)
            returned = {'source_subjects': len(fixture['view'].subjects),
                        'source_cut_sha256': hashlib.sha256(protocol.compact(fixture['source_cut'])).hexdigest(),
                        'workspace_journal_sequence': head['sequence'],
                        'result_sha256': hashlib.sha256(protocol.compact(result)).hexdigest(),
                        'negative_code': refusal['message']['code'],
                        'output_artifact_refs': result['output_artifact_refs']}
    except Exception:
        failure = traceback.format_exc()
    complete = failure is None and len(checks) == 3 and workspace is not None and not workspace.exists()
    receipt = {'schema_version': 'lab-T31-API49-native-positive-transition/v4-candidate',
               'result': 'PASS' if complete else 'FAIL', 'checks': checks,
               'failure': failure, 'observed': returned,
               'owned_fixture_removed': workspace is not None and not workspace.exists(),
               'fixture_sha256_before': before_fixture, 'fixture_sha256_after': sha(FIXTURE),
               'runner_sha256_before': before_runner, 'runner_sha256_after': sha(__file__),
               'api_source_sha256': module.SOURCE_SHA, 'api_profile_sha256': module.PROFILE_SHA,
               'actual_output_bearing_transitions': 0, 'authority_effect': 'none',
               'claim_ceiling': 'One current signed-source native no-output WorkflowRun transition, same-channel wrong-Actor refusal, and owned journal replay only. Exact retry remains unqualified. No producer output, later consumer, Work satisfaction, canonical admission, owner outcome, portable installation or full T31 completion.'}
    with RECEIPT.open('x') as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': receipt['result'], 'checks': checks,
                      'failure': None if failure is None else failure.splitlines()[-1],
                      'receipt_sha256': sha(RECEIPT)}, sort_keys=True), flush=True)
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
