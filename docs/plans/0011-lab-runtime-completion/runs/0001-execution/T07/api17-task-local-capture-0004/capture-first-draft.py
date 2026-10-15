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
import re
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
LINEAGE_SHA='c13bc99371a65b0f0a39aa1418c0eb4c476b05fc94610128840500c9d0d442f1'
GENERATED={'source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'}
FAMILY_BASE=RUN/'T02/optimized-family-preparation-0004/instances/optimized-0004'
ROLE_TARGETS={'source_binding':'source/source-manifest.json','source_package_binding':'source/packages/0001/manifest.json','reader_binding':'reader/source-manifest.json','mapper_binding':'mapped/source-manifest.json','mapper_package_binding':'mapped/packages/0001/manifest.json','context_source_binding':'context/source-manifest.json','context_package_binding':'context/packages/0001/manifest.json','implementation_binding':'context/implementation-binding.json','period_binding':'source/packages/0001/period.json'}
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

def closed_family_binding(row):
    assert type(row) is dict and set(row)=={'path','sha256'},'open family binding'
    assert type(row['path']) is str and type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}',row['sha256']),'invalid family binding'
    path=Path(row['path'])
    assert row['path'] and not path.is_absolute() and path.as_posix()==row['path'] and '..' not in path.parts and '\\' not in row['path'] and '\0' not in row['path'] and row['path']!='.','aliased family origin'
    return row

def family_roles(runtime,descriptor_path):
    common={'schema_version','instance','authority_effect','actual_owner_outcome','shared_API_qualified'}
    legacy=common|{'actual_whole_classes_executed','bindings','independently_declared_fixture_expectations','original5_period_chain_preserved','previous_distinct_legacy_period_binding','root_required_changes','source5_or_oldlegacy_renewed'}
    current=common|{'actual_human_review','context_entrypoint_ref','context_package_binding','context_source_binding','fixture_only','implementation_binding','mapper_binding','mapper_package_binding','original_templates','period_binding','public_source_name','reader_binding','reader_class','reader_root','root_required_api_changes','runtime_postimages','source_binding','source_package_binding'}
    assert type(runtime) is dict and runtime['authority_effect']=='none' and runtime['actual_owner_outcome'] is None and runtime['shared_API_qualified'] is False
    name=runtime['instance'];assert type(name) is str and re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',name),'invalid family name'
    family_root=Path(descriptor_path).parents[1]
    if runtime['schema_version']=='lab-T02-fresh-legacy-runtime-integration-selection/v1-candidate':
        assert set(runtime)==legacy,'open legacy descriptor'
        bindings=runtime['bindings'];assert type(bindings) is dict and set(bindings)=={'source','source_package','reader','mapper','mapper_package','context','context_package','implementation','period'},'open legacy role bindings'
        assert runtime['source5_or_oldlegacy_renewed'] is False and runtime['original5_period_chain_preserved'] is True
        for row in bindings.values():closed_family_binding(row)
        roles={'source':bindings['source'],'reader':bindings['reader'],'mapped':bindings['mapper'],'context':bindings['context']}
    else:
        assert runtime['schema_version']=='lab-current-session-runtime-selection/v1-candidate'
        assert set(runtime) in (current,current|{'optimized_capture_selection_binding','original_frozen_family_unchanged'}),'open Source8 descriptor'
        assert runtime['fixture_only'] is True and runtime['actual_human_review'] is False and runtime['public_source_name']=='completion-current-participation:'+name
        assert runtime['reader_class']=='CurrentFixtureReader' and runtime['reader_root']==str(family_root/'reader') and runtime['context_entrypoint_ref']==str(family_root/'context/build.py')+'#generate','family origin mismatch'
        for key in ['source_binding','source_package_binding','reader_binding','mapper_binding','mapper_package_binding','context_source_binding','context_package_binding','implementation_binding','period_binding']:
            closed_family_binding(runtime[key])
        for key in ['runtime_postimages','original_templates']:
            assert type(runtime[key]) is list and runtime[key]
            for row in runtime[key]:closed_family_binding(row)
        if 'optimized_capture_selection_binding' in runtime:
            closed_family_binding(runtime['optimized_capture_selection_binding']);assert runtime['original_frozen_family_unchanged'] is True
        roles={'source':runtime['source_binding'],'reader':runtime['reader_binding'],'mapped':runtime['mapper_binding'],'context':runtime['context_source_binding']}
    for role,row in roles.items():
        assert row['path']==str(family_root/role/'source-manifest.json'),'role outside exact family origin'
    return roles

def need(value,message):
    if not value:raise ValueError(message)
def selected(row):
    # General input tables retain canonical original absolute host origins.
    need(type(row) is dict and set(row)=={'path','sha256'},'open input binding')
    need(type(row['path']) is str and type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}',row['sha256']) is not None,'invalid input binding')
    path=Path(row['path'])
    need(row['path'] and path.as_posix()==row['path'] and '..' not in path.parts and '\\' not in row['path'] and '\0' not in row['path'] and row['path']!='.' and logical(path)==row['path'],'aliased input origin')
    need(bind(path)==row,'independently selected input differs: '+row['path'])
    return row
def repo_binding(row):
    closed_family_binding(row);return selected(row)
def read_selected(row):
    selected(row);return load(ROOT/row['path'],row['sha256'])
def unique_rows(rows):
    need(type(rows) is list,'input rows must be a list')
    result={}
    for row in rows:
        need(type(row) is dict and set(row)=={'path','sha256'},'open input row')
        need(row['path'] not in result,'duplicate input origin')
        result[row['path']]=row
    return result
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def derived(name,value):return {'path':logical(API/name),'sha256':sha(encoded(value))}
def publish(outputs,lineage,result):
    # Preflight all destinations before writing anything. Only Root may invoke
    # this under its exclusive shared writer slot. Source is published last.
    need(set(outputs)==GENERATED,'unexpected shared output')
    need(not (HERE/'capture-result.json').exists(),'owned result already exists')
    for name in outputs:
        selected(lineage['predecessor_metadata'][name]['original_binding'])
        need(not (API/(name+'.capture-0004-new')).exists(),'temporary output already exists')
    staged={}
    try:
        for name,value in outputs.items():
            path=API/(name+'.capture-0004-new')
            with path.open('xb') as handle:
                st=os.fstat(handle.fileno());staged[path]=(st.st_dev,st.st_ino)
                handle.write(encoded(value));handle.flush();os.fsync(handle.fileno())
        for name in ['SCHEMA-EXECUTION-DEPENDENCIES.json','contract-profile.json','INPUT-ACCOUNTING.json','source-manifest.json']:
            selected(lineage['predecessor_metadata'][name]['original_binding'])
            temporary=API/(name+'.capture-0004-new')
            st=temporary.stat(follow_symlinks=False)
            need((st.st_dev,st.st_ino)==staged[temporary],'owned temporary replaced')
            os.replace(temporary,API/name)
        with (HERE/'capture-result.json').open('xb') as handle:handle.write(encoded(result))
    finally:
        for path,identity in staged.items():
            try:st=path.stat(follow_symlinks=False)
            except FileNotFoundError:continue
            if (st.st_dev,st.st_ino)==identity:path.unlink()
def activate(selection):
    keys={'schema_version','status','authority_effect','task_complete','lineage_binding','writer_binding','known_overlay_receipt_binding','known_margin_receipt_binding','known_api_expected_files','inputs','final_root_packet_binding','final_peer_review_binding'}
    need(type(selection) is dict and set(selection)==keys,'open capture selection')
    need(selection['schema_version']=='lab-T07-capture4-selection/v1-candidate' and selection['authority_effect']=='none' and selection['task_complete'] is False,'invalid capture boundary')
    need(selection['status']=='closed-for-Root-capture' and all(selection[key] is not None for key in ['inputs','final_root_packet_binding','final_peer_review_binding']),'capture4 draft refuses activation until final Root and peer inputs exist')
    need(selection['lineage_binding']=={'path':logical(HERE/'lineage.json'),'sha256':LINEAGE_SHA},'lineage selector differs')
    repo_binding(selection['writer_binding']);need(selection['writer_binding']['path']==logical(HERE/'capture.py'),'writer origin differs')
    known_overlay={'path':logical(RUN/'T02/composite-merge-preparation-0004/application-receipt.json'),'sha256':'3076ebbddd92c3a9f582adbb1dc5cb72b47e0a4b62ae75a1e204f259b229c705'}
    known_margin={'path':logical(RUN/'T00/margin-merge-receipt-0004.json'),'sha256':'6515a338a2fb279c3100d930ea231ae2d16a91fea180a3e7d66d367d97400e06'}
    need(selection['known_overlay_receipt_binding']==known_overlay and selection['known_margin_receipt_binding']==known_margin,'reviewed overlay selector differs')
    overlay=read_selected(known_overlay);read_selected(known_margin)
    need(overlay['actual_changed_targets']==8 and overlay['actual_new_files']==5 and overlay['authority_effect']=='none','overlay receipt differs')
    inputs=selection['inputs']
    need(type(inputs) is dict and set(inputs)=={'api_expected_files','helper_roots','helper_expected_files','component_manifests','direct_inputs','replacement_bindings','active_family','public_software_manifest_binding','guard_binding','profile_updates'},'open final inputs')
    for key in ['final_root_packet_binding','final_peer_review_binding']:
        row=selection[key];closed_family_binding(row)
        need(row['path'].startswith(logical(RUN/'T00')+'/'),'final Root/peer packet must have new T00 origin')
    packet=read_selected(selection['final_root_packet_binding'])
    need(type(packet) is dict and set(packet)=={'schema_version','status','authority_effect','lineage_binding','writer_binding','known_overlay_receipt_binding','known_margin_receipt_binding','inputs','merged_receipt_bindings'},'open Root packet')
    need(packet['schema_version']=='lab-T00-final-capture4-inputs/v1-candidate' and packet['status']=='Root-reviewed-merged-native-family4-ready-for-capture' and packet['authority_effect']=='none','final Root input readiness missing')
    for key in ['lineage_binding','writer_binding','known_overlay_receipt_binding','known_margin_receipt_binding','inputs']:need(packet[key]==selection[key],'Root input declaration differs: '+key)
    need(type(packet['merged_receipt_bindings']) is list and packet['merged_receipt_bindings'],'actual final merged receipts required')
    for row in packet['merged_receipt_bindings']:repo_binding(row)
    peer=read_selected(selection['final_peer_review_binding'])
    need(type(peer) is dict and set(peer)=={'schema_version','result','authority_effect','reviewed_root_packet_binding','review_binding','limitations'},'open final independent peer wrapper')
    need(peer['schema_version']=='lab-T00-capture4-inputs-peer/v1-candidate' and peer['result']=='PASS' and peer['authority_effect']=='none' and peer['reviewed_root_packet_binding']==selection['final_root_packet_binding'],'final independent reviewed inputs missing')
    repo_binding(peer['review_binding']);need(type(peer['limitations']) is list,'peer limitations missing')
    known=unique_rows(selection['known_api_expected_files']);final=unique_rows(inputs['api_expected_files'])
    predecessor=load(HERE/'lineage-preimages'/load(HERE/'lineage.json',LINEAGE_SHA)['capture3_selection_binding']['path'],'b182a70bf823e1e54cef016496e9acf7f573d32264653c0194c61e1bfe2fe661')
    expected=unique_rows(predecessor['api_expected_files']);expected.update(unique_rows(overlay['actual_target_bindings']))
    need(known==expected and len(known)==165 and set(known)<=set(final),'known165 API expectations changed or pruned')
    need(inputs['guard_binding']=={'path':logical(API/'guard.py'),'sha256':'65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'},'original complete guard differs')
    repo_binding(inputs['guard_binding'])
    need(type(inputs['profile_updates']) is list,'profile updates must be selected explicitly')
    return inputs,packet,peer

def new_family(value,add):
    need(type(value) is dict and set(value)=={'descriptor_binding','descriptor_keys','family_bindings','phase_report_bindings','actual_family_selection_binding'},'open actual family input')
    descriptor=value['descriptor_binding'];closed_family_binding(descriptor)
    need(descriptor['path']==logical(FAMILY_BASE/'runtime/runtime-selection.json'),'fresh optimized0004 descriptor origin required')
    runtime=read_selected(descriptor)
    need(type(value['descriptor_keys']) is list and value['descriptor_keys']==sorted(set(value['descriptor_keys'])) and set(runtime)==set(value['descriptor_keys']),'closed exact new descriptor shape required')
    need(runtime['schema_version']=='lab-current-session-runtime-selection/v1-candidate' and runtime['instance']=='optimized-0004' and runtime['public_source_name']=='completion-current-participation:optimized-0004','fresh actual Source4 family identity differs')
    need(runtime['fixture_only'] is True and runtime['actual_human_review'] is False and runtime['actual_owner_outcome'] is None and runtime['authority_effect']=='none' and runtime['shared_API_qualified'] is False,'family claim boundary differs')
    need(runtime['reader_root']==logical(FAMILY_BASE/'reader') and runtime['reader_class']=='CurrentFixtureReader' and runtime['context_entrypoint_ref']==logical(FAMILY_BASE/'context/build.py')+'#generate','new family executable origins differ')
    bindings=value['family_bindings'];need(type(bindings) is dict and set(bindings)==set(ROLE_TARGETS),'all nine new native role/package/period bindings required')
    for key,leaf in ROLE_TARGETS.items():
        row=bindings[key];need(row['path']==logical(FAMILY_BASE/leaf) and runtime[key]==row,'selected new family role differs: '+key);repo_binding(row)
        add(row,'successor-family','Exact new independently selected optimized0004 role/package/period origin; original native history remains.')
    actual=value['actual_family_selection_binding'];need(runtime['actual_family_selection_binding']==actual,'actual family input selector differs')
    family=read_selected(actual)
    need(set(family)=={'schema_version','status','instance','authority_effect','construction_binding','phase_reports','family_bindings'} and family['schema_version']=='lab-T02-v4-actual-family-inputs/v1-candidate' and family['status']=='Root-reviewed-actual-native-family' and family['instance']=='optimized-0004' and family['authority_effect']=='none' and family['family_bindings']==bindings,'actual complete native family prerequisite missing')
    need(family['construction_binding']['path']==logical(FAMILY_BASE/'construction-selection.json'),'true construction origin required')
    construction=read_selected(family['construction_binding']);need(construction['instance']=='optimized-0004' and construction['prefix']=='completion-optimized-source8-0004-optimized-0004','actual construction identity differs')
    need(family['phase_reports']==value['phase_report_bindings'] and type(family['phase_reports']) is list and len(family['phase_reports'])==5,'all five phase report pins required')
    phases=[]
    for row in family['phase_reports']:
        need(row['path'].startswith(logical(RUN/'T02/optimized-family-preparation-0004/reports')+'/'),'actual phase report origin differs')
        report=read_selected(row);need(report['instance']=='optimized-0004' and report['result']=='PASS' and report['error'] is None,'actual native phase failed');phases.append(report['phase'])
        add(row,'successor-family','Actual separately selected native phase evidence; no Session or margin qualification transfer.')
    need(phases==['source','cold','reader','mapped','context'],'actual native phase order differs')
    for key in ['source_binding','reader_binding','mapper_binding','context_source_binding']:
        manifest=read_selected(bindings[key]);need(manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,'native role claim boundary differs')
        for row in manifest['files']:add(row,'successor-family','Complete fresh optimized0004 '+key+' selected native role input.')
    for row in [descriptor,actual,family['construction_binding']]:add(row,'successor-family','Complete fresh family descriptor/construction provenance at its true origin.')
    for key in ['previous_runtime_selection_binding','optimized_capture_selection_binding']:
        add(runtime[key],'successor-family','Explicit preserved predecessor or selected capture recipe; no current origin alias.')
    for key in ['runtime_postimages','original_templates']:
        for row in runtime[key]:add(row,'successor-family','Exact new reviewed runtime postimage or retained original template.')

def main():
    if not __debug__:raise RuntimeError('capture assertions require an unoptimized interpreter')
    parser=argparse.ArgumentParser();parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True)
    args=parser.parse_args();selection_path=Path(args.selection)
    need(selection_path.parent.resolve()==HERE and selection_path.name!='capture-result.json','selection must be a new owned exact origin')
    selection_row={'path':logical(selection_path.resolve()),'sha256':args.selection_sha256}
    selection=read_selected(selection_row);inputs,packet,peer=activate(selection)
    lineage=load(HERE/'lineage.json',LINEAGE_SHA)
    need(lineage['current_guard_binding']==inputs['guard_binding'] and lineage['historical_physical_closure']=='REFUSED','lineage boundary differs')
    for item in lineage['capture3_artifacts']:
        selected(item['original_binding']);selected(item['retained_binding']);need(item['original_binding']['sha256']==item['retained_binding']['sha256'],'capture3 retained bytes differ')
    for value in lineage['predecessor_metadata'].values():
        selected(value['original_binding']);selected(value['snapshot_binding']);need(value['original_binding']['sha256']==value['snapshot_binding']['sha256'],'predecessor metadata differs')
    original=load(PARENT/'source-manifest.json',SOURCE_SHA);old_profile=load(PARENT/'contract-profile.json',PROFILE_SHA)
    need(len(original['files'])==24497 and len(old_profile['files'])==24496,'original full source/profile tables differ')
    absent=load(UNAVAILABLE,UNAVAILABLE_SHA);unavailable={entry['binding']['path']:entry['binding'] for entry in absent['rows']};need(len(unavailable)==25,'original missing dispositions differ')
    parent_by_path=unique_rows(original['files']);retained=[row for row in original['files'] if row['path'] not in unavailable]
    prior_source=load(HERE/'preimage/source-manifest.json',lineage['predecessor_metadata']['source-manifest.json']['original_binding']['sha256'])
    prior_profile=load(HERE/'preimage/contract-profile.json',lineage['predecessor_metadata']['contract-profile.json']['original_binding']['sha256'])
    prior_inventory=load(HERE/'preimage/INPUT-ACCOUNTING.json',lineage['predecessor_metadata']['INPUT-ACCOUNTING.json']['original_binding']['sha256'])
    need(set(prior_inventory)=={'schema_version','source_sha256','profile_sha256','unavailable_sha256','additions','consumption','authority_effect','claim_ceiling'} and prior_inventory['source_sha256']==SOURCE_SHA and prior_inventory['profile_sha256']==PROFILE_SHA and prior_inventory['unavailable_sha256']==UNAVAILABLE_SHA,'strict original accounting shape differs')
    prior_additions=unique_rows([item['binding'] for item in prior_inventory['additions']]);prior_rows=unique_rows(prior_source['files'])
    need(prior_source['files']==retained+[prior_additions[path] for path in sorted(prior_additions)] and len(prior_source['files'])==27400 and len(prior_profile['files'])==27399,'complete predecessor rows or order differ')
    need([row['binding'] for row in prior_inventory['consumption']]==original['files']+[prior_additions[path] for path in sorted(prior_additions)],'original accounting consumption order differs')
    need({row['binding']['path'] for row in prior_inventory['consumption'] if row['status']=='historical-metadata-only'}==set(unavailable),'missing historical dispositions differ')
    replacements={}
    for item in inputs['replacement_bindings']:
        need(type(item) is dict and set(item)=={'preimage_binding','postimage_binding'},'open explicit replacement')
        old,new=item['preimage_binding'],item['postimage_binding'];need(old['path']==new['path'] and old['path'] not in replacements and prior_rows.get(old['path'])==old and old['path'] not in parent_by_path and Path(old['path']).name not in GENERATED and old!=new,'unauthorized or aliased predecessor replacement')
        replacements[old['path']]=new;selected(new)
    additions={};classes={};reasons={}
    def add(row,classification,reason,generated=False):
        need(classification in {'successor-code','successor-family','host-dependency'},'invalid accounting class')
        row={'path':logical(row['path']),'sha256':row['sha256']};path=row['path']
        if path in parent_by_path:
            need(parent_by_path[path]==row and path not in unavailable,'changed or unavailable original input: '+path);selected(row);return
        need(additions.get(path,row)==row,'conflicting successor input: '+path)
        if not generated:selected(row)
        additions[path]=row;classes.setdefault(path,classification);reasons.setdefault(path,reason)
    for row in retained:selected(row)
    for item in prior_inventory['additions']:
        row=item['binding']
        if row['path'] in {logical(API/'contract-profile.json'),logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')}:continue
        add(replacements.get(row['path'],row),item['classification'],item['selection_reason'])
    for path,new in replacements.items():need(additions.get(path)==new,'replacement was not retained')
    for item in lineage['capture3_artifacts']:
        add(item['retained_binding'],'successor-code','Raw immutable capture3 artifact retained with exact original origin recorded separately in lineage.')
    for value in lineage['predecessor_metadata'].values():add(value['snapshot_binding'],'successor-code','Exact predecessor source/profile/schema/accounting bytes retained without current-identity alias.')
    for row in [selection_row,selection['writer_binding'],selection['lineage_binding'],selection['known_overlay_receipt_binding'],selection['known_margin_receipt_binding'],selection['final_root_packet_binding'],selection['final_peer_review_binding'],peer['review_binding']]+packet['merged_receipt_bindings']:
        add(row,'successor-code','Explicit independently selected capture4 input/proof, with no receipt authority transfer.')
    expected_api=unique_rows(inputs['api_expected_files']);actual_api=[]
    for path in sorted(API.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or 'receipts' in path.parts:continue
        if path.name in GENERATED:continue
        actual_api.append(logical(path))
    need(set(actual_api)==set(expected_api),'unselected/missing API package code or resource')
    for name in actual_api:
        if Path(name).suffix=='.py':ast.parse((ROOT/name).read_bytes())
        add(expected_api[name],'successor-code','Explicit reviewed final API17 byte expectation, never inferred from ambient code.')
    expected_helpers=unique_rows(inputs['helper_expected_files']);actual_helpers=[]
    need(type(inputs['helper_roots']) is list and inputs['helper_roots'] and len(set(inputs['helper_roots']))==len(inputs['helper_roots']),'closed distinct helper roots required')
    for folder in inputs['helper_roots']:
        closed_family_binding({'path':folder,'sha256':'0'*64});root=ROOT/folder
        need(root.is_dir() and not root.is_symlink() and not any(p.is_symlink() for p in root.parents),'helper root absent or aliased')
        actual_helpers.extend(logical(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts)
    need(len(actual_helpers)==len(set(actual_helpers)) and set(actual_helpers)==set(expected_helpers),'unselected/missing or overlapping composition helper inputs')
    for row in expected_helpers.values():add(row,'successor-code','Every file of explicitly selected helper roots has an independent expected digest.')
    new_family(inputs['active_family'],add)
    need(type(inputs['component_manifests']) is list and inputs['component_manifests'],'new component manifests must be explicitly selected')
    for component in inputs['component_manifests']:
        need(type(component) is dict and set(component)=={'base','path','sha256'},'open component selection')
        closed_family_binding({'path':component['base'],'sha256':'0'*64})
        row={'path':component['path'],'sha256':component['sha256']};manifest=read_selected(row)
        for entry in manifest['files']:
            path=Path(entry['path']);path=path if path.is_absolute() else ROOT/component['base']/path
            add({'path':logical(path),'sha256':entry['sha256']},'successor-code','Full explicitly selected reviewed current component manifest input.')
        add(row,'successor-code','Complete independently selected component manifest at its true origin.')
    for row in inputs['direct_inputs']:add(row,'successor-code','Explicit independently supplied Root-reviewed direct input.')
    software=inputs['public_software_manifest_binding'];manifest=read_selected(software)
    need(type(manifest.get('files')) is list and manifest['files'],'separately frozen public software inventory required')
    for row in manifest['files']:add(row,'successor-code','Public software input inventory frozen before capture, avoiding metadata digest cycles.')
    add(software,'successor-code','Explicit preceding public software inventory, never current metadata self-trust.')
    static={row['path']:row for row in retained};static.update(additions)
    schema=copy.deepcopy(load(HERE/'preimage/SCHEMA-EXECUTION-DEPENDENCIES.json',lineage['predecessor_metadata']['SCHEMA-EXECUTION-DEPENDENCIES.json']['original_binding']['sha256']))
    schema_rows=unique_rows(schema['files']);need(len(schema_rows)==3418,'all current required schema rows must be retained')
    for path,row in schema_rows.items():
        need(path not in unavailable,'schema consumes missing historical byte');schema_rows[path]=replacements.get(path,row)
        need(static.get(path)==schema_rows[path],'required schema input not retained: '+path)
    for path,row in static.items():
        if path.startswith(logical(API)+'/') or (path in additions and path.endswith('.py')):schema_rows[path]=row
    need(set(row['path'] for row in schema['files'])<=set(schema_rows),'schema row pruning forbidden')
    schema['files']=[schema_rows[path] for path in sorted(schema_rows)]
    schema['selection_reasons']={path:schema['selection_reasons'].get(path,['Exact independently selected current capture4 schema execution input.']) for path in sorted(schema_rows)}
    schema_binding=derived('SCHEMA-EXECUTION-DEPENDENCIES.json',schema);add(schema_binding,'successor-code','Complete regenerated schema table retaining all3418 predecessor paths.',True)
    profile=copy.deepcopy(prior_profile)
    seen_updates=set()
    for item in inputs['profile_updates']:
        need(type(item) is dict and set(item)=={'field','preimage_value','postimage_value'},'open profile update')
        key=item['field'];need(type(key) is str and key in profile and key not in seen_updates and not key.startswith(('historical_','original_')) and key not in {'files','schema_execution_dependency_binding','schema_version','authority_effect','actual_owner_outcome','implemented_operations','wire_call_version','wire_reply_version','claim_ceiling'},'profile provenance/domain update forbidden')
        need(profile[key]==item['preimage_value'],'profile update preimage differs');profile[key]=item['postimage_value'];seen_updates.add(key)
    profile['files']=retained+[additions[path] for path in sorted(additions)]
    profile['schema_execution_dependency_binding']=schema_binding
    profile['historical_original_physical_closure']='REFUSED'
    profile['claim_ceiling']='Focused current capture4 candidate; all original and current predecessor provenance retained. No final/whole API/Session/margin/owner/pilot qualification.'
    profile_binding=derived('contract-profile.json',profile);add(profile_binding,'successor-code','New exact derived profile; every original/predecessor byte retained separately.',True)
    current=retained+[additions[path] for path in sorted(additions)]
    need(set(prior_rows)<=set(row['path'] for row in current),'predecessor source path pruning forbidden')
    inventory={'schema_version':'lab-runtime-input-accounting/v1-candidate','source_sha256':SOURCE_SHA,'profile_sha256':PROFILE_SHA,'unavailable_sha256':UNAVAILABLE_SHA,
        'additions':[{'binding':additions[path],'classification':classes[path],'selection_reason':reasons[path]} for path in sorted(additions)],
        'consumption':[{'binding':row,'status':'historical-metadata-only' if row['path'] in unavailable else 'required-current-byte',
            'basis':'Exact absent original locator retained as unavailable provenance; selected current-family callbacks use complete independently pinned current inputs.' if row['path'] in unavailable else 'Full fresh current byte guard retains every present parent row and every explicitly selected successor/host input.'}
            for row in original['files']+[additions[path] for path in sorted(additions)]],
        'authority_effect':'none','claim_ceiling':'Full original row/order accounting, all predecessor paths and explicit current inputs retained; original physical closure remains REFUSED.'}
    inventory_binding=derived('INPUT-ACCOUNTING.json',inventory)
    manifest=copy.deepcopy(prior_source);manifest['files']=current;manifest['profile_binding']=profile_binding
    manifest['input_accounting']['selection_binding']=inventory_binding
    manifest['claim_ceiling']='Focused current capture4 only; no final/whole API/Session/margin/current owner/human pilot qualification.'
    need(manifest['historical_original_physical_closure']=='REFUSED' and manifest['historical_missing_locators']==25 and manifest['original_present_rows_retained']==24472 and manifest['full_original_source_rows']==24497 and manifest['full_original_profile_rows']==24496 and manifest['original_signed_history_schema_callbacks_changed'] is False,'original full-history safeguards changed')
    source_binding=derived('source-manifest.json',manifest)
    result={'schema_version':'lab-T07-capture4-result/v1-candidate','source_binding':source_binding,'profile_binding':profile_binding,'inventory_binding':inventory_binding,'schema_binding':schema_binding,
        'selection_binding':selection_row,'lineage_binding':selection['lineage_binding'],'final_root_packet_binding':selection['final_root_packet_binding'],
        'current_guard_rows':len(current),'retained_present_parent_rows':len(retained),'retained_predecessor_paths':len(prior_rows),'added_execution_rows':len(additions),'schema_execution_rows':len(schema['files']),
        'historical_physical_closure':'REFUSED','runtime_qualified':False,'task_complete':False,'authority_effect':'none'}
    outputs={'SCHEMA-EXECUTION-DEPENDENCIES.json':schema,'contract-profile.json':profile,'INPUT-ACCOUNTING.json':inventory,'source-manifest.json':manifest}
    publish(outputs,lineage,result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
