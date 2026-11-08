"""Focused original custody and Session alias cases on exact API63 4.23 ABI."""
import hashlib,importlib,importlib.metadata,importlib.util,json,platform,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001'
SOURCE='fc079aaf4390c8d523cb4036ef31421d146a663cc135694f492e02387b879edf'
PROFILE='022ede7e9c70975bc2aa33d9f99f81b3f16eb7145e6c341734fa3bd5681b2662'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:raise ValueError('API63 source/profile differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):raise ValueError('selected ABI differs')
NAME='_cal_t16_api63_custody_focus'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
importlib.import_module(NAME+'.guard').verify(SOURCE)
mod=importlib.import_module(NAME+'.test_custody_api');mod.SOURCE=SOURCE;mod.PROFILE=PROFILE
ids=['test_01_same_original_reader_objects','test_02_actual_selected_engine_profile_cut']
suite=unittest.TestSuite(mod.OriginalAPI(i) for i in ids)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256':SOURCE,'api_profile_sha256':PROFILE,'method_ids':ids,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful(),'authority_effect':'none'},sort_keys=True))
if not result.wasSuccessful():raise SystemExit(1)
