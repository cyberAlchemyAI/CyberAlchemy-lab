"""Focused inherited old/current method proof on the immutable API61 bridge."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t16-abi423-bridge-0001'
SOURCE='84435a57c990a1d85504cf844a257e6dc3607c81519d368c828449ac8106ffc4'
PROFILE='843ee830613211f6c36c6c822ef32b08e71b5799166485ed24b99d09f053e12c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:
    raise ValueError('selected API61 source/profile differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):
    raise ValueError('selected ABI differs')
NAME='_cal_t16_api61_bridge_proof'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
guard=importlib.import_module(NAME+'.guard')
guard.verify(SOURCE)
old=importlib.import_module(NAME+'.test_metadata_scope');old.PROFILE=PROFILE
current=importlib.import_module(NAME+'.test_current_controls');current.PROFILE=PROFILE
suite=unittest.TestSuite([old.MetadataScopes('test_00_current_metadata_after_original_Assignment_expiry'),
                          current.CurrentControls('test_02_new_source_keeps_original_expired_period_exact')])
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256':SOURCE,'api_profile_sha256':PROFILE,
                  'selected_methods':['MetadataScopes.test_00_current_metadata_after_original_Assignment_expiry',
                                      'CurrentControls.test_02_new_source_keeps_original_expired_period_exact'],
                  'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                  'success':result.wasSuccessful(),'authority_effect':'none'},sort_keys=True))
if not result.wasSuccessful():raise SystemExit(1)
