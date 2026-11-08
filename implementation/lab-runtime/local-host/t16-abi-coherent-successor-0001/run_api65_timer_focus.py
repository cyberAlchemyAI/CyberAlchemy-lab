"""Run inherited all-eleven and wrong-delivery methods on sealed API64 ABI."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, time, unittest
from pathlib import Path
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v65-t16-prepared-open-0001'
SOURCE = '4736074040fab7e5d0a1f7902c11cdfc799fddcba5ca27f750ad711dba124731'
PROFILE = 'f5bedc77377c4a5d3f46e1478c21bea5162ed02861f4ce5c5bbe4641c5221392'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if sha(API / 'source-manifest.json') != SOURCE or sha(API / 'contract-profile.json') != PROFILE:
    raise ValueError('API64 source/profile differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'), importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected ABI differs')
NAME = '_cal_t16_api65_timer_focus'
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
mod.Sessions.invoke = timed_invoke
ids = ['test_27_actual_expiry_timer_disposes']
suite = unittest.TestSuite(mod.Sessions(identity) for identity in ids)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256': SOURCE, 'api_profile_sha256': PROFILE,
                  'method_ids': ids, 'run': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'success': result.wasSuccessful(),
                  'authority_effect': 'none'}, sort_keys=True))
if not result.wasSuccessful():
    raise SystemExit(1)
