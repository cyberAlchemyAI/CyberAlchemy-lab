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
SOURCE_PIN='2a13711a7acae4983cd32904ac4c2ced1cab4e83c32ae96c51462d1226bcf887'
PACKAGE_PIN='ef9619cd56ec22d93dceef04bc1138e2aec2a206db6149529fb156ae48bd3fc4'
ADAPTER_PIN='04081f3d717c5b94178e399a58217e055e3f860fa5062fbb01f30b3c135bc07a'
NAME='_cal_completion_diagnostic_0004_mapping_reader'
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
