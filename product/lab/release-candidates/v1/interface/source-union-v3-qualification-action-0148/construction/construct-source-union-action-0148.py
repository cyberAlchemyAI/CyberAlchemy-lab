from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';A=I/'current-source-adapter-action-0148'
A.mkdir(mode=0o700)
def put(name,text):(A/name).write_text(text)
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
put('__init__.py','"""Separately selected fresh union source adapter; original immutable replay and eligibility."""\n')
put('base.py', '''"""Original frozen reader helpers in a distinct, explicitly selected family."""
import importlib.util,sys
from pathlib import Path
ADAPTER_ROOT=Path(__file__).resolve().parent
PARENT_ROOT=ADAPTER_ROOT.parent/'current-source-adapter-v4'
NAME='_cal_source_union_original_adapter_action_0148'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PARENT_ROOT/'__init__.py',submodule_search_locations=[str(PARENT_ROOT)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
parent=__import__(NAME+'.reader',fromlist=['SelectedReader'])
B=parent.adapter.source.B;C=parent.adapter.source.C;records=parent.records
PRODUCER_ROOT=B.HERE;HERE=B.HERE;ROOT=B.ROOT
sha=B.sha;encoded=B.encoded;parse=B.parse;load=B.load;require=B.require;binding=B.binding;original=B.original;verify_source=B.verify_source;original_bridge=B.original_bridge;cut=B.cut
''')
# Original guard filesystem engine is byte-preserved, independently selected.
shutil.copyfile(I/'api-integration-v7/guard.py',A/'bulk.py')
put('boundary.py', '''"""Fresh complete Source5/Reader4 union; facts deduplicated only inside this invocation."""
from dataclasses import asdict
import importlib.metadata,platform
from .base import *
from .bulk import _verify_files
SOURCE_PIN='dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4'
PACKAGE_PIN='8c34a37e1dfa185fc21f323aa08d99c4f097b413c3e0fcf90c0da6d98c731aaf'
PARENT_PIN='be0e1857cf667100ea2dd9c6b115d11032f28fbfdfba4e9234d94aff84f19fee'
def boundary(adapter_pin,source_pin,package_pin):
    require(source_pin==SOURCE_PIN and package_pin==PACKAGE_PIN,'independent original Source5 pins differ')
    ownraw=(ADAPTER_ROOT/'source-manifest.json').read_bytes()
    require(sha(ownraw)==adapter_pin,'independent selected union adapter differs')
    own=parse(ownraw)
    source_raw=(PRODUCER_ROOT/'source-manifest.json').read_bytes()
    parent_raw=(PARENT_ROOT/'source-manifest.json').read_bytes()
    package_raw=(PRODUCER_ROOT/'packages/0001/manifest.json').read_bytes()
    require(sha(source_raw)==source_pin and sha(parent_raw)==PARENT_PIN and sha(package_raw)==package_pin,'original source/adapter/package bytes changed')
    source_manifest=parse(source_raw);parent_manifest=parse(parent_raw);package_manifest=parse(package_raw)
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    require(source_manifest['environment']==own['environment']==environment,'independent source environment differs')
    for m in [source_manifest,parent_manifest,package_manifest,own]:require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'source grants no authority')
    require(own['original_source_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and own['original_package_binding']==binding(PRODUCER_ROOT/'packages/0001/manifest.json') and own['original_adapter_binding']==binding(PARENT_ROOT/'source-manifest.json'),'selected original source family differs')
    rows={}
    for row in [*source_manifest['files'],*parent_manifest['files'],*package_manifest['files'],*own['files']]:
        require(type(row) is dict and set(row)=={'path','sha256'},'closed exact source binding required')
        require(row['path'] not in rows or rows[row['path']]==row,'conflicting selected source digest')
        rows[row['path']]=row
    _verify_files(ROOT,[rows[name] for name in sorted(rows)])
    require(parent_manifest['producer_source_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and parent_manifest['producer_package_binding']==binding(PRODUCER_ROOT/'packages/0001/manifest.json'),'original parent reader producer differs')
    declared=B.episode();value=package_manifest;path=PRODUCER_ROOT/'packages/0001/manifest.json'
    require(set(value)==set('schema_version files source_manifest_binding archive_binding expected_replay_binding period_binding episode_contract_binding visibility public_package_export_allowed authority_effect actual_owner_outcome'.split()),'closed current episode package required')
    require(value['schema_version']=='lab-owned-current-participation-package/v1-candidate' and value['source_manifest_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and value['episode_contract_binding']==binding(PRODUCER_ROOT/'episode-contract.json'),'current episode package source differs')
    require(value['visibility']=='private-candidate-original-custody' and value['public_package_export_allowed'] is False,'original source public export not authorized')
    prefix=(PRODUCER_ROOT/'packages/0001').relative_to(ROOT).as_posix()+'/'
    names=[row['path'] for row in value['files']]
    require(len(names)==len(set(names)) and all(name.startswith(prefix) for name in names),'current package closure escaped')
    require(set(names)=={p.relative_to(ROOT).as_posix() for p in path.parent.rglob('*') if p.is_file() and p!=path},'complete current package tree differs')
    period=parse(original(value['period_binding']));C.validate_period(period,declared)
    expected=parse(original(value['expected_replay_binding']))
    require(expected['engine_pins']==asdict(B.selected_pins()),'original exact executable pins differ')
    require((ADAPTER_ROOT/'source-manifest.json').read_bytes()==ownraw and (PRODUCER_ROOT/'source-manifest.json').read_bytes()==source_raw and (PARENT_ROOT/'source-manifest.json').read_bytes()==parent_raw and path.read_bytes()==package_raw,'selected manifest changed during verification')
    return source_manifest,value,expected,own
''')
original=(I/'current-source-adapter-v4/adapter.py').read_text();guard=original[original.index('    def guard(self):'):original.index('    def closure_report(self):')]
guard=guard.replace('        verify_package(self.package_pin)\n','')
put('adapter.py','''"""New selected guard; byte-identical original constructor/replay/schema/eligibility callbacks."""
from .base import parent,source if False else parent
'''.replace('from .base import parent,source if False else parent','from .base import parent\nsource=parent.adapter.source;cut=parent.adapter.cut\nmodel=parent.adapter.model;eligibility=parent.adapter.eligibility\nCARRIERS=parent.adapter.CARRIERS;CURRENT=parent.adapter.CURRENT\nEXCLUDED_CATEGORIES=parent.adapter.EXCLUDED_CATEGORIES\nclass SignedSources(parent.adapter.SignedSources):')+guard)
put('reader.py','''"""Explicitly pinned host source selection; complete fresh deduplicated boundary."""
from contextlib import contextmanager
from .base import *
from . import adapter
from .boundary import boundary
class SelectedReader:
    def __init__(self,adapter_pin,source_pin,package_pin):
        self.adapter_pin=adapter_pin;self.source_pin=source_pin;self.package_pin=package_pin
        self.HERE=PRODUCER_ROOT;self.adapter=adapter;self.Inspection=parent.Inspection;self.records=records
        self.guard()
    def guard(self):return boundary(self.adapter_pin,self.source_pin,self.package_pin)[3]
    def package(self,source_pin,package_pin):
        source,m,expected,_=boundary(self.adapter_pin,source_pin,package_pin)
        require(source_pin==self.source_pin and package_pin==self.package_pin,'independently selected source/package differs')
        return source,m,expected
    def selection(self,source_pin,package_pin,name):
        require(name=='custody-participation','source adapter nickname is closed')
        _,manifest,expected=self.package(source_pin,package_pin)
        return {'name':name,'archive_binding':manifest['archive_binding'],'expected_replay_binding':manifest['expected_replay_binding'],
            'config_sha256':expected['config_sha256'],'baseline_snapshot_digest':expected['baseline_snapshot_digest'],
            'expected_head':expected['expected_head'],'engine_pins':expected['engine_pins'],
            'review_binding':binding(PRODUCER_ROOT/'packages/0001/review.json'),
            'candidate_selection_basis':{'manifest_sha256':package_pin,'source_manifest_sha256':source_pin,'adapter_source_sha256':self.adapter_pin},
            'authority_effect':'none','actual_owner_outcome':None}
    @contextmanager
    def open_signed(self,source_pin,package_pin):
        selected_row=self.selection(source_pin,package_pin,'custody-participation')
        with C.open_source(source_pin,package_pin) as cold:
            view=self.Inspection(cold.data,selected_row,cold.originals,cold.handle)
            selected=adapter.SignedSources(view,source_pin,selection_reader=lambda name:self.selection(source_pin,package_pin,name))
            view.custody_signed_sources=selected
            try:
                yield selected
                selected.guard();self.guard()
            finally:selected.close()
''')
files={r['path']:r for r in json.loads((I/'current-source-adapter-v4/source-manifest.json').read_bytes())['files']}
for p in [I/'current-source-adapter-v4/source-manifest.json',I/'current-participation-v5/source-manifest.json',I/'current-participation-v5/packages/0001/manifest.json',*A.glob('*.py')]:files[bind(p)['path']]=bind(p)
m={'schema_version':'lab-fresh-union-reader-source/v1-candidate','files':[files[k] for k in sorted(files)],'environment':json.loads((I/'current-participation-v5/source-manifest.json').read_bytes())['environment'],'original_source_binding':bind(I/'current-participation-v5/source-manifest.json'),'original_package_binding':bind(I/'current-participation-v5/packages/0001/manifest.json'),'original_adapter_binding':bind(I/'current-source-adapter-v4/source-manifest.json'),'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Fresh complete source guard union only; original signatures, eligibility and permission remain independently evaluated.'}
(A/'source-manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print(json.dumps({'adapter_pin':bind(A/'source-manifest.json'),'rows':len(files)}))
