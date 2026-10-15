"""Full original native semantics in owned generations under real process kills."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from fixtures import sealed_fixture,call
from recoverable_store import GenerationStore,PendingPins,sha,read

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32'

def all_files(root):
    rows={}
    for p in root.rglob('*'):
        if p.is_symlink():rows[str(p.relative_to(root))]='SYMLINK:'+str(p.readlink())
        elif p.is_file():
            try:rows[str(p.relative_to(root))]=sha(p.read_bytes())
            except PermissionError:rows[str(p.relative_to(root))]='UNREADABLE:'+str(p.stat().st_size)+':'+str(p.stat().st_mode)
    return rows

def real_kill(value,path):
    selection=path/'child-selection.json';selection.write_text(json.dumps(value,indent=2)+'\n')
    child=subprocess.Popen([sys.executable,'-I','-B',str(HERE/'child_run.py'),str(selection)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'})
    deadline=time.monotonic()+30;marker=Path(value['marker'])
    while not marker.exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(0.01)
    if not marker.exists():
        if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
        out,err=child.communicate();raise ValueError('child checkpoint absent: '+err.decode())
    assert child.poll() is None and marker.read_bytes()==value['stage'].encode()
    live_reader=GenerationStore(value['root'],value['identity'],value['executable'],value['executable_sha256'])
    live_cut=live_reader.read_committed();live_count=len(live_cut['native_cut']['semantic_events'])
    assert live_count==(6 if value['stage']=='after-head-commit' else 3)
    before=all_files(path);assert os.getpgid(child.pid)==child.pid
    os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=10);assert child.returncode==-9
    after=all_files(path);assert before==after
    return {'pid':child.pid,'child_exit_code':-9,'real_kill_process_group':True,'owned_checkpoint':value['stage'],'preserved_files_after_kill':after,'reader_succeeded_while_original_child_live':True,'live_reader_semantic_event_count':live_count}

def expect_refusal(function):
    try:function()
    except (ValueError,OSError) as error:return {'refused':True,'error_type':type(error).__name__,'message':str(error)}
    raise AssertionError('expected actual refusal')

def main():
    owned=HERE/'wrapper-episodes-0005';owned.mkdir(mode=0o700)
    production=HERE/'bin-production/lab-ontology-native';observer=HERE/'build-observer/debug/lab-ontology-native';executable_sha=sha(observer.read_bytes())
    base_request,base_events=sealed_fixture(production,HERE/'wrapper-baseline-fixture-0005')
    request,events=sealed_fixture(production,HERE/'wrapper-successor-fixture-0005',offset=3)
    cases=[]
    scenarios=[('native',family,stage) for family in ['semantic','governance'] for stage in ['after-lock','after-first-link','before-cleanup']]
    scenarios+=[('wrapper','none',stage) for stage in ['before-generation-publish','before-head-commit','after-head-commit']]
    scenarios+=[('foreign','semantic',stage) for stage in ['unknown-file','unknown-lock','changed-event','unreadable-file','symlink-event']]
    for number,(kind,family,stage) in enumerate(scenarios):
        path=owned/(f'{number:02d}-'+kind+'-'+family+'-'+stage);path.mkdir(mode=0o700);store_root=path/'store';store_root.mkdir(mode=0o700);s=store_root.stat();identity=(s.st_dev,s.st_ino)
        store=GenerationStore(store_root,identity,observer,executable_sha);store.bootstrap()
        pending,pins=store.prepare(base_request,sha(base_request.read_bytes()));store.run(pending,pins)
        pending,pins=store.prepare(request,sha(request.read_bytes()));old_head=read(store_root/'HEAD.json');old_cut=store.read_committed();assert len(old_cut['native_cut']['semantic_events'])==3
        foreign=store_root/'foreign-sibling.bin';foreign.write_bytes(b'foreign sibling must never be deleted')
        child_stage='after-first-link' if kind=='foreign' else stage
        value={'root':str(store_root),'identity':identity,'executable':str(observer),'executable_sha256':executable_sha,'pending':str(pending),'pins':asdict(pins),'kind':'native' if kind in ['native','foreign'] else 'wrapper','stage':child_stage,'family':family,'marker':str(path/'checkpoint.marker')}
        observation=real_kill(value,path);journal=json.loads(pending.read_bytes());original_stage=store_root/journal['stage'];original_snapshot=all_files(original_stage) if original_stage.exists() else None
        fresh=GenerationStore(store_root,identity,observer,executable_sha)
        before=fresh.read_committed();expected_count=6 if stage=='after-head-commit' else 3;assert len(before['native_cut']['semantic_events'])==expected_count
        head,head_raw,directory=fresh.head();cold=call(production,'read',directory/'semantic',directory/'governance',expected_count);assert cold.returncode==0 and json.loads(cold.stdout)['checkpoint_parity']=='PASS'
        if kind=='foreign':
            target=original_stage/'semantic'
            if stage=='unknown-file':(target/'foreign.bin').write_bytes(b'foreign bytes must remain')
            elif stage=='unknown-lock':(target/'.append.lock').write_bytes(b'foreign lock owner')
            elif stage=='changed-event':
                p=next(p for p in target.iterdir() if p.name.endswith('.json') and 'T32-semantic-4' in p.name);p.write_bytes(b'foreign altered event')
            elif stage=='unreadable-file':
                p=target/'foreign-private.key';p.write_bytes(b'owned synthetic placeholder, never an actual key');p.chmod(0o000)
            else:
                p=next(p for p in target.iterdir() if p.name.endswith('.json') and 'T32-semantic-4' in p.name);saved=path/'selected-event-before-symlink';p.rename(saved);p.symlink_to(saved)
            foreign_snapshot=all_files(store_root);refusal=expect_refusal(lambda:fresh.run(pending,pins,recover=True));assert all_files(store_root)==foreign_snapshot and read(store_root/'HEAD.json')==old_head
            if stage=='unreadable-file':assert refusal['error_type']=='ValueError' and refusal['message']=='unknown generation file'
            result={'refusal':refusal,'foreign_bytes_preserved':True,'committed_generation_unchanged':True}
        else:
            result=fresh.run(pending,pins,recover=True);assert result['committed']
            recovered=fresh.read_committed();assert len(recovered['native_cut']['semantic_events'])==6 and len(recovered['native_cut']['governance_events'])==6
            assert recovered['native_cut']['semantic_events']==base_events['semantic']+events['semantic'] and recovered['native_cut']['governance_events']==base_events['governance']+events['governance']
            head,head_raw,directory=fresh.head();cold=call(production,'read',directory/'semantic',directory/'governance',6);assert cold.returncode==0 and json.loads(cold.stdout)['semantic_events']==base_events['semantic']+events['semantic']
            same_head=read(store_root/'HEAD.json');again=fresh.run(pending,pins,recover=True);assert again['idempotent'] and read(store_root/'HEAD.json')==same_head
            if kind=='native':assert original_stage.exists() and all_files(original_stage)==original_snapshot and any(p.name=='.append.lock' for p in (original_stage/family).iterdir())
            result={'committed':True,'cold_original_native_replay':True,'exact_semantic_and_governance_events':True,'retry_idempotent':True,'original_interrupted_stage_retained':kind=='native','readable_previous_generation_after_precommit_kill':stage!='after-head-commit','commit_point':'fsynced-HEAD-replacement'}
        assert foreign.read_bytes()==b'foreign sibling must never be deleted'
        row={'kind':kind,'family':family,'stage':stage,'result':'PASS','observation':observation,'recovery':result,'production_executable_sha256':sha(production.read_bytes()),'observer_executable_sha256':executable_sha,'authority_effect':'none'}
        (RUN/('wrapper-case-'+str(number).zfill(2)+'-0003.json')).write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');cases.append(row)
    summary={'result':'PASS','cases':len(cases),'native_interruptions':6,'outer_commit_interruptions':3,'foreign_residue_refusals':5,'all_real_process_kills':True,'no_foreign_deletions':True,'exact_original_native_cold_replay_after_recovery':True,'selected_original_runtime_integrated':False,'task_complete':False,'authority_effect':'none'}
    (RUN/'wrapper-recovery-summary-0003.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary));return 0

if __name__=='__main__':raise SystemExit(main())
