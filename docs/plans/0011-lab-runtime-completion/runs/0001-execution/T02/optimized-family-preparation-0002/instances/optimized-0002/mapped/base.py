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
SOURCE_PIN='ff741a6debeeedd890e73014d52c673fd36a3da232e7c39e2e9696c69c59e617'
PACKAGE_PIN='204a8072fd725f62c8e61058a6254d0118c937603e600139efa7cbace1e96f04'
ADAPTER_PIN='86b27e7ff838350cf45c69f1823cb0555f0cc9bdd51c46431156ad3c122646f4'
NAME='_cal_completion_optimized_0002_mapping_reader'
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
