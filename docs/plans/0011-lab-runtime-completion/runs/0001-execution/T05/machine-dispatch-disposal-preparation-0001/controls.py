"""Inert dispatcher ordering controls; no real Machine, policy or API service."""
from datetime import datetime,timedelta,timezone
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import types
import uuid

HERE=Path(__file__).absolute().parent
def load(path):
    name='_cal_T05_inert_dispatch_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def transport(code,raw):
    return {'inert_transport':code,'raw':raw}

class InertService:
    def __init__(self):self.calls=0;self.check=None
    def call(self,raw):
        self.calls+=1
        if self.check is not None:self.check()
        return {'inert_original_dispatch':raw}

def fixture():
    expiry=datetime.now(timezone.utc)+timedelta(minutes=2)
    service=InertService()
    p=types.SimpleNamespace(closed=False,context={'inert':True},service=service,
        resource=types.SimpleNamespace(closed=False,expires=expiry),expires=expiry,
        A=types.SimpleNamespace(now=lambda:datetime.now(timezone.utc)),
        _state_lock=threading.RLock(),Service=InertService)
    p.guard=lambda:dict(p.context) if p.context is not None else None
    return p,service

def dispose(p):
    with p._state_lock:
        p.closed=True;p.context=None;p.service=None

def main():
    old=load(HERE/'original-machine_transport.py')
    new=load(HERE/'postimages/machine_transport.py')
    checks=[];fd0=len(os.listdir('/proc/self/fd'));raw=b'OWNED INERT CALL'
    p,s=fixture();p.guard=lambda:dispose(p)
    try:old.MachinePeer.call(p,raw)
    except ValueError as error:assert str(error)=='Machine dispatcher unavailable'
    else:raise AssertionError('original availability race was not reproduced')
    assert s.calls==0
    checks.append('original guard-return plus disposed dispatcher reproduces observed ValueError branch')
    p,s=fixture();p.guard=lambda:dispose(p)
    assert new.MachinePeer.call(p,raw)==transport('unauthenticated-channel',raw) and s.calls==0
    checks.append('disposal during original guard produces existing refusal and no dispatch')
    p,s=fixture();assert new.MachinePeer.call(p,raw)=={'inert_original_dispatch':raw} and s.calls==1
    checks.append('live dispatcher is called exactly once')
    def fail():raise ValueError('owned inert guard refusal')
    p,s=fixture();p.guard=fail
    assert new.MachinePeer.call(p,raw)==transport('unauthenticated-channel',raw) and s.calls==0
    checks.append('original guard failure remains existing refusal')
    for name in ('closed','resource-closed','context-removed','dispatcher-removed','expired'):
        p,s=fixture()
        if name=='closed':p.closed=True
        elif name=='resource-closed':p.resource.closed=True
        elif name=='context-removed':p.context=None
        elif name=='dispatcher-removed':p.service=None
        else:p.expires=datetime.now(timezone.utc)-timedelta(seconds=1)
        assert new.MachinePeer.call(p,raw)==transport('unauthenticated-channel',raw) and s.calls==0
        checks.append(name+' refuses before dispatcher snapshot')
    p,s=fixture();guard_returned=threading.Event();results=[];errors=[]
    p.guard=lambda:guard_returned.set()
    def run():
        try:results.append(new.MachinePeer.call(p,raw))
        except BaseException as error:errors.append(type(error).__name__)
    with p._state_lock:
        worker=threading.Thread(target=run);worker.start()
        assert guard_returned.wait(2)
        dispose(p)
    worker.join(2)
    assert not worker.is_alive() and not errors and results==[transport('unauthenticated-channel',raw)] and s.calls==0
    checks.append('controlled real thread disposal between guard and snapshot refuses without a leaked exception')
    p,s=fixture();s.check=lambda:dispose(p)
    assert new.MachinePeer.call(p,raw)=={'inert_original_dispatch':raw} and p.service is None and s.calls==1
    checks.append('local dispatcher reference survives later field disposal without dereferencing cleared state')
    p,s=fixture()
    def unlocked():
        observed=[]
        def acquire():
            got=p._state_lock.acquire(timeout=1);observed.append(got)
            if got:p._state_lock.release()
        thread=threading.Thread(target=acquire);thread.start();thread.join(2)
        assert not thread.is_alive() and observed==[True]
    s.check=unlocked
    assert new.MachinePeer.call(p,raw)=={'inert_original_dispatch':raw}
    checks.append('state lock is released before original Service/resource callbacks')
    assert len(os.listdir('/proc/self/fd'))==fd0
    print(json.dumps({'result':'PASS-inert-dispatch-ordering-only','checks':checks,'checks_count':len(checks),
        'FD_delta':0,'actual_Machine_Service_policy_Source_or_Session_constructed':False,
        'actual_expiry_timer_or_full14_runtime_qualified':False,'real_clock_used_for_inert_expiry_case':True,
        'authority_effect':'none'},sort_keys=True))

if __name__=='__main__':main()
