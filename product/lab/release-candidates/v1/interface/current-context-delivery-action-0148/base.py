"""Exact current mapper/raw reader and API protocol with explicit namespaces."""
import importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
MAPPED_PIN='44a2313f0bcad49e251d1ae7ef8e99d2707f9bb2534cdea2acf6959e046fad61'
MAPPED_PACKAGE_PIN='61eba56461293d8e056b71e2066d1ceec40aab633d8a4caf3ddaa550c57b981e'
API_PROFILE_PIN='c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
mapping_name='_cal_context_union_mapper_action_0148'
package(mapping_name,HERE.parent/'current-mapped-context-action-0148')
MAPPED=__import__(mapping_name+'.build',fromlist=['guard'])
reader=MAPPED.reader;records=MAPPED.records
load_bytes=reader.adapter.source.parse
sha=reader.adapter.source.sha;encoded=reader.adapter.source.encoded;load=reader.adapter.source.load
require=reader.adapter.source.require;binding=reader.adapter.source.binding;original=reader.adapter.source.original
api_name='_cal_context_current_protocol_v25_v9'
package(api_name,HERE.parent/'api-v25')
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
    selection=m['execution_dependency_binding']
    require(selection['path']==(HERE/'EXECUTION-DEPENDENCIES.json').relative_to(ROOT).as_posix(),'unselected execution manifest')
    execution=load_bytes(dependency_input_bytes(selection,external))
    require(set(execution)=={'schema_version','files','external_dependency_bindings','selection_reasons','parent_qualification_binding','observed_import_phase_binding','authority_effect','actual_owner_outcome','closure_status'},'closed execution selection required')
    require(execution['schema_version']=='lab-Context-execution-dependencies/v1-candidate' and execution['authority_effect']=='none' and execution['actual_owner_outcome'] is None and execution['closure_status']=='declared-for-successor-qualification','execution selection cannot claim permission or qualification')
    selected=execution['files'];names=[row['path'] for row in selected]
    require(names==sorted(set(names)) and bool(names),'complete unique ordered execution set required')
    qualification={row['path']:row for row in m['files']}
    require(all(qualification.get(row['path'])==row for row in selected),'execution dependency outside frozen qualification source')
    require(set(execution['selection_reasons'])==set(names) and all(execution['selection_reasons'][name] for name in names),'explicit execution selection reasons required')
    selected_external=execution['external_dependency_bindings']
    require(selected_external==[row for row in selected if Path(row['path']).is_absolute()],'execution external selection differs')
    mandatory=['__init__.py','base.py','build.py','control.py','generation.py','implementation-binding.json','lifetime-policy.json']
    require(all((HERE/name).relative_to(ROOT).as_posix() in names for name in mandatory),'required Context execution input missing')
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'Context producer environment differs')
    MAPPED.guard(MAPPED_PIN,additional_rows=[*selected,selection])
    require(m['qualified_mapper_source_binding']==binding(MAPPED.SELECTOR_ROOT/'source-manifest.json') and m['qualified_mapper_package_binding']==binding(MAPPED.HERE/'packages/0001/manifest.json'),'Context source selected mapper differs')
    require(sha((MAPPED.HERE/'packages/0001/manifest.json').read_bytes())==MAPPED_PACKAGE_PIN,'independent Context nativepackage differs')
    require(sha((HERE.parent/'api-v25/contract-profile.json').read_bytes())==API_PROFILE_PIN,'independent current API profile differs')
    return m

# One explicit shared helper namespace for the producer and API successor.
fact_name='_cal_lab_fact_read_scope_v1'
fact_path=HERE.parent/'fact-read-scope-v1'
if fact_name not in sys.modules:package(fact_name,fact_path)
FACT_SCOPE=__import__(fact_name+'.scope',fromlist=['read_scope'])
require(Path(FACT_SCOPE.__file__).resolve()==fact_path/'scope.py','unselected fact scope kernel')
