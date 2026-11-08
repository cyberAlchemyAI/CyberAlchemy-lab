"""Focused inherited installation positive/negative on exact API62 4.23 ABI."""
import hashlib,importlib,importlib.metadata,importlib.util,json,platform,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v62-t16-abi423-alias-0001'
SOURCE='9c39d58572139a731d610bb0cf174655892106b805985567762c2041a98b94be'
PROFILE='c98076fd86b3fced1d7b356017efd234c0205b62c7f357a28419d709d56e5258'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:raise ValueError('API62 source/profile differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):raise ValueError('selected ABI differs')
NAME='_cal_t16_api62_install_focus'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
importlib.import_module(NAME+'.guard').verify(SOURCE)
mod=importlib.import_module(NAME+'.test_installation_release');mod.SOURCE=SOURCE;mod.PROFILE=PROFILE
ids=['test_01_actual_install_has_verified_original_byte_closure','test_07_real_preimage_change_refuses_before_claim']
suite=unittest.TestSuite(mod.InstallationReleaseAPI(i) for i in ids)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256':SOURCE,'api_profile_sha256':PROFILE,'method_ids':ids,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful(),'authority_effect':'none'},sort_keys=True))
if not result.wasSuccessful():raise SystemExit(1)
