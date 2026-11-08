"""Prove API64 refuses changed mapping dispositions without altering signed files."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, tempfile
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v64-t16-abi423-disposition-0001'
SOURCE = '440f21c46ec20910e371765c32152bb0a18efead7a147724b762a0a46965a675'
PROFILE = 'a4c08349d84a5f8f654eda62fa5ec109ffd6610b5fe8aa474e2197f101aaaf71'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if sha(API / 'source-manifest.json') != SOURCE or sha(API / 'contract-profile.json') != PROFILE:
    raise ValueError('API64 differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'), importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected ABI differs')
NAME = '_cal_t16_api64_changed_disposition'
spec = importlib.util.spec_from_file_location(NAME, API / '__init__.py', submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
importlib.import_module(NAME + '.guard').verify(SOURCE)
source = importlib.import_module(NAME + '.source_bridge')
model = importlib.import_module(NAME + '.guarded_reads')
native = importlib.import_module(NAME + '.native_dispositions')
with source.replay_source(source.CURRENT_LEGACY_NAME) as view:
    with model.model_read_batch(view):
        selected = native.selected(view)
    if selected != native.EXCLUDED:
        raise ValueError('exact signed 604-disposition positive differs')
    original = native.MAPPING
    with tempfile.TemporaryDirectory(prefix='cal-t16-api64-negative-') as temp:
        copied = Path(temp) / 'changed-mapping.json'
        data = json.loads(original.read_bytes())
        if len(data['projection_dispositions']) != 604 or data['source_closure']['accounted_subjects'] != 604:
            raise ValueError('current signed count changed')
        data['projection_dispositions'].pop()
        data['source_closure']['accounted_subjects'] = 603
        copied.write_text(json.dumps(data, sort_keys=True) + '\n')
        real_read_bytes = Path.read_bytes
        def changed_read_bytes(path):
            if path == original:
                return copied.read_bytes()
            return real_read_bytes(path)
        try:
            with patch.object(Path, 'read_bytes', changed_read_bytes):
                with model.model_read_batch(view):
                    native.selected(view)
        except ValueError as error:
            if str(error) != 'native disposition bytes differ':
                raise
            negative = str(error)
        else:
            raise ValueError('changed disposition was accepted')
print(json.dumps({'source_sha256': SOURCE, 'positive_signed_count': 604,
                  'changed_disposition_result': 'REFUSED', 'reason': negative,
                  'original_mapping_sha256': sha(original), 'authority_effect': 'none'}, sort_keys=True))
