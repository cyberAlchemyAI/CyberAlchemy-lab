"""Closed mapper source and independently selected original-body source namespace."""
import hashlib,importlib.metadata,importlib.util,json,platform,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
SOURCE_ROOT=HERE.parent/'custody-participation-v1'
SOURCE_PIN='129eae6c7ceb445c6d79bdc54c6abf6da6e9fa312fc6d9205d1a5c18c7cfe14b'
PACKAGE_PIN='e42b503ad366c8c4920eb9380a65190b2910892f2481e62ca260de12692598d7'
name='_cal_original_source_for_mapping_v1'
spec=importlib.util.spec_from_file_location(name,SOURCE_ROOT/'__init__.py',submodule_search_locations=[str(SOURCE_ROOT)])
package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
reader=__import__(name+'.reader',fromlist=['open_signed']);records=__import__(name+'.records',fromlist=['targets'])
source=reader.adapter.source
sha=source.sha;encoded=source.encoded;load=source.load;require=source.require;binding=source.binding;original=source.original
def verify_source(pin):
    path=HERE/'source-manifest.json';require(sha(path.read_bytes())==pin,'independent native mapper source pin differs');m=load(path)
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'mapper source cannot grant authority')
    for row in m['files']:original(row)
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'mapper environment differs')
    require(m['original_source_binding']==binding(SOURCE_ROOT/'source-manifest.json')
        and m['original_package_binding']==binding(SOURCE_ROOT/'packages/0001/manifest.json'),'independently selected original source differs')
    source.verify_source(SOURCE_PIN);reader.package(SOURCE_PIN,PACKAGE_PIN)
    return m
