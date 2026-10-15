"""Exact current mapper/raw reader and API protocol with explicit namespaces."""
import importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
MAPPED_PIN='cdb291afc961952edaee4f1327d89a0decc7ea6ec330bd162c6f571d50657685'
MAPPED_PACKAGE_PIN='911d5f13514737d8f529b0199a0f37340e1a974ac63b53f3f9c2d5fe0e47b9f1'
API_PROFILE_PIN='c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
mapping_name='_cal_context_current_mapper_v2_delivery_v2'
package(mapping_name,HERE.parent/'current-mapped-context-v2')
MAPPED=__import__(mapping_name+'.build',fromlist=['guard'])
reader=MAPPED.reader;records=MAPPED.records
sha=reader.adapter.source.sha;encoded=reader.adapter.source.encoded;load=reader.adapter.source.load
require=reader.adapter.source.require;binding=reader.adapter.source.binding;original=reader.adapter.source.original
api_name='_cal_context_current_protocol_v25_v2'
package(api_name,HERE.parent/'api-v25')
API=__import__(api_name+'.protocol',fromlist=['Schemas'])
def preflight(pin):
    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'independent original Context delivery source pin differs');m=load(HERE/'source-manifest.json')
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'Context producer cannot grant authority')
    for row in m['files']:original(row)
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'Context producer environment differs')
    MAPPED.guard(MAPPED_PIN)
    require(m['qualified_mapper_source_binding']==binding(MAPPED.HERE/'source-manifest.json') and m['qualified_mapper_package_binding']==binding(MAPPED.HERE/'packages/0001/manifest.json'),'Context source selected mapper differs')
    require(sha((MAPPED.HERE/'packages/0001/manifest.json').read_bytes())==MAPPED_PACKAGE_PIN,'independent Context nativepackage differs')
    require(sha((HERE.parent/'api-v25/contract-profile.json').read_bytes())==API_PROFILE_PIN,'independent current API profile differs')
    return m
