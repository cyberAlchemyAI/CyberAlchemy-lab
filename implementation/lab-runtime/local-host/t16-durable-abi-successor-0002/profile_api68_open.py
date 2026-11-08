"""Run inherited all-eleven and wrong-delivery methods on sealed API64 ABI."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, time, unittest, cProfile, pstats
from pathlib import Path
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001'
SOURCE = 'f91edcdba7cb8141405c0931369af02bc6d05c90f03c5cac77ae72165d7e6cb2'
PROFILE = 'ba389526fa3e9e1c9d840632d3b1c038fcc4a648c4e0ed1767b85fe2cf7c0355'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if sha(API / 'source-manifest.json') != SOURCE or sha(API / 'contract-profile.json') != PROFILE:
    raise ValueError('API64 source/profile differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'), importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected ABI differs')
NAME = '_cal_t16_api68_profile_focus'
spec = importlib.util.spec_from_file_location(NAME, API / '__init__.py', submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
importlib.import_module(NAME + '.guard').verify(SOURCE)
mod = importlib.import_module(NAME + '.run_session_checks')
mod.SOURCE = SOURCE
mod.PROFILE = PROFILE
original_invoke = mod.Sessions.invoke
def timed_invoke(self, call, *, raw=None):
    start = time.monotonic()
    profile=cProfile.Profile() if call.get('operation')=='session.open' else None
    if profile is not None:profile.enable()
    try:
        reply = original_invoke(self, call, raw=raw)
        print(json.dumps({'operation': call['operation'], 'kind': reply.get('kind'),
                          'code': reply.get('message', {}).get('code'),
                          'elapsed_seconds': round(time.monotonic() - start, 3),
                          'authority_effect': 'none'}, sort_keys=True), flush=True)
        return reply
    except BaseException as error:
        print(json.dumps({'operation': call.get('operation'), 'exception_type': type(error).__name__,
                          'elapsed_seconds': round(time.monotonic() - start, 3),
                          'authority_effect': 'none'}, sort_keys=True), flush=True)
        raise
    finally:
        if profile is not None:
            profile.disable()
            profile.dump_stats(str(Path(__file__).with_name('api68-open-profile.prof')))
            with Path(__file__).with_name('api68-open-profile-summary.txt').open('w') as stream:
                pstats.Stats(profile,stream=stream).sort_stats('cumulative').print_stats(45)
mod.Sessions.invoke = timed_invoke
ids = ['test_01_actual_private_memory_erased']
suite = unittest.TestSuite(mod.Sessions(identity) for identity in ids)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256': SOURCE, 'api_profile_sha256': PROFILE,
                  'method_ids': ids, 'run': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'success': result.wasSuccessful(),
                  'authority_effect': 'none'}, sort_keys=True))
if not result.wasSuccessful():
    raise SystemExit(1)
