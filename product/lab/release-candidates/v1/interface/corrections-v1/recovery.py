"""Actual process interruption of exact signed correction batches and recovery."""
import subprocess
from episode import *


def public_files(store):
    return {p.relative_to(store.path).as_posix():{'sha256':sha(p.read_bytes()),'base64_original_bytes':base64.b64encode(p.read_bytes()).decode()}
        for p in sorted(store.path.rglob('*.json'))}


def child(root,input_path,pins):
    root=Path(root);require(root.is_relative_to(Path('/tmp')) and not root.is_relative_to(ROOT),'owned crash store required')
    value=parse(Path(input_path).read_bytes())
    with engine(pins) as handle:
        handle.replay_owned(root/'store',value['config_sha256'],value['baseline_snapshot_digest'],value['expected_head'])
        handle.store_module.Store(root/'store',ROOT).apply(value['proposal'],value['approval'],crash_at=value['crash_at'])
    raise ValueError('injection failed to interrupt the real process')


def run(destination,pins):
    destination=Path(destination).resolve();require(destination.is_relative_to(EXAMPLES) and not destination.exists(),'fresh selected recovery evidence required')
    destination.mkdir(parents=True);rows=[]
    for stage in ['after-pending','before-head','after-head']:
        out=destination/stage;out.mkdir();start=time.perf_counter()
        with tempfile.TemporaryDirectory(prefix='cal-R03-correction-recovery-') as temporary,engine(pins) as handle:
            owned=Path(temporary);store,key=handle.create_owned(owned,'R03-correction-recovery-'+stage,selected_project_scope=True,correction_domains=[DOMAIN])
            emit(out/'project-setup.json',project_setup(handle,store,key));before=store.replay(require_current=True)
            proposal=correction_proposal(handle,before,'R03-correction-recovery-'+stage);approval=store.authorize(proposal,key)
            input_value={'proposal':proposal,'approval':approval,'crash_at':stage,'config_sha256':sha((store.path/'config.json').read_bytes()),
                'baseline_snapshot_digest':before['baseline']['snapshot_digest'],'expected_head':before['head']['transaction_digest']}
            emit(out/'input.json',input_value);emit(owned/'input.json',input_value)
            committed={name:entry for name,entry in public_files(store).items() if name.startswith('transactions/')}
            emit(out/'before-public-files.json',public_files(store))
            # The child consumes a pre-existing exact public signature, never the private key.
            key.unlink();(owned/'owner.pub').unlink()
            process=subprocess.run([sys.executable,str(HERE/'recovery.py'),'child',str(owned),str(owned/'input.json'),str(HERE/'pins.json')],capture_output=True)
            (out/'child.stdout').write_bytes(process.stdout);(out/'child.stderr').write_bytes(process.stderr)
            require(process.returncode==86,'actual child did not reach selected interruption')
            emit(out/'interrupted-public-files.json',public_files(store));interrupted=store.replay(require_current=True)
            expected_sequence=2 if stage=='after-head' else 1
            require(interrupted['head']['sequence']==expected_sequence,'interruption published wrong committed prefix')
            if stage=='after-head':verify_result(handle,before,interrupted,proposal)
            else:require(all(t['version_ref'] not in interrupted['projection']['subjects'] for t in proposal['targets']),'precommit interruption exposed correction')
            wrong_head='0'*64;files_before_wrong=public_files(store)
            try:store.recover(wrong_head)
            except Exception:pass
            else:raise ValueError('wrong HEAD recovery accepted')
            require(public_files(store)==files_before_wrong,'wrong HEAD recovery changed original files')
            recovery=store.recover(interrupted['head']['transaction_digest']);emit(out/'recovery.json',recovery)
            require(not store.leftovers(interrupted['head']),'recovery left uncommitted material')
            for name,b in committed.items():require(sha((store.path/name).read_bytes())==b['sha256'],'recovery changed original committed prefix')
            applied=store.apply(proposal,approval);require(applied['idempotent']==(stage=='after-head'),'recovery retry commit boundary differs')
            emit(out/'application.json',applied);retry=store.apply(proposal,approval)
            require(retry['idempotent'] and retry['transaction_digest']==applied['transaction_digest'],'recovered retry differs')
            emit(out/'retry.json',retry);after=store.replay(require_current=True);corrections=verify_result(handle,before,after,proposal)
            original_archive=archive(store,pins);emit(out/'branch.snapshot',original_archive)
            expected={'projection_sha256':handle.common.digest(after['projection']),'transaction_sha256s':[handle.common.digest(t) for t in after['transactions']],
                'applied_corrections':corrections,'config_sha256':sha((store.path/'config.json').read_bytes()),'expected_head':after['head']['transaction_digest'],
                'baseline_snapshot_digest':after['baseline']['snapshot_digest'],'engine_pins':asdict(pins),'archive_sha256':sha((out/'branch.snapshot').read_bytes())}
            emit(out/'expected-replay.json',expected)
        require(not owned.exists(),'owned recovery store remains')
        cold=subprocess.run([sys.executable,str(HERE/'cold.py'),str(out),sha((out/'expected-replay.json').read_bytes()),str(HERE/'pins.json')],capture_output=True)
        (out/'cold.stdout').write_bytes(cold.stdout);(out/'cold.stderr').write_bytes(cold.stderr)
        require(cold.returncode==0 and parse(cold.stdout)['result']=='PASS','recovered cold replay differs')
        result={'stage':stage,'result':'PASS','child_exit_code':process.returncode,'committed_sequence_at_interruption':expected_sequence,
            'corrections':len(corrections),'exact_retry_idempotent':True,'original_committed_prefix_preserved':True,'wrong_head_recovery_rejected':True,
            'cold_signature_replay':True,'private_key_removed_before_child':True,'owned_store_removed':True,'duration_seconds':time.perf_counter()-start}
        emit(out/'result.json',result);rows.append(result)
    result={'result':'PASS','cases':rows,'actual_interrupted_processes':3,'fresh_cold_processes':3,'authority_effect':'none',
        'canonical_effects_applied':0,'source_effects_applied':0,'actual_owner_outcome':None,'private_keys_exported':False}
    emit(destination/'result.json',result);print(json.dumps(result,sort_keys=True));return result


if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='child':child(sys.argv[2],sys.argv[3],EnginePins(**parse(Path(sys.argv[4]).read_bytes())))
    else:
        require(len(sys.argv)==3,'usage: recovery.py fresh-evidence pins-json')
        run(sys.argv[1],EnginePins(**parse(Path(sys.argv[2]).read_bytes())))
