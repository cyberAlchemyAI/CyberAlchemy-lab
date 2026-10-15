"""Exact current mapper/raw reader and API protocol with explicit namespaces."""
import importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[7]
MAPPED_PIN='2be51c49c7ec785c174f7e42ed20c1e15a93bcc2801455e1c929bad633214663'
MAPPED_PACKAGE_PIN='7db998cc452a7e978ef948061276f2af48f44efced5b04296bc941a17bcd5f51'
API_PROFILE_PIN='2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
mapping_name='_cal_completion_context_revision_0002_mapper'
package(mapping_name,ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0001/instances/optimized-0001/mapped')
MAPPED=__import__(mapping_name+'.build',fromlist=['guard'])
reader=MAPPED.reader;records=MAPPED.records
load_bytes=reader.adapter.source.parse
sha=reader.adapter.source.sha;encoded=reader.adapter.source.encoded;load=reader.adapter.source.load
require=reader.adapter.source.require;binding=reader.adapter.source.binding;original=reader.adapter.source.original
api_name='_cal_source8_context_protocol_api12'
package(api_name,(ROOT/'product/lab/release-candidates/v1/interface')/'api-integration-v12')
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
    m=load_bytes(original({'path':(HERE/'source-manifest.json').relative_to(ROOT).as_posix(),'sha256':pin}))
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'Context cannot grant authority')
    names=[r['path'] for r in m['files']]
    require(names==sorted(set(names)),'Context source closure must be unique')
    reader.adapter.source.B.verify_inputs(m['files'],selected_external=m['external_dependency_bindings'])
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'Context environment differs')
    MAPPED.guard(MAPPED_PIN)
    require(m['qualified_mapper_source_binding']==binding(MAPPED.HERE/'source-manifest.json') and m['qualified_mapper_package_binding']==binding(MAPPED.HERE/'packages/0001/manifest.json'),'Context mapper selection differs')
    require(sha((MAPPED.HERE/'packages/0001/manifest.json').read_bytes())==MAPPED_PACKAGE_PIN,'Context native package differs')
    require(sha(((ROOT/'product/lab/release-candidates/v1/interface')/'api-integration-v12/contract-profile.json').read_bytes())==API_PROFILE_PIN,'original schema profile differs')
    return m

# One explicit shared helper namespace for the producer and API successor.
fact_name='_cal_lab_fact_read_scope_v1'
fact_path=(ROOT/'product/lab/release-candidates/v1/interface')/'fact-read-scope-v1'
if fact_name not in sys.modules:package(fact_name,fact_path)
FACT_SCOPE=__import__(fact_name+'.scope',fromlist=['read_scope'])
require(Path(FACT_SCOPE.__file__).resolve()==fact_path/'scope.py','unselected fact scope kernel')
