"""One real authenticated prospective Work validation; no package/admission claim."""
import argparse
import copy
from contextlib import ExitStack
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v52'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_closed_work_model_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    name = '_cal_closed_work_model_actual'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    P = importlib.import_module(name + '.protocol')
    F = importlib.import_module(name + '.example_fixture')
    MF = importlib.import_module(name + '.metadata_fixture')
    A = importlib.import_module(name + '.auth')
    S = importlib.import_module(name + '.service')
    events = []
    with ExitStack() as stack:
        view = stack.enter_context(P.source.replay_source('custody-participation'))
        schemas = P.Schemas(args.profile_sha256)
        R = P.source.custody_delivery().records
        prior = view.subjects[R.WORK + '@' + R.VERSION]
        record = copy.deepcopy(prior['record'])
        record['node_id'] = 'work:R03-exact-candidate-example'
        record['name'] = 'Prepare a closed package import candidate'
        record['payload'].update(project_ref=view.data['config']['scope_ref'],
            goal_refs=[R.GOAL + '@' + R.VERSION], input_refs=[R.INTENT + '@' + R.VERSION],
            output_refs=[], completion_state='candidate-prepared',
            work_statement='Validate an exact candidate against the existing current Goal, Intent and Project before preparing portable original content. This does not claim completed work or a produced output.')
        materials, metadata, target = F.materials_for(view, record_override=record)
        root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-package-closed-work-')))
        root.chmod(0o700)
        key, policy, pin = MF.provision(root, materials, metadata, scoped=False)
        channel = A.ReaderChannel(policy, pin, schemas)
        context = channel.authenticate(F.proof(key, channel.challenge))
        assert context['agent_instance_ref'] is context['session_ref'] is context['assignment_ref'] is None
        service = S.Service(view, channel, schemas)
        stack.callback(service.close)
        call = F.candidate_call(service, target, operation='change.validate', key='fixture:package-closed-work-validate')
        original = P.compact(call)
        reply = service.call(original)
        events.append({'original_call': call, 'request_byte_sha256': P.source.sha(original), 'reply': reply})
        assert reply['kind'] == 'result', reply
        report = reply['message']
        assert report['schema_version'] == 'lab-validation-report/v1-candidate'
        # Record actual result even if semantic closure did not pass. A complete
        # shape or successful envelope must never substitute for PASS semantics.
        complete_model = report['result'] == 'pass'
        before = view.handle.common.digest(view.data['projection'])
        view.custody_signed_sources.guard()
        assert before == view.handle.common.digest(view.data['projection'])
        target_body = copy.deepcopy(record)
        target_header = copy.deepcopy(target['artifact'])
        bound_report = copy.deepcopy(report)
    guard.verify(args.source_sha256)
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': P.source.sha(path.read_bytes())}
    wire = RUN / 'package-closed-work-model-wire-0001.json'
    with wire.open('x') as stream:
        json.dump(events, stream, indent=2, sort_keys=True)
        stream.write('\n')
    output = RUN / 'package-closed-work-model-receipt-0001.json'
    result = {'schema_version': 'lab-package-closed-work-model-check/v1-candidate',
        'result': 'PASS' if complete_model else 'FAIL', 'source_sha256': args.source_sha256,
        'profile_sha256': args.profile_sha256, 'actual_public_calls': 1, 'actual_authenticated_host_used': True,
        'actual_signed_source_replay_completed': True, 'source_guarded_exit_completed': True,
        'owned_fixture_cleanup_completed': True, 'actual_validation_result': report['result'],
        'prospective_Work_target_model_passed': complete_model, 'validation_report': bound_report,
        'candidate_Work_header': target_header, 'candidate_Work_body': target_body,
        'canonical_admissions_applied': 0, 'private_Session_memory_restored': False,
        'public_package_handlers_added': 0, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'One original current API52 change.validate call for a separately prepared Work with exact existing Project/Goal/Intent inputs and no represented output yet. No output or completed Work is invented. This is a candidate fixture, not package export/import, source admission, human pilot, canonical admission or full plan.',
        'files': [bind(wire), bind(Path(__file__).resolve()), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json')]}
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': result['result'], 'actual_validation_result': report['result'],
        'actual_public_calls': 1, 'report_binding': bind(output), 'task_complete': False}), flush=True)
    return 0 if complete_model else 1


if __name__ == '__main__':
    raise SystemExit(main())
