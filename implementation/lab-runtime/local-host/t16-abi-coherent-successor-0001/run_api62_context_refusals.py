"""Isolated exact-pin refusal probes without editing the selected family."""
import hashlib,importlib,importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v62-t16-abi423-alias-0001'
SOURCE='9c39d58572139a731d610bb0cf174655892106b805985567762c2041a98b94be'
PROFILE='c98076fd86b3fced1d7b356017efd234c0205b62c7f357a28419d709d56e5258'
FRESH='fcae80f6c11f43e6b96f4eebdf370a9303b61e10736c8b71e926ed6e6d022245'
OLD='99e701e592490486cf64949b68d5d2e266a176424720af1a944740a1e23a6654'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:raise ValueError('API62 binding differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):raise ValueError('ABI differs')
name='_cal_t16_api62_context_refusals'
spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
importlib.import_module(name+'.guard').verify(SOURCE)
source=importlib.import_module(name+'.source_bridge')
d=source.current_legacy_delivery()
if d.HERE!=ROOT/source.CURRENT_LEGACY_CONTEXT or sha(d.HERE/'source-manifest.json')!=FRESH:raise ValueError('selected family differs')
old_refused=False
try:d.preflight(OLD)
except Exception:old_refused=True
if not old_refused:raise AssertionError('old/wrong-family pin accepted')
base=importlib.import_module(d.__package__+'.base')
copy=HERE/'working/api62-changed-context-copy'
copy.mkdir(parents=True,exist_ok=True)
if any(copy.iterdir()):raise ValueError('changed Context copy directory is not empty')
original=(d.HERE/'source-manifest.json').read_bytes()
(copy/'source-manifest.json').write_bytes(original+b' ')
changed_sha=sha(copy/'source-manifest.json')
try:
    base.HERE=copy
    changed_refused=False
    try:d.preflight(FRESH)
    except Exception:changed_refused=True
finally:base.HERE=d.HERE
if not changed_refused or sha(d.HERE/'source-manifest.json')!=FRESH:raise AssertionError('changed copy accepted or selected family mutated')
(copy/'source-manifest.json').unlink()
copy.rmdir()
print(json.dumps({'api_source_sha256':SOURCE,'selected_context_sha256':FRESH,'old_wrong_family_pin_refused':old_refused,'changed_fresh_context_bytes_refused':changed_refused,'changed_copy_sha256':changed_sha,'selected_context_unchanged':True,'authority_effect':'none'},sort_keys=True))
