"""Task-local immutable construction pins and real native build phases.

Source/reader/mapper phases do not open a live Context or Session. The Context
phase must be separately scheduled by the shared runtime-slot coordinator.
All signatures use fresh owned scratch keys through the original engine.
"""
from __future__ import annotations
import argparse
import ast
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
INTERFACE=HERE.parent
RUNTIME=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02'
API12=INTERFACE/'api-v25'
NATIVE=INTERFACE/'runtime-dependencies-v1-completion-0001/installations/0001/bin/lab-context-native-reader'
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(path):return json.loads(Path(path).read_bytes())
def binding(path):return {'path':Path(path).relative_to(ROOT).as_posix(),'sha256':sha(Path(path).read_bytes())}
def environment():return {'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
def require(ok,message):
    if not ok:raise ValueError(message)
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return __import__(name+'.build',fromlist=['*'])
def add(rows,row):
    path=Path(row['path']) if Path(row['path']).is_absolute() else ROOT/row['path']
    require(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe captured construction input')
    require(sha(path.read_bytes())==row['sha256'],'captured original input changed '+row['path'])
    require(rows.get(row['path'],row)==row,'conflicting construction input digest')
    rows[row['path']]=row
def capture(family,role,parents,extra=()):
    folder=family/role;require(not (folder/'source-manifest.json').exists(),'immutable role snapshot already selected')
    rows={}
    for path in parents:
        add(rows,binding(path))
        for row in parse(path)['files']:add(rows,row)
    for f in sorted(folder.rglob('*')):
        if f.is_file() and f.suffix in ('.py','.json'):
            if f.suffix=='.py':ast.parse(f.read_text())
            add(rows,binding(f))
    for row in extra:add(rows,row)
    # This is a construction snapshot, not a shared API freeze or qualification.
    value={'schema_version':'lab-current-fixture-'+role+'-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'environment':environment(),'construction_status':'construction-bound-unqualified','fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    return value
def snapshot(family,role,value):
    path=family/role/'source-manifest.json';write(path,value);return binding(path)['sha256']
def replace_unselected(path,mapping):
    require(not (path.parent/'source-manifest.json').exists(),'cannot change selected construction code')
    text=path.read_text()
    for old,new in mapping.items():
        require(old in text,'closed stage selector absent '+old)
        text=text.replace(old,new)
    ast.parse(text);path.write_text(text)
def source(family):
    source_root=family/'source'
    value=capture(family,'source',[INTERFACE/'legacy-session-fixture-source-v1-action-0148/source-manifest.json',INTERFACE/'current-participation-v5/source-manifest.json',INTERFACE/'current-participation-v5/packages/0001/manifest.json'],[binding(p) for p in sorted((family/'reader').glob('*.py'))]+[parse(family/'construction-selection.json')['generator_binding'],binding(Path(__file__).resolve())])
    value.update({'original_legacy_source_binding':binding(INTERFACE/'legacy-session-fixture-source-v1-action-0148/source-manifest.json'),'original_legacy_package_binding':binding(INTERFACE/'legacy-session-fixture-source-v1-action-0148/packages/0001/manifest.json'),'original_legacy_period_binding':binding(INTERFACE/'legacy-session-fixture-source-v1-action-0148/packages/0001/period.json'),'original5_period_binding':binding(INTERFACE/'current-participation-v5/packages/0001/period.json')})
    pin=snapshot(family,'source',value);B=package('_cal_T02_legacy_source_'+family.name.replace('-','_'),source_root);B.main(pin)
    return {'source_binding':binding(source_root/'source-manifest.json'),'package_binding':binding(source_root/'packages/0001/manifest.json'),'native_build_receipt':binding(source_root/'packages/0001/build-result.json')}
def cold(family):
    folder=family/'source';name='_cal_T02_current_source_cold_'+family.name.replace('-','_')
    package(name,folder);C=__import__(name+'.cold',fromlist=['*']);R=__import__(name+'.records',fromlist=['*']);B=__import__(name+'.base',fromlist=['*']);G=__import__(name+'.build',fromlist=['*'])
    pin=sha((folder/'source-manifest.json').read_bytes());pkg=sha((folder/'packages/0001/manifest.json').read_bytes());cuts=[];roots=[]
    for unused in range(2):
        with C.open_source(pin,pkg) as view:
            roots.append(view.root)
            require(datetime.fromisoformat(view.period['not_before'])<=datetime.now(timezone.utc)<datetime.fromisoformat(view.period['expires_at']),'actual new source period not current')
            require(datetime.fromisoformat(view.period['expires_at'])-datetime.fromisoformat(view.period['not_before'])==__import__('datetime').timedelta(hours=24),'new source duration differs')
            for identity in [R.PRINCIPAL,R.PROFILE,R.ASSIGNMENT,R.IMPLEMENTATION,R.WORK,R.CONTEXT]:
                require(view.data['projection']['subjects'][identity+'@'+R.VERSION]['effective_state']=='local-admitted-current','actual fresh source record not current')
            for row in B.load(folder/'packages/0001/record-index.json'):
                raw=B.original(row['original_binding'])
                actual=view.handle.custody.original_bytes(view.handle.store_module.Store(view.store,B.ROOT),row['version_ref'],view.data['head']['transaction_digest'])
                require(raw==actual and sha(raw)==row['original_byte_sha256'],'actual original transaction/source parity differs')
            cuts.append((view.data['head']['transaction_digest'],view.handle.common.digest(view.data['projection'])))
    require(cuts[0]==cuts[1] and all(not p.exists() for p in roots),'independent cold parity or cleanup differs')
    B.verify_source(pin)
    return {'result':'PASS-native-cold','independent_cold_replays':2,'original_byte_parity':True,'owned_cold_roots_removed':True,'source_binding':binding(folder/'source-manifest.json'),'package_binding':binding(folder/'packages/0001/manifest.json'),'period_binding':binding(folder/'packages/0001/period.json'),'private_signer_removed':B.load(folder/'packages/0001/build-result.json')['owned_store_and_key_removed'],'fixture_only':True,'actual_human_review':False,'authority_effect':'none','actual_owner_outcome':None,'public_API_qualified':False}
def reader(family):
    src=family/'source';dst=family/'reader';value=capture(family,'reader',[src/'source-manifest.json',src/'packages/0001/manifest.json'])
    value.update({'producer_source_binding':binding(src/'source-manifest.json'),'producer_package_binding':binding(src/'packages/0001/manifest.json'),'implementation_entrypoint_ref':dst.relative_to(ROOT).as_posix()+'/reader.py#SelectedReader.open_signed','original_Source8_permission_transferred':False})
    pin=snapshot(family,'reader',value)
    name='_cal_T02_current_reader_'+family.name.replace('-','_');spec=importlib.util.spec_from_file_location(name,dst/'__init__.py',submodule_search_locations=[str(dst)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);R=__import__(name+'.reader',fromlist=['*']);obj=R.SelectedReader(pin,sha((src/'source-manifest.json').read_bytes()),sha((src/'packages/0001/manifest.json').read_bytes()))
    with obj.open_signed(obj.source_pin,obj.package_pin) as selected:
        require(type(selected) is obj.adapter.SignedSources and type(selected.view) is obj.Inspection,'actual new reader classes differ')
        selected.guard();scope=selected.sources.scope_ref
    refused=[]
    for bad in [('0'*64,obj.source_pin,obj.package_pin),(pin,'0'*64,obj.package_pin),(pin,obj.source_pin,'0'*64)]:
        try:R.SelectedReader(*bad).package(bad[1],bad[2])
        except ValueError:refused.append(True)
        else:raise ValueError('wrong independent reader/source/package pin accepted')
    return {'result':'PASS-current-reader','reader_binding':binding(dst/'source-manifest.json'),'actual_distinct_local_types':True,'wrong_independent_pin_refusals':len(refused),'scope_ref':scope,'fixture_only':True,'public_API_qualified':False}
def mapped(family):
    src=family/'source';rd=family/'reader';dst=family/'mapped'
    replacements={'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2':sha((src/'source-manifest.json').read_bytes()),'8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964':sha((src/'packages/0001/manifest.json').read_bytes()),'0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5':sha((rd/'source-manifest.json').read_bytes())}
    for filename in ['base.py','build.py']:
        active={k:v for k,v in replacements.items() if k in (dst/filename).read_text()};replace_unselected(dst/filename,active)
    require(NATIVE.is_file() and NATIVE.stat().st_mode&0o777==0o755 and sha(NATIVE.read_bytes())==NATIVE_SHA,'original native executable selection differs')
    value=capture(family,'mapped',[src/'source-manifest.json',src/'packages/0001/manifest.json',rd/'source-manifest.json'])
    value.update({'original_source_binding':binding(src/'source-manifest.json'),'original_package_binding':binding(src/'packages/0001/manifest.json'),'adapter_source_binding':binding(rd/'source-manifest.json'),'native_executable_binding':{'path':NATIVE.relative_to(ROOT).as_posix(),'sha256':NATIVE_SHA,'required_mode':493},'complete_current_Lesson_inventory':0})
    additions=[binding(NATIVE)];value['files']=sorted(value['files']+additions,key=lambda r:r['path']);pin=snapshot(family,'mapped',value);B=package('_cal_T02_current_mapper_'+family.name.replace('-','_'),dst);B.build(pin)
    return {'result':'PASS-native-mapper','mapper_binding':binding(dst/'source-manifest.json'),'package_binding':binding(dst/'packages/0001/manifest.json'),'fixture_only':True,'public_API_qualified':False}
def context(family):
    src=family/'source';mp=family/'mapped';dst=family/'context'
    replacements={'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2':sha((src/'source-manifest.json').read_bytes()),'8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964':sha((src/'packages/0001/manifest.json').read_bytes()),'04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c':sha((mp/'source-manifest.json').read_bytes()),'ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94':sha((mp/'packages/0001/manifest.json').read_bytes())}
    for filename in ['base.py','build.py','generation.py']:
        active={k:v for k,v in replacements.items() if k in (dst/filename).read_text()};replace_unselected(dst/filename,active)
    implementation={'schema_version':'lab-original-reader-implementation-evidence/v1-candidate','entrypoint_ref':(family/'reader/reader.py').relative_to(ROOT).as_posix()+'#SelectedReader.open_signed','code_binding':{'ref':(family/'reader/reader.py').relative_to(ROOT).as_posix(),'sha256':sha((family/'reader/reader.py').read_bytes())},'environment_contract_ref':'protocol:R03-selected-R02-reader-environment','environment':environment(),'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Exact new controlled fixture source/producer binding only; no old renewal, human review, admission or shared qualification.'}
    write(dst/'implementation-binding.json',implementation)
    # The unchanged Schemas.guard owns its closed original execution dependency
    # selection. The whole API12 source remains original historical provenance;
    # its unrelated vanished native locator does not name this producer's mapper.
    api_profile=parse(API12/'contract-profile.json')
    execution_binding=binding(API12/'contract-profile.json');execution_path=API12/'contract-profile.json'
    inputs=parse(API12/'schema-inputs.json');execution={'files':list({r['path']:r for r in api_profile['files']+inputs['files']}.values())};original_manifest=parse(API12/'source-manifest.json')
    declared={r['path']:r for r in original_manifest['files']}
    require(all(declared.get(r['path'])==r for r in execution['files']),'schema execution input outside original whole source')
    selected_names={r['path'] for r in execution['files']}
    rows=[]
    predecessor='/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader'
    for row in original_manifest['files']:
        current=row['path'] in selected_names
        if current:add({},row)
        disposition={'original_binding':row,'required_current_schema_execution_input':current,'disposition':'original-current-schema-execution-input' if current else 'retained-original-whole-API12-historical-provenance-outside-Context-execution'}
        if row['path']==predecessor:
            require(not Path(predecessor).exists(),'predecessor path now exists; recapture disposition explicitly')
            require(row['sha256']==NATIVE_SHA and sha(NATIVE.read_bytes())==NATIVE_SHA,'independently reproduced original native bytes differ')
            disposition.update(original_locator_exists=False,original_locator_currentness_claimed=False,retained_original_byte_reproduction=binding(NATIVE),disposition='original-native-locator-unavailable; exact-byte-reproduction-independently-selected-for-new-mapper')
        rows.append(disposition)
    provenance={'schema_version':'lab-T02-Context-execution-dependency-disposition/v1-candidate','original_API12_whole_source_binding':binding(API12/'source-manifest.json'),'original_API12_whole_profile_binding':binding(API12/'contract-profile.json'),'original_schema_execution_selection_binding':execution_binding,'original_whole_source_row_count':len(rows),'required_current_schema_execution_row_count':len(selected_names),'causal_selection':'Actual unchanged API-v25 Schemas.guard reads all original30 profile files plus every original schema-input row; original protocol/guard/schema code remains unchanged. Current signed distinct legacy history and native mapper are separately fully captured and guarded.','full_original_history_validation_preserved':True,'original_Schemas_code_changed':False,'original_schema_execution_guard_changed':False,'rows':rows,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    write(dst/'execution-dependency-dispositions.json',provenance)
    value=capture(family,'context',[mp/'source-manifest.json',mp/'packages/0001/manifest.json',execution_path,API12/'schema-inputs.json'],[binding(API12/'source-manifest.json'),binding(API12/'contract-profile.json'),binding(Path(__file__).resolve()),binding(INTERFACE/'runtime-dependencies-v1-completion-0001/installations/0001/installation.json')])
    value.update({'external_dependency_bindings':[r for r in value['files'] if Path(r['path']).is_absolute()],'qualified_mapper_source_binding':binding(mp/'source-manifest.json'),'qualified_mapper_package_binding':binding(mp/'packages/0001/manifest.json'),'common_host_qualification':False,'actual_human_outcome':False})
    pin=snapshot(family,'context',value);B=package('_cal_T02_current_context_'+family.name.replace('-','_'),dst);B.build(pin,sha((mp/'packages/0001/manifest.json').read_bytes()))
    return {'result':'PASS-native-Context-construction','context_binding':binding(dst/'source-manifest.json'),'package_binding':binding(dst/'packages/0001/manifest.json'),'implementation_binding':binding(dst/'implementation-binding.json'),'fixture_only':True,'public_API_qualified':False}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--instance',required=True);parser.add_argument('--phase',choices=['source','cold','reader','mapped','context'],required=True);args=parser.parse_args()
    family=HERE/'instances'/args.instance;require(family.is_dir() and family.parent==HERE/'instances','selected instance outside owned scope')
    started=datetime.now(timezone.utc).isoformat();result=None;error=None
    try:result=globals()[args.phase](family)
    except BaseException as failure:
        import traceback
        error={'class':type(failure).__name__,'detail':str(failure),'traceback':traceback.format_exc()}
    report={'schema_version':'lab-T02-new-legacy-family-phase/v1-candidate','phase':args.phase,'instance':args.instance,'started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'result':'FAIL' if error else 'PASS','observation':result,'error':error,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    path=RUNTIME/(args.instance+'-'+args.phase+'.json');write(path,report)
    print(json.dumps({'result':report['result'],'phase':args.phase,'report_binding':binding(path)}),flush=True)
    if error:raise SystemExit(1)
if __name__=='__main__':main()
