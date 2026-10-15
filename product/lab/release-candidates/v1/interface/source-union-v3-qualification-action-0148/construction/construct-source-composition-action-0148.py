from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';A=I/'current-source-adapter-action-0148';M=I/'current-mapped-context-action-0148';C=I/'current-context-delivery-action-0148';API=I/'api-session-source-action-0148'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def load(p):return json.loads(p.read_bytes())
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def files_union(*groups):
 d={}
 for group in groups:
  for r in group:
   assert r['path'] not in d or d[r['path']]==r
   d[r['path']]=r
 return [d[k] for k in sorted(d)]
def ownfiles(p):return [bind(f) for f in sorted(p.rglob('*')) if f.is_file() and f.name not in ('source-manifest.json','contract-profile.json','EXECUTION-DEPENDENCIES.json','SCHEMA-EXECUTION-DEPENDENCIES.json')]
# Additional rows are a single-invocation closed selection from an independently
# pinned mapper/Context manifest. No cached verification result is accepted.
p=A/'boundary.py';s=p.read_text().replace('def boundary(adapter_pin,source_pin,package_pin):','def boundary(adapter_pin,source_pin,package_pin,*,additional_rows=()):').replace("*package_manifest['files'],*own['files']", "*package_manifest['files'],*own['files'],*additional_rows");p.write_text(s)
m=load(A/'source-manifest.json');m['files']=[bind(ROOT/r['path']) if r['path'].startswith(str(A.relative_to(ROOT))+'/') else r for r in m['files']];put(A/'source-manifest.json',m);APIN=sha(A/'source-manifest.json')
M.mkdir(mode=0o700)
(M/'__init__.py').write_text('"""Separately selected complete union mapper guard, exact original native package."""\n')
(M/'base.py').write_text('''"""New mapper selector; original native projection bytes remain exactly pinned."""
from pathlib import Path
import importlib.util,sys
SELECTOR_ROOT=Path(__file__).resolve().parent
HERE=SELECTOR_ROOT.parent/'current-mapped-context-v4'
ROOT=HERE.parents[5]
A=SELECTOR_ROOT.parent/'current-source-adapter-action-0148'
NAME='_cal_union_reader_mapper_action_0148'
if NAME not in sys.modules:
    s=importlib.util.spec_from_file_location(NAME,A/'__init__.py',submodule_search_locations=[str(A)])
    m=importlib.util.module_from_spec(s);sys.modules[NAME]=m;s.loader.exec_module(m)
R=__import__(NAME+'.reader',fromlist=['SelectedReader']);BOUNDARY=__import__(NAME+'.boundary',fromlist=['boundary'])
SOURCE_PIN=BOUNDARY.SOURCE_PIN;PACKAGE_PIN=BOUNDARY.PACKAGE_PIN
ADAPTER_PIN='ADAPTER_TOKEN'
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
'''.replace('ADAPTER_TOKEN',APIN))
(M/'build.py').write_text('''"""Original native executable/signature functions, separately selected fresh mapper guard."""
from .base import *
EXE=ORIGINAL.EXE;EXE_SHA=ORIGINAL.EXE_SHA;ONTOLOGY=ORIGINAL.ONTOLOGY
PROFILE=ORIGINAL.PROFILE;EDGE_PROFILE=ORIGINAL.EDGE_PROFILE
call=ORIGINAL.call;native_bytes=ORIGINAL.native_bytes;seal=ORIGINAL.seal
# Package lives in the frozen original directory. SELECTOR_ROOT selects code.
def guard(pin,*,additional_rows=()):
    verify_source(pin,additional_rows=additional_rows)
    require(EXE.is_file() and not EXE.is_symlink() and sha(EXE.read_bytes())==EXE_SHA,'original native executable differs')
''')
old=load(I/'current-mapped-context-v4/source-manifest.json')
m={'schema_version':'lab-union-mapper-source/v1-candidate','files':files_union(old['files'],load(A/'source-manifest.json')['files'],ownfiles(M),[bind(A/'source-manifest.json'),bind(I/'current-mapped-context-v4/source-manifest.json'),bind(I/'current-mapped-context-v4/packages/0001/manifest.json')]),'original_mapper_binding':bind(I/'current-mapped-context-v4/source-manifest.json'),'original_package_binding':bind(I/'current-mapped-context-v4/packages/0001/manifest.json'),'selected_adapter_binding':bind(A/'source-manifest.json'),'environment':old['environment'],'authority_effect':'none','actual_owner_outcome':None};put(M/'source-manifest.json',m);MPIN=sha(M/'source-manifest.json')
C.mkdir(mode=0o700)
for name in ['__init__.py','base.py','build.py','control.py','generation.py','lifetime-policy.json','implementation-binding.json']:
 shutil.copyfile(I/'current-context-delivery-v9'/name,C/name)
shutil.copytree(I/'current-context-delivery-v9/protocols',C/'protocols')
p=C/'base.py';s=p.read_text().replace("mapping_name='_cal_context_current_mapper_v4_delivery_v9'","mapping_name='_cal_context_union_mapper_action_0148'").replace("HERE.parent/'current-mapped-context-v4'","HERE.parent/'current-mapped-context-action-0148'").replace('38e24b3517ef1868c57fc21e58e300e578187303a888dd9b22ff20e086d3317b',MPIN)
s=s.replace('    for row in selected:dependency_input_bytes(row,selected_external)\n','')
s=s.replace('    MAPPED.guard(MAPPED_PIN)','    MAPPED.guard(MAPPED_PIN,additional_rows=[*selected,selection])')
s=s.replace("binding(MAPPED.HERE/'source-manifest.json')","binding(MAPPED.SELECTOR_ROOT/'source-manifest.json')")
p.write_text(s)
p=C/'generation.py';p.write_text(p.read_text().replace('38e24b3517ef1868c57fc21e58e300e578187303a888dd9b22ff20e086d3317b',MPIN))
m=load(C/'implementation-binding.json');m['entrypoint_ref']=str((A/'reader.py').relative_to(ROOT))+'#SelectedReader.open_signed';m['code_binding']={'ref':str((C/'build.py').relative_to(ROOT)),'sha256':sha(C/'build.py')};put(C/'implementation-binding.json',m)
old=load(I/'current-context-delivery-v9/source-manifest.json');e=load(I/'current-context-delivery-v9/EXECUTION-DEPENDENCIES.json')
# Preserve full historical qualification closure. Execution remaps only actual
# new Context code; original frozen parent source rows remain history inputs.
owned=ownfiles(C)+ownfiles(M)+ownfiles(A)+[bind(A/'source-manifest.json'),bind(M/'source-manifest.json')]
execution=files_union(e['files'],owned);e['files']=execution;e['external_dependency_bindings']=[r for r in execution if r['path'].startswith('/')]
for row in owned:e['selection_reasons'][row['path']]=['Actual explicitly selected source-union family code or parent binding; original eligibility, replay, schema and private permission semantics retained.']
e['parent_qualification_binding']=bind(I/'current-context-delivery-v9/source-manifest.json');put(C/'EXECUTION-DEPENDENCIES.json',e)
old['files']=files_union(old['files'],owned,[bind(C/'EXECUTION-DEPENDENCIES.json')]);old['external_dependency_bindings']=[r for r in old['files'] if r['path'].startswith('/')];old['execution_dependency_binding']=bind(C/'EXECUTION-DEPENDENCIES.json');old['qualified_mapper_source_binding']=bind(M/'source-manifest.json');old['qualified_mapper_package_binding']=bind(I/'current-mapped-context-v4/packages/0001/manifest.json');old['source_family_delta']='Separately selected fresh complete union; original signed source/package/period/keys/native projection unchanged.';put(C/'source-manifest.json',old);CPIN=sha(C/'source-manifest.json')
API.mkdir(mode=0o700)
for p in (I/'api-integration-v7').iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.md'):shutil.copyfile(p,API/p.name)
for name in ['schemas','session-inputs']:shutil.copytree(I/'api-integration-v7'/name,API/name)
for name in ['source_bridge.py','custody_context_sessions.py']:
 p=API/name;s=p.read_text().replace('85f81392b9ae2e4c34d96c0f6696b3b0a34397717f4b11706fa062eba8a20cb3',CPIN).replace("'_cal_api_v39_custody_context_v9'","'_cal_api_union_custody_action_0148'").replace("HERE.parent/'current-context-delivery-v9'","HERE.parent/'current-context-delivery-action-0148'");p.write_text(s)
# Existing witnesses retain original helper origins; additionally require actual
# separately selected SignedSources/reader class module paths, never pretend v4.
p=API/'custody_context_sessions.py';s=p.read_text();needle="        self.source=view.custody_signed_sources;";s=s.replace(needle,"        source.require(Path(sys.modules[D.reader.adapter.__name__].__file__).resolve()==HERE.parent/'current-source-adapter-action-0148/adapter.py' and type(view.custody_signed_sources) is D.reader.adapter.SignedSources,'independent source-union adapter class differs')\n"+needle);p.write_text(s)
# Rebind local schema byte rows and keep same operation mappings/input bytes.
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');prefix=str((I/'api-integration-v7').relative_to(ROOT))+'/'
e['files']=[bind(API/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row for row in e['files']]
e['files']=files_union(e['files'],[bind(API/'custody_context_sessions.py')]);e['selection_reasons']={r['path']:['Exact real schema/runtime input selected for new source family.'] for r in e['files']};put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=files_union(p['files'],ownfiles(API),[bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]);p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
m=load(API/'source-manifest.json');m['files']=files_union(m['files'],ownfiles(API),[bind(API/'contract-profile.json'),bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),bind(C/'source-manifest.json'),bind(C/'EXECUTION-DEPENDENCIES.json'),bind(M/'source-manifest.json'),bind(A/'source-manifest.json')],owned);put(API/'source-manifest.json',m)
print(json.dumps({'adapter':bind(A/'source-manifest.json'),'mapper':bind(M/'source-manifest.json'),'context':bind(C/'source-manifest.json'),'api':bind(API/'source-manifest.json'),'profile':bind(API/'contract-profile.json')}))
