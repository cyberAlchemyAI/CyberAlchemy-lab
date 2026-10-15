"""Independent capture5 declarations/current-byte review. Never imports writer."""
import argparse, ast, hashlib, json, os, stat
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
CAP4=RUN/'T07/api17-task-local-capture-0004'
CAP5=RUN/'T07/api17-task-local-capture-0005'
PROP=RUN/'T07/final-capture5-inputs-proposal-0001'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
GEN={'source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'}
held={}; checks={}
sha=lambda b:hashlib.sha256(b).hexdigest()
def capture(row):
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    assert '..' not in p.parts and not any(x.is_symlink() for x in [p,*p.parents])
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd);assert stat.S_ISREG(s.st_mode); chunks=[]
        while True:
            b=os.read(fd,1024*1024)
            if not b:break
            chunks.append(b)
        raw=b''.join(chunks)
        identity=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        assert identity(s)==identity(os.fstat(fd))
        assert sha(raw)==row['sha256'],str(p)
        assert 'size_bytes' not in row or len(raw)==row['size_bytes']
        record=identity(s)
        assert p.stat(follow_symlinks=False).st_ino==s.st_ino
        if str(p) in held:assert held[str(p)]==(row['sha256'],record)
        held[str(p)]=(row['sha256'],record)
        return raw
    finally:os.close(fd)
def load(row):return json.loads(capture(row))
def binding(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()))
def known(p,pin):return load(dict(path=str(p.relative_to(ROOT)),sha256=pin))
def unique(rows):
    assert isinstance(rows,list);d={r['path']:r for r in rows};assert len(d)==len(rows);return d
def main():
    a=argparse.ArgumentParser();a.add_argument('--input-sha',required=True);a.add_argument('--result',required=True);a.add_argument('--root-packet');a.add_argument('--root-sha');args=a.parse_args()
    fd0=len(os.listdir('/proc/self/fd'))
    inp=known(PROP/'proposed-inputs.json',args.input_sha)
    assert set(inp)=={'api_expected_files','helper_roots','helper_expected_files','component_manifests','direct_inputs','replacement_bindings','active_family','public_software_manifest_binding','guard_binding','profile_updates'}
    writer=capture(dict(path=str((CAP5/'capture_v5.py').relative_to(ROOT)),sha256='488db1f09b24e987035a5c249104972bb18ef7a618d6e593f17305695cb6e7ef'))
    ast.parse(writer,filename=str(CAP5/'capture_v5.py'))
    lineage=known(CAP4/'lineage.json','c13bc99371a65b0f0a39aa1418c0eb4c476b05fc94610128840500c9d0d442f1')
    assert lineage['historical_physical_closure']=='REFUSED'
    for r in lineage['capture3_artifacts']:
        assert r['original_binding']['sha256']==r['retained_binding']['sha256'];capture(r['original_binding']);capture(r['retained_binding'])
    for r in lineage['predecessor_metadata'].values():
        assert r['original_binding']['sha256']==r['snapshot_binding']['sha256'];capture(r['original_binding']);capture(r['snapshot_binding'])
    prior={n:load(r['snapshot_binding']) for n,r in lineage['predecessor_metadata'].items()}
    original=known(API.parent/'api-integration-v16/source-manifest.json','8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7')
    oldprofile=known(API.parent/'api-integration-v16/contract-profile.json','8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c')
    absent=known(RUN/'T07/accounting-0001/unavailable-original-inputs.json','4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a')
    missing={r['binding']['path'] for r in absent['rows']};assert len(missing)==25
    originals=unique(original['files']);old=unique(prior['source-manifest.json']['files']);adds=unique([r['binding'] for r in prior['INPUT-ACCOUNTING.json']['additions']])
    assert len(originals)==24497 and len(oldprofile['files'])==24496 and len(old)==27400 and len(prior['contract-profile.json']['files'])==27399 and len(adds)==2928
    retained=[r for r in original['files'] if r['path'] not in missing]
    assert prior['source-manifest.json']['files']==retained+[adds[p] for p in sorted(adds)]
    consumption=prior['INPUT-ACCOUNTING.json']['consumption']
    assert [r['binding'] for r in consumption]==original['files']+[adds[p] for p in sorted(adds)]
    assert {r['binding']['path'] for r in consumption if r['status']=='historical-metadata-only'}==missing
    repl={}
    for r in inp['replacement_bindings']:
        pre,post=r['preimage_binding'],r['postimage_binding'];assert pre['path']==post['path'] and pre!=post and old[pre['path']]==pre and pre['path'] not in originals and Path(pre['path']).name not in GEN and pre['path'] not in repl
        repl[pre['path']]=post;capture(post)
    assert len(repl)==7
    expected=unique(inp['api_expected_files']);assert len(expected)==165
    actual={str(p.relative_to(ROOT)) for p in API.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.name not in GEN}
    assert set(expected)==actual
    for r in expected.values():capture(r)
    assert inp['guard_binding']==lineage['current_guard_binding'];capture(inp['guard_binding'])
    helpers=unique(inp['helper_expected_files']);assert len(helpers)==7 and len(inp['helper_roots'])==len(set(inp['helper_roots']))==3
    actualhelpers=[str(p.relative_to(ROOT)) for r in inp['helper_roots'] for p in (ROOT/r).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    assert len(actualhelpers)==len(set(actualhelpers)) and set(actualhelpers)==set(helpers)
    for r in helpers.values():capture(r)
    current=dict(old)
    for p,r in old.items():
        if p.startswith(str(API.relative_to(ROOT))+'/') and Path(p).name in GEN:continue
        capture(repl.get(p,r));current[p]=repl.get(p,r)
    components=unique(inp['component_manifests']);assert len(components)==19;component_rows=0
    def add(r):
        r=dict(path=r['path'],sha256=r['sha256']);capture(r)
        if r['path'] in originals:assert originals[r['path']]==r and r['path'] not in missing
        if r['path'] in current:assert current[r['path']]==r
        current[r['path']]=r
    for r in inp['component_manifests']:
        assert set(r)=={'path','sha256','base'}
        m=load(r)
        for row in m['files']:
            p=Path(row['path']);p=p if p.is_absolute() else ROOT/r['base']/p
            add(dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),sha256=row['sha256']));component_rows+=1
        add(r)
    direct=unique(inp['direct_inputs']);assert len(direct)==115
    for r in direct.values():add(r)
    software=load(inp['public_software_manifest_binding']);assert len(software['files'])==16 and software['authority_effect']=='none'
    assert inp['public_software_manifest_binding']['sha256']=='5bdd8adba0ffd73ea2ab5121e6a52ce232c86bf398b1ed25c233b7f3bd3e9081'
    for r in software['files']:add(r)
    family=inp['active_family'];assert len(family)==7
    runtime=load(family['descriptor_binding']);actualfamily=load(family['actual_family_selection_binding'])
    assert runtime['instance']==actualfamily['instance']=='optimized-0005' and runtime['actual_family_selection_binding']==family['actual_family_selection_binding']
    assert sorted(runtime)==family['descriptor_keys'] and family['family_bindings']==actualfamily['family_bindings'] and len(family['family_bindings'])==9
    baseline=known(RUN/'T02/optimized-family-preparation-0005/preparation-baseline.json','95a73902cc5b584f0185a0b16df5ad4213816d57a0356e8fc3bc62c86fba0067')
    construction=load(actualfamily['construction_binding']);assert construction['optimized_recipe_declaration_mapping']==baseline['declaration_mapping'] and len(baseline['declaration_mapping'])==349
    assert construction['mutable_API_preparation_snapshot_pairs']==baseline['mutable_snapshot_pairs']
    snapshots=[r['snapshot_binding'] for r in baseline['mutable_snapshot_pairs']];assert len(snapshots)==6
    forbidden={str(API.relative_to(ROOT))+'/'+n for n in GEN|{'source_bridge.py','current_context_sessions.py','authentication.schema.json','machine_auth_scope.py','current_machine_context_scope.py'}}
    acc=load(family['pre_source_acceptance_binding']);assert acc['construction_binding']==actualfamily['construction_binding'] and acc['status']=='Root-reviewed-staged-family5-closure'
    preview=load(acc['preview_binding']);pvpeer=load(acc['independent_review_binding']);assert pvpeer['result']=='PASS' and pvpeer['construction_binding']==acc['construction_binding'] and pvpeer['preview_binding']==acc['preview_binding']
    count=0
    for key,r in family['family_bindings'].items():
        assert runtime[key]==r;m=load(r)
        if 'files' in m:
            for row in m['files']:add(row);count+=1
        if key in ['source_binding','reader_binding','mapper_binding','context_source_binding']:
            assert all(row in m['files'] for row in snapshots) and not set(unique(m['files']))&forbidden
            if key=='source_binding':assert m==preview['source_manifest_value']
    assert actualfamily['phase_reports']==family['phase_report_bindings']
    phases=[load(r) for r in family['phase_report_bindings']];assert [r['phase'] for r in phases]==['source','cold','reader','mapped','context'] and all(r['result']=='PASS' and r['error'] is None for r in phases)
    pairs=[dict(original_binding=r['original_binding'],snapshot_binding=r['snapshot_binding']) for r in baseline['runtime_template_snapshot_pairs']]
    assert pairs==family['template_preimages']==runtime['original_template_preimages']
    assert [r['original_binding'] for r in pairs]==runtime['original_templates']
    for r in pairs:assert r['original_binding']['sha256']==r['snapshot_binding']['sha256'];capture(r['snapshot_binding'])
    schema=prior['SCHEMA-EXECUTION-DEPENDENCIES.json'];assert len(schema['files'])==3418 and set(unique(schema['files']))==set(schema['selection_reasons'])
    for r in schema['files']:assert r['path'] not in missing and current[r['path']]==repl.get(r['path'],r)
    assert not inp['profile_updates'] and set(old)<=set(current)
    packetbinding=None
    if args.root_packet:
        packetbinding=dict(path=args.root_packet,sha256=args.root_sha);packet=load(packetbinding)
        assert len(packet)==9 and packet['status']=='Root-reviewed-merged-native-family5-ready-for-capture' and packet['inputs']==inp and packet['authority_effect']=='none'
        assert packet['lineage_binding']==dict(path=str((CAP4/'lineage.json').relative_to(ROOT)),sha256='c13bc99371a65b0f0a39aa1418c0eb4c476b05fc94610128840500c9d0d442f1')
        assert packet['writer_binding']['sha256']=='488db1f09b24e987035a5c249104972bb18ef7a618d6e593f17305695cb6e7ef'
        for r in packet['merged_receipt_bindings']:capture(r)
    for p,(pin,record) in list(held.items()):capture(dict(path=p,sha256=pin))
    assert len(os.listdir('/proc/self/fd'))==fd0
    report=dict(result='PASS-pure-declaration-and-current-byte-review',proposed_inputs_binding=binding(PROP/'proposed-inputs.json'),actual_Root_packet_binding=packetbinding,source_rows_conserved=27400,profile_rows_conserved=27399,original_source_rows=24497,original_profile_rows=24496,original_present_rows_fresh=24472,original_unavailable_dispositions=25,historical_physical_closure='REFUSED',prior_additions_classes_reasons_conserved=2928,prior_schema_paths_reasons_conserved=3418,successor_replacements=7,current_API=165,helpers=7,helper_roots=3,components=19,component_row_occurrences=component_rows,direct_inputs=115,software_rows=16,native_family_row_occurrences=count,all_five_phases_PASS=True,snapshots_in_every_role=6,forbidden_live_API_inputs_per_role=0,all_five_true_template_pairs=True,source_equals_preview=True,unique_fresh_entry_exit_inputs=len(held),FD_delta=0,writer_imported_or_executed=False,native_runtime_or_lease_calls=False,private_bodies_exported=False,authority_effect='none',task_complete=False)
    with (Path(__file__).parent/args.result).open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
