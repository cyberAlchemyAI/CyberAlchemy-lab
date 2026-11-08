"""One API60 method through the original 4.23 Source5 union adapter."""
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
TASK = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v60-t16-abi423-0001'
SOURCE = '8fa16946889b0bf9fdb83895d3162c9549bcc867f307729359220d8ecaecb184'
PROFILE = '94427e61f76b5c8b26a4bae2036433863f7e8dccb49eaaaae668bf1a5f72c7c5'
METHOD = 'MetadataScopes.test_00_current_metadata_after_original_Assignment_expiry'
SELECTION = TASK / 'HISTORICAL-SELECTION-0001.json'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
selected = json.loads(SELECTION.read_bytes())
if selected != {
        'schema_version': 'lab-T16-API60-one-historical-method-selection/v1-candidate',
        'api_source_sha256': SOURCE,
        'api_profile_sha256': PROFILE,
        'inherited_method': METHOD,
        'inherited_test_file_sha256': sha(API / 'test_metadata_scope.py'),
        'historical_adapter_manifest_sha256': sha(ROOT / 'product/lab/release-candidates/v1/interface/current-source-adapter-v2-action-0148/source-manifest.json'),
        'runner_sha256': sha(Path(__file__)),
        'dependency_selection_sha256': sha(ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'),
        'installed_receipt_sha256': sha(INSTALL / 'installation.json'),
        'loader_sha256': sha(INSTALL / 'lib/abi/ld-linux-x86-64.so.2'),
        'python_sha256': sha(INSTALL / 'bin/python'),
        'selected_method_count': 1,
        'authority_effect': 'none'}:
    raise ValueError('historical selected runner differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'),
        importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected 4.23 ABI differs')
name = 't16_api60_historical'
spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                               submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[name] = package
spec.loader.exec_module(package)
guard = importlib.import_module(name + '.guard')
guard.verify(SOURCE)
tests = importlib.import_module(name + '.test_metadata_scope')
tests.PROFILE = PROFILE
case = tests.MetadataScopes(METHOD.split('.')[1])
result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
print(json.dumps({'api_source_sha256': SOURCE, 'inherited_method': METHOD,
                  'run': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'success': result.wasSuccessful()}, sort_keys=True))
if not result.wasSuccessful(): raise SystemExit(1)
