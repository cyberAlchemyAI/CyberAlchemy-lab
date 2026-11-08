"""Direct current-family native disposition guard diagnostic on selected ABI."""
import hashlib,importlib,importlib.metadata,importlib.util,json,platform,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001'
SOURCE='fc079aaf4390c8d523cb4036ef31421d146a663cc135694f492e02387b879edf'
PROFILE='022ede7e9c70975bc2aa33d9f99f81b3f16eb7145e6c341734fa3bd5681b2662'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:raise ValueError('API63 differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):raise ValueError('ABI differs')
NAME='_cal_t16_api63_native_disposition_diagnostic'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
importlib.import_module(NAME+'.guard').verify(SOURCE)
source=importlib.import_module(NAME+'.source_bridge')
model=importlib.import_module(NAME+'.guarded_reads')
native=importlib.import_module(NAME+'.native_dispositions')
try:
    with source.replay_source(source.CURRENT_LEGACY_NAME) as view:
        with model.model_read_batch(view):native.selected(view)
except Exception as exc:
    print(json.dumps({'result':'REFUSED','exception_type':type(exc).__name__,'message':str(exc),'actual_mapping_count':604,'selected_api_source_sha256':SOURCE,'authority_effect':'none'},sort_keys=True))
    raise
