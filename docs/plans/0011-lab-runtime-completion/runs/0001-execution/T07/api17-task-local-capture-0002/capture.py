"""Capture focused API17 pins with every present parent row and full accounting.

This is an owned technical capture, not T15 or a historical/full release verdict.
Frozen parent manifests, absent locators and all original callbacks stay intact.
"""
import ast
import argparse
import os
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
API=INTERFACE/'api-integration-v17'
PARENT=INTERFACE/'api-integration-v16'
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
ACCOUNTING=INTERFACE/'runtime-input-accounting-v1-completion-0001'
SOURCE_SHA='8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
PROFILE_SHA='8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
ACCOUNTING_SHA='54fad4029d47435faaa3a6dad215f6d268b6589c1be982d9e764f27ef2880729'
SELECTION_PIN=None
UNAVAILABLE=RUN/'T07/accounting-0001/unavailable-original-inputs.json'
UNAVAILABLE_SHA='4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'
DEPENDENCIES=RUN/'T07/revision-0002/dependency-selection-0002.json'
DEPENDENCIES_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path,expected=None):
    raw=path.read_bytes()
    assert expected is None or sha(raw)==expected,str(path)
    return json.loads(raw)
def logical(path):
    path=Path(path)
    if not path.is_absolute():return path.as_posix()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
def bind(path):
    path=Path(path);path=path if path.is_absolute() else ROOT/path
    assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),str(path)
    return {'path':logical(path),'sha256':sha(path.read_bytes())}
def write_new(path,value):
    raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    if path.parent==API:
        # Only Root writes these unfrozen task-local selections. Every old byte
        # is preserved and independently checked before any new capture writes.
        temporary=path.with_name(path.name+'.capture-0002-new')
        with temporary.open('xb') as handle:
            handle.write(raw);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,path)
    else:
        with path.open('xb') as handle:handle.write(raw)
    return bind(path)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--selection-sha256',required=True)
    args=parser.parse_args()
    selection=load(HERE/'component-selection.json',args.selection_sha256)
    assert selection['authority_effect']=='none' and selection['task_complete'] is False
    assert selection['guard_binding']==bind(API/'guard.py')
    assert selection['guard_binding']['sha256']=='65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'
    for name in ['source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json']:
        assert (API/name).read_bytes()==(HERE/'preimage'/name).read_bytes(),'prior selection changed'
    original=load(PARENT/'source-manifest.json',SOURCE_SHA)
    old_profile=load(PARENT/'contract-profile.json',PROFILE_SHA)
    assert len(original['files'])==24497 and len(old_profile['files'])==24496
    absent=load(UNAVAILABLE,UNAVAILABLE_SHA)
    unavailable={entry['binding']['path']:entry['binding'] for entry in absent['rows']}
    assert len(unavailable)==25
    parent_by_path={row['path']:row for row in original['files']}
    retained=[row for row in original['files'] if row['path'] not in unavailable]
    additions={};classes={};reasons={}
    def add(binding,classification,reason):
        binding={'path':logical(binding['path']),'sha256':binding['sha256']}
        if binding['path'] in parent_by_path:
            assert parent_by_path[binding['path']]==binding,'changed original input '+binding['path']
            assert binding['path'] not in unavailable,'required missing original byte '+binding['path']
            return
        assert additions.get(binding['path'],binding)==binding,'conflicting successor input '+binding['path']
        assert bind(binding['path'])==binding,'uncaptured declared bytes '+binding['path']
        additions[binding['path']]=binding
        classes.setdefault(binding['path'],classification)
        reasons.setdefault(binding['path'],reason)
    def add_file(path,classification,reason):add(bind(path),classification,reason)
    add_file(PARENT/'source-manifest.json','successor-code','Exact complete historical parent source metadata, not physical closure.')
    add_file(Path(__file__),'successor-code','Exact owned capture algorithm and independently selected inputs.')
    for path in sorted(API.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or 'receipts' in path.parts:continue
        if path.name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'):continue
        if path.suffix=='.py':ast.parse(path.read_bytes())
        add_file(path,'successor-code','Explicit API17 package file; original test/helper bodies retained.')
    helper=load(ACCOUNTING/'source-manifest.json',ACCOUNTING_SHA)
    for row in helper['files']:add(row,'successor-code','Frozen complete historical accounting verifier input; no body/provenance PASS transfer.')
    add_file(ACCOUNTING/'source-manifest.json','successor-code','Independent frozen accounting component pin.')
    for folder in ['machine-context-scope-v2-completion-0001','lesson-host-composition-v46-completion-0001','lesson-application-v4-completion-0001']:
        for path in sorted((INTERFACE/folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                add_file(path,'successor-code','Explicit selected current runtime composition helper.')
    fixtures=INTERFACE/'current-session-fixtures-v1-completion-0001/instances'
    for family in ['legacy-diagnostic-0001','diagnostic-0004']:
        for role in ['source','reader','mapped','context']:
            path=fixtures/family/role/'source-manifest.json'
            manifest=load(path)
            for row in manifest['files']:add(row,'successor-family','Complete independently constructed current '+family+' '+role+' input.')
            add_file(path,'successor-family','Full current-family source manifest; original signed history/schema callbacks stay unchanged.')
        add_file(fixtures/family/'runtime/runtime-selection.json','successor-family','Independent exact current runtime/period/Principal selection.')
    dependencies=load(DEPENDENCIES,DEPENDENCIES_SHA)
    for row in dependencies['inputs']:add(row,'host-dependency','Entire independently pinned current host/stdlib/native/ABI/wheel input selection.')
    add_file(DEPENDENCIES,'host-dependency','Independently qualified complete current host dependency inventory.')
    for version,generation in [('runtime-dependencies-v1-completion-0001','0001'),('runtime-dependencies-v2-completion-0001','0004')]:
        installation=INTERFACE/version/'installations'/generation
        receipt=load(installation/'installation.json')
        for name,value in receipt['installed_files'].items():
            add({'path':str(installation/name),'sha256':value['sha256']},'host-dependency','Full retained owned dependency installation; no host origin alias.')
        add_file(installation/'installation.json','host-dependency','Exact retained installation receipt and complete installed-file pins.')
    add_file(HERE/'component-selection.json','successor-code','Independent exact selected component input document; external expected digest checked by Root capture invocation.')
    for component in selection['component_manifests']:
        selected_component=load(ROOT/component['path'],component['sha256'])
        base=ROOT/component['base']
        for row in selected_component['files']:
            path=Path(row['path'])
            path=path if path.is_absolute() else base/path
            add({'path':str(path),'sha256':row['sha256']},'successor-code','Complete separately frozen current operator/provisioner/fixture software input; no authority or final PASS inherited.')
        add(component_binding:={'path':component['path'],'sha256':component['sha256']},'successor-code','Exact separately reviewed candidate component manifest.')
    for row in selection['direct_inputs']:
        add(row,'successor-code','Explicit separately reviewed current diagnostic/caller/fixture origin eligible for guarded imports.')
    for row in load(HERE.parent/'api17-task-local-capture-0001/capture-revision-0002/source-manifest.json','718111b4c225f443776b4e463efb1ea83efef5e3903f0c50b758e3811beae97f')['files']:
        add(row,'successor-code','Full reviewed no-follow metadata capture proposal and14 owned physical replacement checks; full original byte guard unchanged.')
    static={row['path']:row for row in retained};static.update(additions)
    schema=copy.deepcopy(load(PARENT/'SCHEMA-EXECUTION-DEPENDENCIES.json'))
    selected={row['path']:row for row in schema['files']}
    assert not set(selected)&set(unavailable),'original schema selection consumes missing historical byte'
    for path,row in static.items():
        if path.startswith(logical(API)+'/') or (path in additions and path.endswith('.py')):
            selected[path]=row
    schema['files']=[selected[path] for path in sorted(selected)]
    schema['selection_reasons']={path:schema['selection_reasons'].get(path,['Exact new API17 protocol/auth/handler/schema helper input.']) for path in sorted(selected)}
    schema['parent_source_binding']={'path':logical(PARENT/'source-manifest.json'),'sha256':SOURCE_SHA}
    schema['parent_profile_binding']={'path':logical(PARENT/'contract-profile.json'),'sha256':PROFILE_SHA}
    schema['claim_ceiling']='Focused current API17 schema execution selection. Full original provenance retained separately; no final/historical qualification.'
    schema_binding=write_new(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',schema)
    add(schema_binding,'successor-code','Exact independently captured complete current schema execution inventory.')
    profile=copy.deepcopy(old_profile)
    profile['files']=retained+[additions[path] for path in sorted(additions)]
    profile['schema_execution_dependency_binding']=schema_binding
    profile['historical_parent_source_binding']={'path':logical(PARENT/'source-manifest.json'),'sha256':SOURCE_SHA}
    profile['historical_parent_profile_binding']={'path':logical(PARENT/'contract-profile.json'),'sha256':PROFILE_SHA}
    profile['historical_original_physical_closure']='REFUSED'
    profile['claim_ceiling']='34 authored current candidate operations; focused current Session integration only. All original literal provenance tables and physical historical refusals retained. No T15/final qualification, owner outcome, pilot or admission.'
    native=INTERFACE/'runtime-dependencies-v1-completion-0001/installations/0001/bin/lab-context-native-reader'
    profile['external_execution_dependency_bindings']=[bind(native)]
    profile['Machine_context_scope_method_binding']=bind(INTERFACE/'machine-context-scope-v2-completion-0001/generation.py')
    profile_binding=write_new(API/'contract-profile.json',profile)
    add(profile_binding,'successor-code','Exact new independently captured current protocol profile; parent profile remains immutable.')
    current=retained+[additions[path] for path in sorted(additions)]
    inventory={'schema_version':'lab-runtime-input-accounting/v1-candidate','source_sha256':SOURCE_SHA,'profile_sha256':PROFILE_SHA,'unavailable_sha256':UNAVAILABLE_SHA,
        'additions':[{'binding':additions[path],'classification':classes[path],'selection_reason':reasons[path]}for path in sorted(additions)],
        'consumption':[{'binding':row,'status':'historical-metadata-only' if row['path'] in unavailable else 'required-current-byte',
            'basis':'Exact absent original locator retained as unavailable provenance; selected current-family callbacks use complete independently pinned current inputs.' if row['path'] in unavailable else 'Full fresh current byte guard retains every present parent row and every explicitly selected successor/host input.'}
            for row in original['files']+[additions[path]for path in sorted(additions)]],
        'authority_effect':'none','claim_ceiling':'Full original row/order accounting and explicit focused current execution selection; original physical closure remains REFUSED.'}
    # The source manifest independently binds inventory bytes. Inventory cannot
    # include its own hash without a cycle; the host checks that binding fresh.
    inventory_binding=write_new(API/'INPUT-ACCOUNTING.json',inventory)
    manifest={'schema_version':'lab-runtime-execution-source/v2-candidate','files':current,'environment':original['environment'],
        'input_accounting':{'component_binding':bind(ACCOUNTING/'source-manifest.json'),'module_binding':bind(ACCOUNTING/'accounting.py'),
            'source_binding':{'path':logical(PARENT/'source-manifest.json'),'sha256':SOURCE_SHA},
            'profile_binding':{'path':logical(PARENT/'contract-profile.json'),'sha256':PROFILE_SHA},
            'unavailable_binding':bind(UNAVAILABLE),'selection_binding':inventory_binding},
        'profile_binding':profile_binding,'parent_source_binding':{'path':logical(PARENT/'source-manifest.json'),'sha256':SOURCE_SHA},
        'historical_original_physical_closure':'REFUSED','historical_missing_locators':25,'original_present_rows_retained':len(retained),
        'full_original_source_rows':24497,'full_original_profile_rows':24496,'original_signed_history_schema_callbacks_changed':False,
        'whole_API_qualified':False,'current_Agent_qualified':False,'task_complete':False,'goal_complete':False,'actual_owner_outcome':None,'authority_effect':'none',
        'claim_ceiling':'Focused current API17 runtime selection only. Final entire plan/historical physical proof/publication/current owner/human pilot qualification remains unproven.'}
    source_binding=write_new(API/'source-manifest.json',manifest)
    result={'source_binding':source_binding,'profile_binding':profile_binding,'inventory_binding':inventory_binding,
        'current_guard_rows':len(current),'retained_present_parent_rows':len(retained),'added_execution_rows':len(additions),
        'schema_execution_rows':len(schema['files']),'historical_physical_closure':'REFUSED','runtime_qualified':False,'authority_effect':'none'}
    write_new(HERE/'capture-result.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
