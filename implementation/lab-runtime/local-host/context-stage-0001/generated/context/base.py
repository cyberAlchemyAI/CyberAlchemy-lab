"""Exact current mapper/raw reader and API protocol with explicit namespaces."""

def _t35_effect_refused():
    raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')

def _t35_binding_path(path):
    from pathlib import Path, PurePosixPath
    value = Path(path)
    name = value.as_posix()
    if not value.is_absolute() or '//' in name or any((x in ('.', '..') for x in name.split('/'))):
        raise ValueError('noncanonical generated binding path')
    family = PurePosixPath(Path(__file__).resolve().parent)
    snapshot = PurePosixPath(Path(__file__).resolve().parent.parents[5])
    item = PurePosixPath(name)
    if family in item.parents:
        return name
    if snapshot in item.parents:
        return str(item.relative_to(snapshot))
    raise ValueError('generated path outside external output and input snapshot')
import importlib.metadata, importlib.util, json, platform, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
MAPPED_PIN = '0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358'
MAPPED_PACKAGE_PIN = '0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea'
API_PROFILE_PIN = '2ef0657841ba21ba2b68c7987654817ea39deda669bf89207fa406aa89279d64'

def package(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
mapping_name = '_cal_legacy_context_dev_20261020_0003_legacy_fixture_context_mapper_0257'
package(mapping_name, HERE.parent / 'docker-mapped-20261020-0001')
MAPPED = __import__(mapping_name + '.build', fromlist=['guard'])
reader = MAPPED.reader
records = MAPPED.records
sha = reader.adapter.source.sha
encoded = reader.adapter.source.encoded
load = reader.adapter.source.load
require = reader.adapter.source.require
binding = reader.adapter.source.binding
original = reader.adapter.source.original
api_name = '_cal_legacy_context_dev_20261020_0003_legacy_fixture_context_protocol25_0257'
package(api_name, ROOT / 'product/lab/release-candidates/v1/interface' / 'api-v25')
API = __import__(api_name + '.protocol', fromlist=['Schemas'])

def dependency_input_bytes(row, selected_external):
    from _t35_external_runtime_capture import read
    require(row in selected_external or not Path(row['path']).is_absolute(), 'external dependency input not explicitly selected')
    return read(row)

def preflight(pin):
    m = reader.adapter.source.parse(original({'path': _t35_binding_path(HERE / 'source-manifest.json'), 'sha256': pin}))
    require(m['authority_effect'] == 'none' and m['actual_owner_outcome'] is None, 'Context producer cannot grant authority')
    external = m['external_dependency_bindings']
    require(external == [r for r in m['files'] if Path(r['path']).is_absolute()], 'external dependency selection differs')
    reader.adapter.source.B.verify_inputs(m['files'], selected_external=external)
    require(m['environment'] == {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema'), 'cryptography': importlib.metadata.version('cryptography')}, 'Context producer environment differs')
    MAPPED.guard(MAPPED_PIN)
    require(m['qualified_mapper_source_binding'] == binding(MAPPED.HERE / 'source-manifest.json') and m['qualified_mapper_package_binding'] == binding(MAPPED.HERE / 'packages/0001/manifest.json'), 'Context source selected mapper differs')
    require(sha((MAPPED.HERE / 'packages/0001/manifest.json').read_bytes()) == MAPPED_PACKAGE_PIN, 'independent Context nativepackage differs')
    require(sha((ROOT / 'product/lab/release-candidates/v1/interface' / 'api-v25/contract-profile.json').read_bytes()) == API_PROFILE_PIN, 'independent current API profile differs')
    return m
fact_name = '_cal_lab_fact_read_scope_v1'
fact_path = ROOT / 'product/lab/release-candidates/v1/interface' / 'fact-read-scope-v1'
if fact_name not in sys.modules:
    package(fact_name, fact_path)
FACT_SCOPE = __import__(fact_name + '.scope', fromlist=['read_scope'])
require(Path(FACT_SCOPE.__file__).resolve() == fact_path / 'scope.py', 'unselected original fact scope')
