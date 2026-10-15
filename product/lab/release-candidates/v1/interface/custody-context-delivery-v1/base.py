"""Exact current mapper/raw reader and API protocol with explicit namespaces."""
import importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
MAPPED_PIN='759c492b4d6551acb06aff6c71c88039dbc6ea9df374be0bd64adf9558b7f27d'
MAPPED_PACKAGE_PIN='fe205340b240838aad5dd3d4cd1a03115b1b9dc4b939358334a0ca4dbd7e6c34'
API_PROFILE_PIN='506343b60e960c98fe42f427608d8801be0c6f9139c8d0957474d313a967c45b'
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
mapping_name='_cal_context_original_mapper_v1'
package(mapping_name,HERE.parent/'custody-mapped-context-v2')
MAPPED=__import__(mapping_name+'.build',fromlist=['guard'])
reader=MAPPED.reader;records=MAPPED.records
sha=reader.adapter.source.sha;encoded=reader.adapter.source.encoded;load=reader.adapter.source.load
require=reader.adapter.source.require;binding=reader.adapter.source.binding;original=reader.adapter.source.original
api_name='_cal_context_original_protocol_v16_v1'
package(api_name,HERE.parent/'api-v16')
API=__import__(api_name+'.protocol',fromlist=['Schemas'])
def preflight(pin):
    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'independent original Context delivery source pin differs');m=load(HERE/'source-manifest.json')
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'Context producer cannot grant authority')
    for row in m['files']:original(row)
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'Context producer environment differs')
    MAPPED.guard(MAPPED_PIN)
    require(m['qualified_mapper_source_binding']==binding(MAPPED.HERE/'source-manifest.json') and m['qualified_mapper_package_binding']==binding(MAPPED.HERE/'packages/0001/manifest.json'),'Context source selected mapper differs')
    require(sha((MAPPED.HERE/'packages/0001/manifest.json').read_bytes())==MAPPED_PACKAGE_PIN,'independent Context nativepackage differs')
    require(sha((HERE.parent/'api-v16/contract-profile.json').read_bytes())==API_PROFILE_PIN,'independent current API profile differs')
    return m
