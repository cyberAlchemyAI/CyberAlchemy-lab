"""Independent pins, unknown journal/lock, invalid native events, writer exclusion."""
from dataclasses import replace
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from fixtures import call
from recoverable_store import GenerationStore,sha,read

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32'

def fail(function,message=None):
    try:function()
    except (ValueError,OSError) as error:
        if message:assert message in str(error),str(error)
        return {'error_type':type(error).__name__,'message':str(error)}
    raise AssertionError('expected refusal')

def main():
    parent=HERE/'control-episodes-0001';parent.mkdir(mode=0o700)
    executable=HERE/'bin-production/lab-ontology-native';pin=sha(executable.read_bytes());base=HERE/'wrapper-baseline-fixture-0004/sealed-events.json';request=HERE/'wrapper-successor-fixture-0004/sealed-events.json';results=[]
    for kind in ['wrong-pending-pin','unknown-publication','unknown-writer-lock','wrong-root-identity','unsealed-request','invalid-native-event','concurrent-writer']:
        root=parent/kind;root.mkdir(mode=0o700);s=root.stat();store=GenerationStore(root,(s.st_dev,s.st_ino),executable,pin);store.bootstrap();pending,base_pins=store.prepare(base,sha(base.read_bytes()));store.run(pending,base_pins);before=read(root/'HEAD.json')
        pending,pins=store.prepare(request,sha(request.read_bytes()));value=json.loads(pending.read_bytes())
        if kind=='wrong-pending-pin':result=fail(lambda:store.run(pending,replace(pins,pending_sha256='0'*64)),'independent pending digest differs')
        elif kind=='unknown-publication':
            path=root/('publication-'+value['operation']+'.json');path.write_bytes(b'{"foreign_owner":"retain exact foreign controls"}')
            result=fail(lambda:store.run(pending,pins,recover=True),'unknown publication controls');assert path.read_bytes()==b'{"foreign_owner":"retain exact foreign controls"}'
        elif kind=='unknown-writer-lock':
            path=root/'writer.lock';path.write_bytes(b'foreign lock bytes');result=fail(lambda:store.run(pending,pins),'unknown writer lock bytes');assert path.read_bytes()==b'foreign lock bytes'
        elif kind=='wrong-root-identity':result=fail(lambda:GenerationStore(root,(s.st_dev,s.st_ino+1),executable,pin),'owned store identity/mode changed')
        elif kind=='unsealed-request':
            path=root/'unsealed-request.json';v=json.loads(request.read_bytes());v['semantic'][0]['event_digest']='0'*64;path.write_text(json.dumps(v));result=fail(lambda:store.prepare(path,sha(path.read_bytes())),'request events were not already exactly sealed')
        elif kind=='invalid-native-event':
            path=root/'native-invalid-drafts.json';v=json.loads(request.read_bytes());v['semantic'][0]['complete_resulting_semantic_state']['label']='';path.write_text(json.dumps(v));sealed=call(executable,'seal',path);assert sealed.returncode==0
            path=root/'native-invalid-sealed.json';path.write_bytes(sealed.stdout);bad_pending,bad_pins=store.prepare(path,sha(path.read_bytes()));result=fail(lambda:store.run(bad_pending,bad_pins),'NONEMPTY_STRING_REQUIRED');bad=json.loads(bad_pending.read_bytes());assert not (root/bad['stage']/'semantic/.append.lock').exists()
        else:
            marker=root/'writer-live.marker';code="import fcntl,sys,time;from pathlib import Path;f=open(sys.argv[1],'r+b');fcntl.flock(f,fcntl.LOCK_EX);Path(sys.argv[2]).write_bytes(b'actual writer lock held');time.sleep(30)"
            child=subprocess.Popen([sys.executable,'-I','-B','-c',code,str(root/'writer.lock'),str(marker)],start_new_session=True)
            try:
                deadline=time.monotonic()+10
                while not marker.exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(0.01)
                assert marker.exists() and child.poll() is None
                result=fail(lambda:store.run(pending,pins));assert result['error_type']=='BlockingIOError'
            finally:
                if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
                child.wait(timeout=10)
        assert read(root/'HEAD.json')==before and len(store.read_committed()['native_cut']['semantic_events'])==3
        results.append({'case':kind,'result':'PASS','refusal':result,'committed_head_unchanged':True,'cold_original_native_read_unchanged':True})
    report={'result':'PASS','cases':results,'tests':len(results),'authority_effect':'none','task_complete':False};(RUN/'control-tests-0001.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':'PASS','control_cases':len(results)}));return 0

if __name__=='__main__':raise SystemExit(main())
