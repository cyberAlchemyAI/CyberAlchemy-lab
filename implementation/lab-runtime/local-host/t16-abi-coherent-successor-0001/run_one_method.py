"""One inherited API53 current-source method in the selected API60/4.23 cut."""
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
SELECTION = TASK / 'RUNNER-SELECTION-0001.json'
sys.path.insert(0, str(INSTALL / 'deps'))
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v60-t16-abi423-0001'
SOURCE = '8fa16946889b0bf9fdb83895d3162c9549bcc867f307729359220d8ecaecb184'
PROFILE = '94427e61f76b5c8b26a4bae2036433863f7e8dccb49eaaaae668bf1a5f72c7c5'
METHOD = 'CurrentControls.test_05_actual_guarded_byte_model_origin_and_body'

selected = json.loads(SELECTION.read_bytes())
if selected != {
        'schema_version': 'lab-T16-API60-one-method-selection/v1-candidate',
        'api_source_sha256': SOURCE,
        'api_profile_sha256': PROFILE,
        'inherited_method': METHOD,
        'inherited_test_file_sha256': hashlib.sha256((API / 'test_current_controls.py').read_bytes()).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency_selection_sha256': hashlib.sha256((ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json').read_bytes()).hexdigest(),
        'installed_receipt_sha256': hashlib.sha256((INSTALL / 'installation.json').read_bytes()).hexdigest(),
        'loader_sha256': hashlib.sha256((INSTALL / 'lib/abi/ld-linux-x86-64.so.2').read_bytes()).hexdigest(),
        'python_sha256': hashlib.sha256((INSTALL / 'bin/python').read_bytes()).hexdigest(),
        'family_source_manifest_sha256': hashlib.sha256((ROOT / 'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0/source/source-manifest.json').read_bytes()).hexdigest(),
        'family_context_manifest_sha256': hashlib.sha256((ROOT / 'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0/context/source-manifest.json').read_bytes()).hexdigest(),
        'selected_method_count': 1,
        'authority_effect': 'none',
    }:
    raise ValueError('focused selected runner differs')

if (platform.python_version(), importlib.metadata.version('jsonschema'),
        importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected 4.23 ABI differs')
for name, expected in (('source-manifest.json', SOURCE), ('contract-profile.json', PROFILE)):
    if hashlib.sha256((API / name).read_bytes()).hexdigest() != expected:
        raise ValueError('selected API60 byte differs: ' + name)
name = 't16_api60_selected'
spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                               submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[name] = package
spec.loader.exec_module(package)
guard = importlib.import_module(name + '.guard')
selected = guard.verify(SOURCE)
if selected['environment']['jsonschema'] != '4.23.0':
    raise ValueError('API60 environment differs')
tests = importlib.import_module(name + '.test_current_controls')
tests.PROFILE = PROFILE
case = tests.CurrentControls(METHOD.split('.')[1])
result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
print(json.dumps({'api_source_sha256': SOURCE, 'api_profile_sha256': PROFILE,
                  'inherited_method': METHOD, 'run': result.testsRun,
                  'failures': len(result.failures), 'errors': len(result.errors),
                  'success': result.wasSuccessful()}, sort_keys=True))
if not result.wasSuccessful():
    raise SystemExit(1)
