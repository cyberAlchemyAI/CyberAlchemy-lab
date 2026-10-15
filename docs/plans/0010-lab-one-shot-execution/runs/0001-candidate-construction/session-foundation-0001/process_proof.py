"""Observe actual consumer SIGKILL, cold metadata, disposal and fresh identity."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
PACKAGE=ROOT/'implementation/lab-continuity/candidates/v2'
sys.path.insert(0,str(PACKAGE))
os.environ['R03_GENERATOR_SHA']='4dd5907dc1269e2b0f15a217cd1e60a277554b69889ea76f1e2e571e3fd3010e'
from test_foundation import *


def main():
    checks=[];children=[];frames=[];live=[]
    def check(value,name):
        require(value,name);checks.append({'test':name,'result':'PASS'})
    def receive(process):
        selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
        try:
            require(selector.select(timeout=60),'actual child frame deadline')
            line=process.stdout.readline();require(line,'actual child stream ended without reply')
            value=json.loads(line);frames.append(value);return value
        finally:selector.close()
    def start(control,name):
        p=subprocess.Popen([sys.executable,str(HERE/'child.py'),str(control)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        live.append(p);value=receive(p)
        check(value['kind']=='ready' and value['pid']==p.pid,name+': actual child ready')
        return p
    def request(p,**value):
        p.stdin.write(json.dumps(value)+'\n');p.stdin.flush();return receive(p)
    def stop(p,name,kill=False):
        if kill:p.kill()
        else:
            p.stdin.write('{"operation":"stop"}\n');p.stdin.flush()
        code=p.wait(timeout=60);err=p.stderr.read()
        check(code==(-9 if kill else 0),name+': actual terminal exit')
        check(not err,name+': no unexpected child diagnostic')
        children.append({'name':name,'pid':p.pid,'exit_code':code,'actual_SIGKILL':kill});live.remove(p)
        p.stdin.close();p.stdout.close();p.stderr.close()
    try:
        with TemporaryDirectory(prefix='cal-R03-real-custody-process-') as tmp:
            root=Path(tmp);store,snapshot,native=setup(root);(root/'custody').mkdir(mode=0o700)
            control=root/'control.json';control.write_bytes(encoded({'root':str(root),'store_pins':asdict(store.pins),'snapshot':snapshot,
                'native_request':native.request,'native_pins':asdict(native.pins)}));control.chmod(0o600)
            before={p.relative_to(store.path).as_posix():byte_digest(regular(p)) for p in store.path.rglob('*') if p.is_file()}
            first=start(control,'live-before-kill');opened=request(first,operation='open',key='killed-consumer')
            check(opened['kind']=='result' and opened['result']['posture']=='active','actual warm current consumer')
            old=opened['result'];token='R03 private killed-process RAM '+os.urandom(16).hex()
            note=request(first,operation='note',session_ref=old['session_ref'],text=token)
            check(note['kind']=='result' and note['result']['persisted'] is False,'actual private RAM note accepted')
            check(all(token.encode() not in regular(p) for p in (root/'custody').iterdir()),'actual RAM note excluded from custody files')
            stop(first,'live-before-kill',kill=True)
            cold=start(control,'cold-after-kill');inspected=request(cold,operation='inspect',session_ref=old['session_ref'])
            check(inspected['kind']=='result' and inspected['result']['posture']=='indeterminate','cold lost consumer remains indeterminate')
            check(inspected['result']['disposal_observed'] is False and inspected['result']['ended_at'] is None,'cold absence is not asserted disposal')
            replay=request(cold,operation='open',key='killed-consumer')
            check(replay['kind']=='result' and replay['result']['posture']=='indeterminate' and replay['result']['session_ref']==old['session_ref'],'same key never resumes or recreates killed consumer')
            denied=request(cold,operation='close',session_ref=old['session_ref'],expected_binding=old['metadata_binding'])
            check(denied['kind']=='error' and 'indeterminate' in denied['reason'],'cold close cannot invent observed disposal')
            new=request(cold,operation='open',key='new-current-consumer')
            check(new['kind']=='result' and new['result']['posture']=='active','new key creates actual current consumer')
            fresh=new['result']
            check(fresh['agent_instance_ref']!=old['agent_instance_ref'] and fresh['session_ref']!=old['session_ref'],'fresh Session and Machine identities after actual kill')
            closed=request(cold,operation='close',session_ref=fresh['session_ref'],expected_binding=fresh['metadata_binding'])
            check(closed['kind']=='result' and closed['result']['posture']=='closed' and closed['result']['disposal_observed'] is True,'actual explicit disposal receipt')
            stop(cold,'cold-after-kill')
            final=start(control,'cold-after-verified-close');observed=request(final,operation='inspect',session_ref=fresh['session_ref'])
            check(observed['kind']=='result' and observed['result']['posture']=='closed' and observed['result']['disposal_observed'] is True,'cold exact verified disposal retained')
            never=request(final,operation='open',key='new-current-consumer')
            check(never['kind']=='result' and never['result']['posture']=='closed','closed key does not reactivate a consumer')
            stop(final,'cold-after-verified-close')
            after={p.relative_to(store.path).as_posix():byte_digest(regular(p)) for p in store.path.rglob('*') if p.is_file()}
            check(before==after,'actual signed source bytes unchanged')
            metadata={p.name:json.loads(regular(p)) for p in (root/'custody').iterdir() if p.name!='.custody-lock'}
            check(token not in json.dumps(metadata) and token not in json.dumps(frames),'private note excluded from all retained evidence')
        check(not root.exists(),'all owned source, control and custody roots removed')
        value={'schema_version':'lab-read-custody-process-observation/v1-candidate','result':'PASS','checks':checks,'children':children,
            'frames':frames,'metadata':metadata,'actual_process_interruptions':1,'API_calls_executed':0,
            'authority_effect':'none','actual_owner_outcome':None,'owned_fixture_roots_removed':True,'Session_memory_exported':False}
        output=HERE/'process-result.json';require(not output.exists(),'process evidence already exists')
        output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'result':'PASS','checks':len(checks),'children':len(children),'actual_process_interruptions':1}),flush=True)
    finally:
        for p in live:
            p.kill();p.wait(timeout=60)
            p.stdin.close();p.stdout.close();p.stderr.close()

if __name__=='__main__':main()
