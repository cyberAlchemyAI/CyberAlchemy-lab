"""Exact current source, adapter and native mapping remain separately selected."""
import importlib.metadata
import importlib.util
import platform
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
SOURCE_ROOT=HERE.parent/'current-participation-v4'
ADAPTER_ROOT=HERE.parent/'current-source-adapter-v3'
SOURCE_PIN='b5130870913b980398dab64a1c33067231a042fe9d06f6d35f5afedaaffa96f2'
PACKAGE_PIN='b4381aa92a3519f1536bb4a64a74b4af0d0d3556bfc35a9254b8489bab301092'
ADAPTER_PIN='debbe5c1eeab71fc0bcf565c317411904a4b942d51bf5e74f6d4a3df0d90e11d'
NAME='_cal_current_episode_source_for_native_mapping_v3'
spec=importlib.util.spec_from_file_location(NAME,ADAPTER_ROOT/'__init__.py',submodule_search_locations=[str(ADAPTER_ROOT)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
R=__import__(NAME+'.reader',fromlist=['*'])
reader=R.SelectedReader(ADAPTER_PIN,SOURCE_PIN,PACKAGE_PIN)
records=reader.records
source=reader.adapter.source
sha=source.sha;encoded=source.encoded;load=source.load;require=source.require;binding=source.binding;original=source.original
def verify_source(pin):
    path=HERE/'source-manifest.json'
    require(sha(path.read_bytes())==pin,'independent current native mapper source differs')
    m=load(path)
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'mapper source grants no authority')
    for row in m['files']:original(row)
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'current mapper environment differs')
    require(m['original_source_binding']==binding(SOURCE_ROOT/'source-manifest.json') and m['original_package_binding']==binding(SOURCE_ROOT/'packages/0001/manifest.json') and m['adapter_source_binding']==binding(ADAPTER_ROOT/'source-manifest.json'),'independent producer or adapter selection differs')
    reader.guard();reader.package(SOURCE_PIN,PACKAGE_PIN)
    return m
