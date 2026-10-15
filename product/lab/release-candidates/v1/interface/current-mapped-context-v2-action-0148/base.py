"""New mapper selector; original native projection bytes remain exactly pinned."""
from pathlib import Path
import importlib.util,sys
SELECTOR_ROOT=Path(__file__).resolve().parent
HERE=SELECTOR_ROOT.parent/'current-mapped-context-v4'
ROOT=HERE.parents[5]
A=SELECTOR_ROOT.parent/'current-source-adapter-v2-action-0148'
NAME='_cal_union_reader_mapper_v2_action_0148'
if NAME not in sys.modules:
    s=importlib.util.spec_from_file_location(NAME,A/'__init__.py',submodule_search_locations=[str(A)])
    m=importlib.util.module_from_spec(s);sys.modules[NAME]=m;s.loader.exec_module(m)
R=__import__(NAME+'.reader',fromlist=['SelectedReader']);BOUNDARY=__import__(NAME+'.boundary',fromlist=['boundary'])
SOURCE_PIN=BOUNDARY.SOURCE_PIN;PACKAGE_PIN=BOUNDARY.PACKAGE_PIN
ADAPTER_PIN='dd12b28311ac0e94eaeaf459560d855134404d94adf80f96be53868438b123c3'
reader=R.SelectedReader(ADAPTER_PIN,SOURCE_PIN,PACKAGE_PIN);records=reader.records;source=reader.adapter.source
sha=source.sha;encoded=source.encoded;load=source.load;require=source.require;binding=source.binding;original=source.original
NAME2='_cal_union_original_mapper_action_0148'
if NAME2 not in sys.modules:
    s=importlib.util.spec_from_file_location(NAME2,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    m=importlib.util.module_from_spec(s);sys.modules[NAME2]=m;s.loader.exec_module(m)
ORIGINAL=__import__(NAME2+'.build',fromlist=['call'])
def verify_source(pin,*,additional_rows=()):
    path=SELECTOR_ROOT/'source-manifest.json';raw=path.read_bytes();require(sha(raw)==pin,'independent union mapper selector changed');m=source.parse(raw)
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'mapper grants no authority')
    require(m['original_mapper_binding']==binding(HERE/'source-manifest.json') and m['original_package_binding']==binding(HERE/'packages/0001/manifest.json') and m['selected_adapter_binding']==binding(A/'source-manifest.json'),'original mapping/new source selection differs')
    BOUNDARY.boundary(ADAPTER_PIN,SOURCE_PIN,PACKAGE_PIN,additional_rows=[*m['files'],*additional_rows])
    require(path.read_bytes()==raw,'mapper selector changed during verification')
    return m
