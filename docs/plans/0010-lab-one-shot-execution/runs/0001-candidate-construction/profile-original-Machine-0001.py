"""Measure original real fixture costs; never extend a grant or replace a guard."""
import argparse
import cProfile
import hashlib
import importlib.util
import json
from pathlib import Path
import pstats
import sys
import time

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v35'
SOURCE = 'c4e6e226082890da6569acb1175878fa5b3f70e06b1e42cd0a11331ec3c21e11'
PROFILE = 'e4bc3484d8c675ee75881e43d9bcec7fa750da02bd454ad0131dd68c0642bdc7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnostic(error):
    frames = []
    tb = error.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        path = Path(code.co_filename)
        if path.is_relative_to(ROOT):
            frames.append({'path': path.relative_to(ROOT).as_posix(),
                           'function': code.co_name, 'line': tb.tb_lineno})
        tb = tb.tb_next
    return {'exception_class': type(error).__name__, 'frames': frames}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-sha256', required=True)
    args = parser.parse_args()
    inputs = RUN / 'original-Machine-profile-inputs-0001.json'
    assert sha(inputs) == args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        path = ROOT / row['path']
        assert not path.is_symlink() and not any(parent.is_symlink() for parent in path.parents)
        assert sha(path) == row['sha256']
    assert sha(API / 'source-manifest.json') == SOURCE
    assert sha(API / 'contract-profile.json') == PROFILE
    output = RUN / 'original-Machine-profile-0001.json'
    assert not output.exists()
    spec = importlib.util.spec_from_file_location('_cal_original_Machine_profile_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    name = '_cal_original_Machine_profile_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    sessions = __import__(name + '.test_custody_sessions', fromlist=['*'])
    sessions.PROFILE = PROFILE
    original = __import__(name + '.test_machine_transport', fromlist=['*'])

    class Fixture(original.MachineTransport):
        def setUp(self):
            super().setUp()
            assert isinstance(self.__dict__.get('authenticated'), dict)
            del self.authenticated

    # Invoke no test method or unittest runner. This is a separate diagnostic
    # episode using the original fixture's actual constructors and authenticator.
    fixture = Fixture('test_01_actual_identity_signature_and_shared_custody')
    phases = []

    def observe(label, callback):
        profiler = cProfile.Profile()
        started = time.monotonic()
        profiler.enable()
        failure = None
        try:
            callback()
        except BaseException as error:
            failure = diagnostic(error)
        finally:
            profiler.disable()
        stats = pstats.Stats(profiler)
        hot = []
        for (filename, line, function), (primitive, total, own, cumulative, _) in stats.stats.items():
            path = Path(filename)
            if path.is_relative_to(ROOT):
                hot.append({'path': path.relative_to(ROOT).as_posix(), 'line': line,
                            'function': function, 'primitive_calls': primitive,
                            'total_calls': total, 'own_seconds': own,
                            'cumulative_seconds': cumulative})
        row = {'phase': label, 'elapsed_seconds': time.monotonic() - started,
               'status': 'ERROR' if failure else 'COMPLETED',
               'failure': failure,
               'top_repository_functions_by_cumulative_time': sorted(hot, key=lambda value: value['cumulative_seconds'], reverse=True)[:25]}
        phases.append(row)
        print(json.dumps({'phase': label, 'status': row['status'],
                          'elapsed_seconds': row['elapsed_seconds'], 'failure': failure}), flush=True)
        return failure is None

    cleanup_failures = []
    authenticated = False
    try:
        if observe('source-replay-and-schema', Fixture.setUpClass):
            if observe('owned-host-session-and-peer', fixture.setUp):
                authenticated = observe('Machine-proof-and-authentication', fixture.authenticated)
    finally:
        for callback in [lambda: fixture.tearDown() if hasattr(fixture, 'service') else None,
                         fixture.doCleanups, Fixture.doClassCleanups]:
            try:
                callback()
            except BaseException as error:
                cleanup_failures.append(diagnostic(error))
    root = getattr(fixture, 'root', None)
    peer = getattr(fixture, 'peer', None)
    resource = getattr(fixture, 'resource', None)
    cleanup = {'owned_workspace_existed': root is not None,
               'owned_workspace_removed': root is not None and not root.exists(),
               'peer_created': peer is not None,
               'peer_closed': peer is not None and peer.closed,
               'Machine_signer_disposed': peer is not None and peer._private_key is None,
               'Session_resource_created': resource is not None,
               'Session_resource_closed': resource is not None and resource.closed,
               'Session_RAM_empty': resource is not None and len(resource.memory) == 0,
               'cleanup_failures': cleanup_failures}
    guard.verify(SOURCE)
    report = {'schema_version': 'lab-original-Machine-cost-observation/v1-candidate',
              'result': 'OBSERVED', 'source_sha256': SOURCE, 'profile_sha256': PROFILE,
              'input_sha256': args.input_sha256, 'phases': phases, 'cleanup': cleanup,
              'actual_authentication_completed': authenticated,
              'maximum_Session_seconds': 900, 'time_bounds_extended': False,
              'source_callbacks_replaced': False, 'clock_replaced': False,
              'permission_cached': False, 'test_methods_invoked': 0,
              'current_Agent_qualified': False, 'whole_API_qualified': False,
              'authority_effect': 'none', 'actual_owner_outcome': None,
              'claim_ceiling': 'One diagnostic episode with cProfile overhead; observed cumulative timings overlap and are not a performance baseline. Full original suites remain required.'}
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'OBSERVED', 'authentication_completed': authenticated, 'cleanup': cleanup}), flush=True)
    assert not cleanup_failures, 'diagnostic cleanup incomplete'
    assert root is None or cleanup['owned_workspace_removed'], 'owned workspace retained'
    assert peer is None or cleanup['peer_closed'] and cleanup['Machine_signer_disposed']
    assert resource is None or cleanup['Session_resource_closed'] and cleanup['Session_RAM_empty']


if __name__ == '__main__':
    main()
