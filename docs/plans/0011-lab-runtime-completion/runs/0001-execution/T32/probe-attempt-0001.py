"""Real child SIGKILL through full public native append and original cold read."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from fixtures import sealed_fixture,call

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def snapshot(directory):
    rows={}
    for family in ['semantic','governance']:
        for p in sorted((directory/family).iterdir()):
            assert p.is_file() and not p.is_symlink()
            raw=p.read_bytes();s=p.stat();rows[family+'/'+p.name]={'sha256':sha(raw),'size_bytes':len(raw),'inode':s.st_ino,'link_count':s.st_nlink}
    return rows

def main():
    production=HERE/'bin-production/lab-ontology-native';observer=HERE/'build-observer/debug/lab-ontology-native'
    assert production.is_file() and observer.is_file() and sha(production.read_bytes())!=sha(observer.read_bytes()),'observer must be separately built/pinned'
    events,value=sealed_fixture(production,HERE/'technical-fixtures-0001')
    episodes=HERE/'episodes-0001';episodes.mkdir(mode=0o700);results=[]
    baseline=episodes/'uninterrupted';baseline.mkdir(mode=0o700)
    for family in ['semantic','governance']:(baseline/family).mkdir()
    p=call(production,'append',baseline/'semantic',baseline/'governance',events);assert p.returncode==0,p.stderr
    p=call(production,'read',baseline/'semantic',baseline/'governance',3);assert p.returncode==0,p.stderr
    cold=json.loads(p.stdout);assert cold['semantic_events']==value['semantic'] and cold['governance_events']==value['governance'] and cold['checkpoint_parity']=='PASS'
    (RUN/'uninterrupted-native-original.json').write_text(json.dumps({'result':'PASS','production_executable_sha256':sha(production.read_bytes()),'exact_events':True,'checkpoint_parity':True,'semantic_events':3,'governance_events':3,'cold_stdout_sha256':sha(p.stdout)},indent=2)+'\n')
    for family in ['semantic','governance']:
        for stage in ['after-lock','after-first-link','before-cleanup']:
            case=episodes/(family+'-'+stage);case.mkdir(mode=0o700)
            for f in ['semantic','governance']:(case/f).mkdir()
            foreign=case/'foreign-retain.bin';foreign.write_bytes(b'foreign sibling must remain exact')
            marker=case/'observed.marker';env={'PATH':'/usr/bin:/bin','LC_ALL':'C','CAL_T32_STOP_STAGE':stage,'CAL_T32_STOP_FAMILY':family,'CAL_T32_MARKER':str(marker)}
            process=subprocess.Popen([str(observer),'append',str(case/'semantic'),str(case/'governance'),str(events)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
            deadline=time.monotonic()+30
            while not marker.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(0.01)
            if not marker.exists():
                if process.poll() is None:process.kill()
                out,err=process.communicate();raise RuntimeError('observer checkpoint absent: '+err.decode())
            assert marker.read_bytes()==stage.encode() and process.poll() is None
            pid=process.pid;before=snapshot(case);process.send_signal(signal.SIGKILL);out,err=process.communicate(timeout=10)
            assert process.returncode==-signal.SIGKILL
            after=snapshot(case);assert before==after and foreign.read_bytes()==b'foreign sibling must remain exact'
            replay=call(production,'read',case/'semantic',case/'governance',3)
            assert replay.returncode==1 and b'APPEND_IN_PROGRESS' in replay.stderr
            assert snapshot(case)==after and foreign.read_bytes()==b'foreign sibling must remain exact'
            record={'family':family,'checkpoint':stage,'child_pid':pid,'real_sigkill':True,'child_exit_code':process.returncode,'checkpoint_marker':str(marker),'observer_executable_sha256':sha(observer.read_bytes()),'production_cold_read_executable_sha256':sha(production.read_bytes()),'before_kill':before,'after_kill':after,'original_cold_read_exit_code':replay.returncode,'original_cold_read_error':replay.stderr.decode(),'original_cold_read_refuses_partial_history':True,'cold_recovery_available_in_original':False,'foreign_sibling_preserved':True,'observer_changes_stripped_restore_production_source':True,'authority_effect':'none'}
            (RUN/(family+'-'+stage+'.json')).write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');results.append(record)
    foreign=episodes/'foreign-lock';foreign.mkdir(mode=0o700)
    for family in ['semantic','governance']:(foreign/family).mkdir()
    lock=foreign/'semantic/.append.lock';lock.write_bytes(b'foreign-owner-never-delete')
    p=call(production,'append',foreign/'semantic',foreign/'governance',events)
    assert p.returncode==1 and lock.read_bytes()==b'foreign-owner-never-delete'
    result={'result':'PASS-OBSERVATIONS','actual_interruption_cases':len(results),'original_direct_batch_recovery':'MISSING','original_reader_partial_history_guard':'PASS','foreign_lock_preservation':'PASS','persisted_batch_atomic_visibility_proven':False,'observed_exact_gap':'Real interrupted child leaves empty sentinel and zero/partial/full linked events; fresh original reader refuses APPEND_IN_PROGRESS. Original API has no crash reconciliation entrypoint. Separate publisher commit protocols do not wrap these direct append calls.','production_executable_sha256':sha(production.read_bytes()),'observer_executable_sha256':sha(observer.read_bytes()),'authority_effect':'none','task_complete':False}
    (RUN/'original-interruption-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return 0

if __name__=='__main__':raise SystemExit(main())
