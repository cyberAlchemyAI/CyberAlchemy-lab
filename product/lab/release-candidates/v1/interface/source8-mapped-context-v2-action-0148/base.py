"""Exact current source, adapter and native mapping remain separately selected."""
import importlib.metadata
import importlib.util
import platform
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
SOURCE_ROOT=HERE.parent/'current-participation-v8'
ADAPTER_ROOT=HERE.parent/'current-source-adapter-v7'
SOURCE_PIN='cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36'
PACKAGE_PIN='c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f'
ADAPTER_PIN='78d8150086ed41f6f2c2218805a2387caab1e5931b2619a894330557cb30d23c'
NAME='_cal_source8_native_mapping_reader_action_0148'
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
