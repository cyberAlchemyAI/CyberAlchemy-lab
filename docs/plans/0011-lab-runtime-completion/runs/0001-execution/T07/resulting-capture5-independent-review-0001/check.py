"""Cold read-only capture5 output review. Does not execute capture/API/runtime code."""
import argparse,copy,hashlib,json,os,stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
CAP4=RUN/'T07/api17-task-local-capture-0004';CAP5=RUN/'T07/api17-task-local-capture-0005'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
GEN={'source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'}
held={};sha=lambda b:hashlib.sha256(b).hexdigest()
def logical(p):
    p=Path(p);p=p if p.is_absolute() else ROOT/p
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
def capture(row):
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    assert '..' not in p.parts and not any(x.is_symlink() for x in [p,*p.parents])
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        identity=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        start=os.fstat(fd);assert stat.S_ISREG(start.st_mode);chunks=[]
        while True:
            b=os.read(fd,1024*1024)
            if not b:break
            chunks.append(b)
        raw=b''.join(chunks);assert identity(start)==identity(os.fstat(fd))
        assert sha(raw)==row['sha256'],str(p)
        if 'size_bytes' in row:assert len(raw)==row['size_bytes']
        record=(row['sha256'],identity(start));assert str(p) not in held or held[str(p)]==record
        held[str(p)]=record;return raw
    finally:os.close(fd)
def load(row):return json.loads(capture(row))
def pin(p,h):return dict(path=logical(p),sha256=h)
def unique(rows):
    d={r['path']:r for r in rows};assert len(d)==len(rows);return d
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--result-sha',required=True);args=parser.parse_args()
    fd0=len(os.listdir('/proc/self/fd'))
    resultrow=pin(CAP5/'capture-result.json',args.result_sha);result=load(resultrow)
    assert result['schema_version']=='lab-T07-capture5-result/v1-candidate' and result['authority_effect']=='none' and result['runtime_qualified'] is False and result['task_complete'] is False
    for key,digest in {'source_binding':'ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1','profile_binding':'9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b','inventory_binding':'44443a5a83f64dfb95aad167dfef7e3a86453436aed8f44cc4c8824ef3b8720c','schema_binding':'441153854bf900e54c8f38f519dacdded03a9fa46662b40dac9bb5fef11ae9fe'}.items():assert result[key]['sha256']==digest
    selectionrow=pin(CAP5/'final-component-selection-0001.json','a3ac43e4b6ae053462df6f239a94756cf8b72d94606a1bba18e8e298acea3e24');selection=load(selectionrow)
    assert result['selection_binding']==selectionrow and selection['status']=='closed-for-Root-capture'
    packet=load(selection['final_root_packet_binding']);peer=load(selection['final_peer_review_binding']);review=load(peer['review_binding'])
    assert selection['final_root_packet_binding']['sha256']=='34fb89f5ad60406814546b55fb25a14fb6eda520e0466c85afd92b59a36e0829'
    assert selection['final_peer_review_binding']['sha256']=='f50db72072e3fbca4eea073a7e7e73bad426380bbc9c7d817d6e9402d2b0e5cf'
    assert peer['result']==review['result']=='PASS' and peer['reviewed_root_packet_binding']==review['reviewed_root_packet_binding']==selection['final_root_packet_binding']
    assert result['final_root_packet_binding']==selection['final_root_packet_binding'] and packet['inputs']==selection['inputs']
    inputs=selection['inputs'];lineage=load(selection['lineage_binding']);assert result['lineage_binding']==selection['lineage_binding']
    prior={n:load(r['snapshot_binding']) for n,r in lineage['predecessor_metadata'].items()}
    for r in lineage['capture3_artifacts']:capture(r['original_binding']);capture(r['retained_binding'])
    original=load(pin(API.parent/'api-integration-v16/source-manifest.json','8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'))
    oldprofile=load(pin(API.parent/'api-integration-v16/contract-profile.json','8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'))
    absentrow=pin(RUN/'T07/accounting-0001/unavailable-original-inputs.json','4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a');absent=load(absentrow)
    missing={r['binding']['path'] for r in absent['rows']};assert len(missing)==25
    source=load(result['source_binding']);profile=load(result['profile_binding']);schema=load(result['schema_binding']);inventory=load(result['inventory_binding'])
    assert result['source_binding']['path']==logical(API/'source-manifest.json') and result['profile_binding']['path']==logical(API/'contract-profile.json') and result['schema_binding']['path']==logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json') and result['inventory_binding']['path']==logical(API/'INPUT-ACCOUNTING.json')
    assert source['profile_binding']==result['profile_binding'] and source['input_accounting']['selection_binding']==result['inventory_binding'] and profile['schema_execution_dependency_binding']==result['schema_binding']
    assert len(original['files'])==24497 and len(oldprofile['files'])==24496
    retained=[r for r in original['files'] if r['path'] not in missing];assert len(retained)==24472
    old=unique(prior['source-manifest.json']['files']);assert len(old)==27400 and len(prior['contract-profile.json']['files'])==27399
    replacements={r['preimage_binding']['path']:r['postimage_binding'] for r in inputs['replacement_bindings']};assert len(replacements)==7
    for pair in inputs['replacement_bindings']:
        pre,post=pair['preimage_binding'],pair['postimage_binding'];assert pre['path']==post['path'] and old[pre['path']]==pre and pre['path'] not in unique(original['files'])
    expected={p:replacements.get(p,r) for p,r in old.items()}
    expected[logical(API/'contract-profile.json')]=result['profile_binding'];expected[logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]=result['schema_binding']
    def add(r):
        r=dict(path=logical(r['path']),sha256=r['sha256']);p=r['path']
        assert p not in expected or expected[p]==r,(p,expected.get(p),r)
        expected[p]=r
    for r in lineage['capture3_artifacts']:add(r['retained_binding'])
    for r in lineage['predecessor_metadata'].values():add(r['snapshot_binding'])
    for r in [selectionrow,selection['writer_binding'],selection['lineage_binding'],selection['known_overlay_receipt_binding'],selection['known_margin_receipt_binding'],selection['final_root_packet_binding'],selection['final_peer_review_binding'],peer['review_binding']]+packet['merged_receipt_bindings']:add(r)
    for k in ['api_expected_files','helper_expected_files','direct_inputs']:
        for r in inputs[k]:add(r)
    family=inputs['active_family'];descriptor=load(family['descriptor_binding']);actualfamily=load(family['actual_family_selection_binding']);acc=load(family['pre_source_acceptance_binding'])
    for r in family['family_bindings'].values():add(r)
    for r in family['phase_report_bindings']:add(r)
    for k in ['source_binding','reader_binding','mapper_binding','context_source_binding']:
        for r in load(family['family_bindings'][k])['files']:add(r)
    for r in [family['descriptor_binding'],family['actual_family_selection_binding'],actualfamily['construction_binding'],family['pre_source_acceptance_binding'],acc['preview_binding'],acc['independent_review_binding']]:add(r)
    for k in ['previous_runtime_selection_binding','optimized_capture_selection_binding']:add(descriptor[k])
    for r in descriptor['runtime_postimages']:add(r)
    for r in family['template_preimages']:add(r['snapshot_binding'])
    for component in inputs['component_manifests']:
        for r in load(component)['files']:
            p=Path(r['path']);p=p if p.is_absolute() else ROOT/component['base']/p;add(dict(path=logical(p),sha256=r['sha256']))
        add(component)
    required=json.loads((CAP5/'required-components.json').read_bytes())['bindings']
    for r in required.values():add(r)
    add(pin(RUN/'T02/composite-merge-preparation-0004/independent-review-0001.json','77bc2e7b6e925d5eba46d805f5aaf501d15fc22843aad3eaf47d34657f3ac028'))
    add(pin(RUN/'T35/full-learning-driver-0004/independent-review-0001.json','48f731601527ce05cf6a771a3c49ab2cbf0e2103adddff992f91ff90c253bf25'))
    software=load(inputs['public_software_manifest_binding']);assert len(software['files'])==16
    for r in software['files']:add(r)
    add(inputs['public_software_manifest_binding']);assert not inputs['profile_updates']
    current=unique(source['files']);assert current==expected and set(old)<=set(current)
    assert source['files']==retained+[current[p] for p in sorted(set(current)-{r['path'] for r in retained})]
    assert profile['files']==[r for r in source['files'] if r['path']!=logical(API/'contract-profile.json')]
    changes_profile={k for k in profile.keys()|prior['contract-profile.json'].keys() if profile.get(k)!=prior['contract-profile.json'].get(k)}
    assert changes_profile<={'files','schema_execution_dependency_binding','historical_original_physical_closure','claim_ceiling'}
    source_old=copy.deepcopy(prior['source-manifest.json']);source_new=copy.deepcopy(source)
    for d in [source_old,source_new]:
        for k in ['files','profile_binding','claim_ceiling']:d.pop(k)
        d['input_accounting'].pop('selection_binding')
    assert source_old==source_new
    oldschema=unique(prior['SCHEMA-EXECUTION-DEPENDENCIES.json']['files']);assert len(oldschema)==3418
    for p in oldschema:assert schema['selection_reasons'][p]==prior['SCHEMA-EXECUTION-DEPENDENCIES.json']['selection_reasons'][p]
    schema_expected={p:replacements.get(p,r) for p,r in oldschema.items()}
    for p,r in current.items():
        if p.startswith(logical(API)+'/') or (p not in {r['path'] for r in retained} and p.endswith('.py')):
            if p not in {logical(API/'contract-profile.json'),logical(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')}:schema_expected[p]=r
    assert unique(schema['files'])==schema_expected
    assert set(schema['selection_reasons'])==set(schema_expected)
    originalpaths={r['path'] for r in original['files']};additions=unique([r['binding'] for r in inventory['additions']]);assert set(additions)==set(current)-originalpaths
    assert inventory['source_sha256']=='8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7' and inventory['profile_sha256']=='8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c' and inventory['unavailable_sha256']==absentrow['sha256']
    assert [r['binding'] for r in inventory['consumption']]==original['files']+[additions[p] for p in sorted(additions)]
    assert {r['binding']['path'] for r in inventory['consumption'] if r['status']=='historical-metadata-only'}==missing
    new_adds={r['binding']['path']:r for r in inventory['additions']};prior_adds={r['binding']['path']:r for r in prior['INPUT-ACCOUNTING.json']['additions']};assert len(prior_adds)==2928
    generated_two={logical(API/n) for n in ['contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json']}
    for p,r in prior_adds.items():
        assert new_adds[p]['classification']==r['classification']
        if p not in generated_two:assert new_adds[p]['selection_reason']==r['selection_reason']
    assert all(r['classification'] in ['successor-code','successor-family','host-dependency'] and r['selection_reason'] for r in inventory['additions'])
    assert len(current)==result['current_guard_rows'] and len(additions)==result['added_execution_rows'] and len(schema['files'])==result['schema_execution_rows']
    assert result['retained_predecessor_paths']==27400 and result['retained_present_parent_rows']==24472 and result['historical_physical_closure']=='REFUSED'
    assert source['historical_original_physical_closure']==profile['historical_original_physical_closure']=='REFUSED' and source['historical_missing_locators']==25 and source['original_signed_history_schema_callbacks_changed'] is False
    for r in source['files']:capture(r)
    for r in schema['files']:assert current[r['path']]==r
    for r in profile['files']:assert current[r['path']]==r
    for p,(pin_value,identity) in list(held.items()):capture(dict(path=p,sha256=pin_value))
    assert len(os.listdir('/proc/self/fd'))==fd0
    report=dict(result='PASS-resulting-capture5-full-source-profile-schema-accounting',capture_result_binding=resultrow,capture_result=result,all_current_source_files_freshly_guarded=len(current),unique_entry_exit_inputs=len(held),FD_delta=0,prior_source_paths_conserved=27400,prior_profile_paths_conserved=27399,original_source_rows_conserved=24497,original_profile_rows_conserved=24496,original_present_rows_guarded=24472,unavailable_historical_dispositions=25,historical_physical_closure='REFUSED',replacement_pairs=7,old_schema_paths_reasons_conserved=3418,prior_addition_classes_conserved=2928,prior_literal_addition_reasons_conserved=2926,derived_output_reason_successors=2,exact_declared_union_matches_source=True,exact_profile_file_membership=True,exact_schema_execution_union=True,other_profile_source_scalars_preserved=True,schema_profile_Source_internal_bindings_verified=True,actual_Root_selection_packet_peer_result_correspondence=True,writer_or_API_imported_or_executed=False,native_runtime_lease_or_private_packet_calls=False,private_bodies_exported=False,authority_effect='none',runtime_qualified=False,task_complete=False)
    with (Path(__file__).parent/'controls-0001.json').open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
