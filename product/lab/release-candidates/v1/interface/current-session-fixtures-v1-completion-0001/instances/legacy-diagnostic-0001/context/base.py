"""Exact current mapper/raw reader and API protocol with explicit namespaces."""
import importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[8]
MAPPED_PIN='051976107472c9c51c1eb55155e1165fbe6f82f38f3220e28a23d504944ad5b6'
MAPPED_PACKAGE_PIN='f2fe3795e24dbeff492da2593a5d4e759c474e5bbf3ed9f235e8ad4dbf30248a'
API_PROFILE_PIN='c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
mapping_name='_cal_legacy_diagnostic_0001_legacy_fixture_context_mapper_0257'
package(mapping_name,HERE.parent/'mapped')
MAPPED=__import__(mapping_name+'.build',fromlist=['guard'])
reader=MAPPED.reader;records=MAPPED.records
sha=reader.adapter.source.sha;encoded=reader.adapter.source.encoded;load=reader.adapter.source.load
require=reader.adapter.source.require;binding=reader.adapter.source.binding;original=reader.adapter.source.original
api_name='_cal_legacy_diagnostic_0001_legacy_fixture_context_protocol25_0257'
package(api_name,(ROOT/'product/lab/release-candidates/v1/interface')/'api-v25')
API=__import__(api_name+'.protocol',fromlist=['Schemas'])
def dependency_input_bytes(row,selected_external):
    name=row['path'];p=Path(name)
    if p.is_absolute():
        require(row in selected_external,'external dependency input not explicitly selected')
    else:
        require(p.as_posix()==name and '..' not in p.parts and '\\' not in name,'unsafe dependency input path')
        p=ROOT/p
    require(p.is_file() and not p.is_symlink() and not any(a.is_symlink() for a in p.parents),'unsafe dependency input custody')
    raw=p.read_bytes();require(sha(raw)==row['sha256'],'dependency input bytes changed')
    return raw

def preflight(pin):
    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'independent original Context delivery source pin differs');m=load(HERE/'source-manifest.json')
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'Context producer cannot grant authority')
    external=m['external_dependency_bindings']
    require(external==[r for r in m['files'] if Path(r['path']).is_absolute()],'external dependency selection differs')
    for row in m['files']:dependency_input_bytes(row,external)
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'Context producer environment differs')
    MAPPED.guard(MAPPED_PIN)
    require(m['qualified_mapper_source_binding']==binding(MAPPED.HERE/'source-manifest.json') and m['qualified_mapper_package_binding']==binding(MAPPED.HERE/'packages/0001/manifest.json'),'Context source selected mapper differs')
    require(sha((MAPPED.HERE/'packages/0001/manifest.json').read_bytes())==MAPPED_PACKAGE_PIN,'independent Context nativepackage differs')
    require(sha(((ROOT/'product/lab/release-candidates/v1/interface')/'api-v25/contract-profile.json').read_bytes())==API_PROFILE_PIN,'independent current API profile differs')
    return m

fact_name="_cal_lab_fact_read_scope_v1"
fact_path=(ROOT/"product/lab/release-candidates/v1/interface")/"fact-read-scope-v1"
if fact_name not in sys.modules:package(fact_name,fact_path)
FACT_SCOPE=__import__(fact_name+".scope",fromlist=["read_scope"])
require(Path(FACT_SCOPE.__file__).resolve()==fact_path/"scope.py","unselected original fact scope")
