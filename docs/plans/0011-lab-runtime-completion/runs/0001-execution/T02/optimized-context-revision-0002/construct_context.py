"""Distinct Context producer over immutable qualified Source/Reader/Mapper roots."""
from __future__ import annotations
import argparse,ast,hashlib,importlib.metadata,importlib.util,json,platform,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[6]
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
RUNTIME=HERE/'reports'
API12=INTERFACE/'api-integration-v12'
QUALIFIED=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0001/instances/optimized-0001'
SOURCE=QUALIFIED/'source';READER=QUALIFIED/'reader';MAPPED=QUALIFIED/'mapped'
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
    selection=parse(family/'construction-selection.json')
    for row in selection['optimized_input_bindings']:add(rows,row)
    for row in selection['optimized_recipe_bindings']:add(rows,row)
    for row in extra:add(rows,row)
    # This is a construction snapshot, not a shared API freeze or qualification.
    value={'schema_version':'lab-current-fixture-'+role+'-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'environment':environment(),'construction_status':'construction-bound-unqualified','fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    return value

def snapshot(family,role,value):
    path=family/role/'source-manifest.json';write(path,value);return binding(path)['sha256']

def context(family):
    src=SOURCE;mp=MAPPED;dst=family/'context'
    implementation={'schema_version':'lab-original-reader-implementation-evidence/v1-candidate','entrypoint_ref':(READER/'reader.py').relative_to(ROOT).as_posix()+'#CurrentFixtureReader.open_signed','code_binding':{'ref':(dst/'build.py').relative_to(ROOT).as_posix(),'sha256':sha((dst/'build.py').read_bytes())},'environment_contract_ref':'protocol:R03-selected-R02-reader-environment','environment':environment(),'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Exact new controlled fixture source/producer binding only; no old renewal, human review, admission or shared qualification.'}
    write(dst/'implementation-binding.json',implementation)
    # The unchanged Schemas.guard owns its closed original execution dependency
    # selection. The whole API12 source remains original historical provenance;
    # its unrelated vanished native locator does not name this producer's mapper.
    api_profile=parse(API12/'contract-profile.json')
    execution_binding=api_profile['schema_execution_dependency_binding']
    execution_path=ROOT/execution_binding['path']
    require(sha(execution_path.read_bytes())==execution_binding['sha256'],'original schema execution selection differs')
    execution=parse(execution_path);original_manifest=parse(API12/'source-manifest.json')
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
    provenance={'schema_version':'lab-T02-Context-execution-dependency-disposition/v1-candidate','original_API12_whole_source_binding':binding(API12/'source-manifest.json'),'original_API12_whole_profile_binding':binding(API12/'contract-profile.json'),'original_schema_execution_selection_binding':execution_binding,'original_whole_source_row_count':len(rows),'required_current_schema_execution_row_count':len(selected_names),'causal_selection':'Actual unchanged API12 Schemas.guard reads every original SCHEMA-EXECUTION-DEPENDENCIES row; unchanged protocol resources and guards remain in that closure. Current signed Source8-derived history and mapper are separately fully captured and guarded.','full_original_history_validation_preserved':True,'original_Schemas_code_changed':False,'original_schema_execution_guard_changed':False,'rows':rows,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False}
    write(dst/'execution-dependency-dispositions.json',provenance)
    value=capture(family,'context',[mp/'source-manifest.json',mp/'packages/0001/manifest.json',execution_path],[binding(API12/'source-manifest.json'),binding(API12/'contract-profile.json'),binding(Path(__file__).resolve()),binding(INTERFACE/'runtime-dependencies-v1-completion-0001/installations/0001/installation.json')])
    value.update({'external_dependency_bindings':[r for r in value['files'] if Path(r['path']).is_absolute()],'qualified_mapper_source_binding':binding(mp/'source-manifest.json'),'qualified_mapper_package_binding':binding(mp/'packages/0001/manifest.json'),'common_host_qualification':False,'actual_human_outcome':False})
    pin=snapshot(family,'context',value);B=package('_cal_T02_current_context_'+family.name.replace('-','_'),dst);B.build(pin,sha((mp/'packages/0001/manifest.json').read_bytes()))
    return {'result':'PASS-native-Context-construction','context_binding':binding(dst/'source-manifest.json'),'package_binding':binding(dst/'packages/0001/manifest.json'),'implementation_binding':binding(dst/'implementation-binding.json'),'fixture_only':True,'public_API_qualified':False}
def selected_recipe(expected):
    selected=HERE/'recipe-selection.json'
    require(sha(selected.read_bytes())==expected,'independently selected successor recipe differs')
    value=parse(selected)
    require(value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'technical recipe required')
    for row in value['files']:add({},row)
    for row in value['qualified_reused_role_bindings']:add({},row)
    return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--recipe-sha256',required=True);args=parser.parse_args()
    selected_recipe(args.recipe_sha256);started=datetime.now(timezone.utc).isoformat();result=None;error=None
    try:result=context(HERE)
    except BaseException as failure:
        import traceback
        error={'class':type(failure).__name__,'frames':[{'file':frame.filename,'line':frame.lineno,'function':frame.name} for frame in traceback.extract_tb(failure.__traceback__)]}
    selected_recipe(args.recipe_sha256)
    report={'schema_version':'lab-T02-context-successor-phase/v1-candidate','phase':'context','instance':'optimized-context-0002','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'result':'FAIL' if error else 'PASS','observation':result,'error':error,'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False,'old_source_derived_signed_history_reader_mapper_and_period_unchanged':True,'old_failed_Context_grant_not_reused':True}
    path=RUNTIME/'context-phase.json';write(path,report);print(json.dumps({'result':report['result'],'report_binding':binding(path)}),flush=True)
    if error:raise SystemExit(1)
if __name__=='__main__':main()
