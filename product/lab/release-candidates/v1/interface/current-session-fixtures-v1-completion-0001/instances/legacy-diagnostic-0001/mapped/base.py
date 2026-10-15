"""Exact current source, adapter and native mapping remain separately selected."""
import importlib.metadata
import importlib.util
import platform
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[8]
SOURCE_ROOT=HERE.parent/'source'
ADAPTER_ROOT=HERE.parent/'reader'
SOURCE_PIN='c7f2a64f67fbf0395838605f99121c1ba87e13803af295f7129702c32acdb44a'
PACKAGE_PIN='bfd28bd3a9406afaccaa9c598b3573b23ae54f9532c1c940d1466134926b0907'
ADAPTER_PIN='28958521f36dc4159d8a9f9f2cfd0e0306791e2e3f0b82ca9a0f43903d2d9c2e'
NAME='_cal_legacy_diagnostic_0001_legacy_session_fixture_mapping_reader_v2_0257'
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
