"""Exact current source, adapter and native mapping remain separately selected."""
import importlib.metadata
import importlib.util
import platform
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
SOURCE_ROOT=HERE.parent/'source'
ADAPTER_ROOT=HERE.parent/'reader'
SOURCE_PIN='5b6bd1fc683fc56b3aaafe5c7a738a45244da290132215288965a2d8a7ec39ad'
PACKAGE_PIN='8a78ca32bb59ac634d5351b1b166bce6022cdc51ae4c548144585af00843d863'
ADAPTER_PIN='a61c77b70118615a28f40d6986b3c182c2496ba96f6b2d5581b8fc11e6a33782'
NAME='_cal_completion_optimized_0005_mapping_reader'
spec=importlib.util.spec_from_file_location(NAME,ADAPTER_ROOT/'__init__.py',submodule_search_locations=[str(ADAPTER_ROOT)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
R=__import__(NAME+'.reader',fromlist=['*'])
reader=R.CurrentFixtureReader(ADAPTER_PIN,SOURCE_PIN,PACKAGE_PIN)
records=reader.records
source=reader.adapter.source
sha=source.sha;encoded=source.encoded;load=source.load;require=source.require;binding=source.binding;original=source.original
def verify_source(pin):
    path=HERE/'source-manifest.json'
    m=source.parse(original({'path':path.relative_to(ROOT).as_posix(),'sha256':pin}))
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'mapper source grants no authority')
    source.B.verify_inputs(m['files'])
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'current mapper environment differs')
    require(m['original_source_binding']==binding(SOURCE_ROOT/'source-manifest.json') and m['original_package_binding']==binding(SOURCE_ROOT/'packages/0001/manifest.json') and m['adapter_source_binding']==binding(ADAPTER_ROOT/'source-manifest.json'),'independent producer or adapter selection differs')
    reader.guard();reader.package(SOURCE_PIN,PACKAGE_PIN)
    return m
