"""Actual nonce channel and OS flock expiry at the private claim boundary."""
from datetime import timedelta
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v6'
SOURCE='7ab054776a5fa8fd310f60e126a29c98686d159f989fb3a721cb6dcd1f1f119f'
PROFILE='d832f9c20e487261d9987906408dfbd54c7f6cf624890f9144d750d7eb8a053f'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    report=RUN/'Deadline-before-claim-0148.json'
    assert not report.exists()
    name='_cal_actual_claim_boundary_0148'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    G=__import__(name+'.guard',fromlist=['*'])
    P=__import__(name+'.protocol',fromlist=['*'])
    A=__import__(name+'.auth',fromlist=['*'])
    F=__import__(name+'.fixtures',fromlist=['*'])
    W=__import__(name+'.workspace',fromlist=['*'])
    checks=[];failure=None;channel=None;fixture=None;elapsed=None
    try:
        G.verify(SOURCE)
        schemas=P.Schemas(PROFILE)
        with tempfile.TemporaryDirectory(prefix='cal-actual-claim-deadline-0148-') as rawroot:
            fixture=Path(rawroot);fixture.chmod(0o700)
            key,policy,pin=F.provision(fixture)
            channel=A.ReaderChannel(policy,pin,schemas)
            channel.authenticate(F.proof(key,channel.challenge))
            vault=W.Vault(channel)
            checks.append({'check':'actual-independent-private-custody-and-signed-nonce','result':'PASS'})
            call=F.call(channel.context,'lab.status')
            call['operation']='change.prepare';call['idempotency_key']='actual:guarded-claim-deadline:0148'
            raw=P.compact(call)
            ready=threading.Event();release=threading.Event();holder_error=[]
            def holder():
                fd=None
                try:
                    fd=os.open(vault.root/'.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
                    fcntl.flock(fd,fcntl.LOCK_EX);ready.set()
                    release.wait(timeout=30)
                except BaseException:holder_error.append(traceback.format_exc());ready.set()
                finally:
                    if fd is not None:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
            thread=threading.Thread(target=holder);thread.start()
            assert ready.wait(timeout=10) and not holder_error
            deadline=A.now()+timedelta(seconds=5)
            timer=threading.Timer(20,release.set);timer.start()
            started=time.monotonic()
            try:
                try:vault.claim(call,raw,channel.context,deadline=deadline)
                except W.DeadlineBeforeClaim:pass
                else:raise AssertionError('expired guarded claim unexpectedly allocated')
            finally:
                elapsed=time.monotonic()-started;release.set();timer.cancel();thread.join(timeout=10)
            assert not thread.is_alive() and not holder_error
            assert A.now()>=deadline
            assert not list((vault.root/'objects').iterdir()) and not list((vault.root/'journal').iterdir())
            checks.append({'check':'actual-OS-lock-and-real-expiry-refuse-before-object-or-journal-write','result':'PASS','elapsed_seconds':elapsed,'lock_hold_seconds':20,'deadline_seconds':5})
            ns,fp,claim,result,created=vault.claim(call,raw,channel.context,deadline=A.now()+timedelta(minutes=10))
            assert created and result is None and claim['fingerprint']==fp
            before={p.name:p.read_bytes() for p in (vault.root/'journal').iterdir()}
            objects={p.name:p.read_bytes() for p in (vault.root/'objects').iterdir()}
            retry=vault.claim(call,raw,channel.context,deadline=A.now()+timedelta(minutes=10))
            assert retry[0]==ns and retry[2]==claim and not retry[4]
            assert before=={p.name:p.read_bytes() for p in (vault.root/'journal').iterdir()}
            assert objects=={p.name:p.read_bytes() for p in (vault.root/'objects').iterdir()}
            checks.append({'check':'unexpired-real-claim-and-exact-retry-no-second-write','result':'PASS'})
            channel.dispose();channel=None
        assert not fixture.exists()
        G.verify(SOURCE)
        checks.append({'check':'full-candidate-source-guard-and-owned-fixture-removal','result':'PASS'})
    except BaseException:failure=traceback.format_exc()
    finally:
        if channel is not None:channel.dispose()
    value={'schema_version':'lab-real-claim-deadline-qualification/v1-candidate','result':'PASS' if failure is None else 'FAIL','checks':checks,'failure':failure,
        'files':[binding(p) for p in [API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
        'owned_fixture_removed':fixture is not None and not fixture.exists(),'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False,'task_complete':False,
        'claim_ceiling':'Internal private Vault claim boundary on an actual authenticated channel only; no public domain dispatch, whole API, Session performance, pilot or owner approval.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'checks':len(checks),'report':binding(report)}),flush=True)
    return 0 if failure is None else 1
if __name__=='__main__':raise SystemExit(main())
