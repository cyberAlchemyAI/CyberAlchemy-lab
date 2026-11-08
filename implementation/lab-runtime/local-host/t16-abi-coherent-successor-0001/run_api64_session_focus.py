"""Run inherited all-eleven and wrong-delivery methods on sealed API64 ABI."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, time, unittest
from pathlib import Path
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v64-t16-abi423-disposition-0001'
SOURCE = '440f21c46ec20910e371765c32152bb0a18efead7a147724b762a0a46965a675'
PROFILE = 'a4c08349d84a5f8f654eda62fa5ec109ffd6610b5fe8aa474e2197f101aaaf71'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if sha(API / 'source-manifest.json') != SOURCE or sha(API / 'contract-profile.json') != PROFILE:
    raise ValueError('API64 source/profile differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'), importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected ABI differs')
NAME = '_cal_t16_api64_session_focus'
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
ids = ['test_00_all_eleven_actual_operations', 'test_14_wrong_original_delivery_denied']
suite = unittest.TestSuite(mod.Sessions(identity) for identity in ids)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256': SOURCE, 'api_profile_sha256': PROFILE,
                  'method_ids': ids, 'run': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'success': result.wasSuccessful(),
                  'authority_effect': 'none'}, sort_keys=True))
if not result.wasSuccessful():
    raise SystemExit(1)
