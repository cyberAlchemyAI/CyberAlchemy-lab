"""Deterministic owned races plus genuine concurrent child invocation."""
from contextlib import contextmanager
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch
from . import capture_io as C
from . import checks
from . import provisioning as P


def require(v,m): P.require(v,m)


def concurrency():
    root,plan,pin=checks.fixture('concurrent')
    first=subprocess.Popen(checks.command(root,pin,'interrupt-intent'),env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    deadline=time.monotonic()+45
    try:
        while not (root/'observer-ready.json').exists() and first.poll() is None and time.monotonic()<deadline:time.sleep(.05)
        require((root/'observer-ready.json').exists(),'first constructor did not reach locked intent')
        second=subprocess.run(checks.command(root,pin,'rehearse'),env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,text=True,timeout=20)
        require(second.returncode!=0 and 'controller operation already in progress' in second.stderr,'concurrent operation did not refuse at controller lock')
        require(not (root/'target/store').exists() and not (root/'channel/result-coldoperation').exists(),'busy caller caused target/result effect')
        first.kill();first.communicate(timeout=5);require(first.returncode==-9,'original writer was not interrupted')
        result=checks.child(root,pin,'reconcile',{'id':'coldoperation'})
        require(result['status']=='uncertain-retain-no-redispatch','cold reconcile after kernel lock release redispatched')
        return {'case':'kernel lock spans durable intent through original constructor/result','result':'PASS','first_exit':first.returncode,'concurrent_exit':second.returncode,'cold_reconcile':result['status'],'target_effect':False,'result_effect':False,'root':str(root),'plan_sha256':pin}
    finally:
        if first.poll() is None:first.kill();first.communicate(timeout=5)


def captures():
    cases=[]
    for kind in ['leaf','ancestor']:
        root=Path(tempfile.mkdtemp(prefix='cal-T34-capture-race-'));(root/'input').mkdir(mode=0o700)
        selected=root/'input/code.py';selected.write_bytes(b'VERIFIED=True\n');raw=selected.read_bytes();digest=P.sha(raw)
        old_read=os.read;done=False
        def observed_read(fd,size):
            nonlocal done
            blob=old_read(fd,size)
            if not done and blob:
                done=True
                if kind=='leaf':selected.rename(root/'input/retained.py');selected.symlink_to('/dev/null')
                else:(root/'input').rename(root/'retained-input');(root/'input').symlink_to(root/'retained-input',target_is_directory=True)
            return blob
        try:
            with patch.object(C.os,'read',observed_read):C.capture(selected,digest)
        except (ValueError,OSError):cases.append({'case':'same capture '+kind+' replacement','result':'PASS-refused','observer':'owned os.read observer after actual selected bytes','original_callback_changed':False})
        else:raise AssertionError('raced input accepted')
    root=Path(tempfile.mkdtemp(prefix='cal-T34-same-byte-'));path=root/'__init__.py';raw=b'captured_value="selected"\n';path.write_bytes(raw)
    selected=C.capture(path,P.sha(raw));path.write_bytes(b'raise RuntimeError("unselected software executed")\n')
    module=C.execute('_T34_same_byte_capture',path,selected,True)
    require(module.captured_value=='selected','loader executed reopened replacement bytes');sys.modules.pop(module.__name__)
    cases.append({'case':'same verified byte string executes after disk replacement','result':'PASS','executed_reopened_file':False})
    return cases


def replay_parent_race():
    root,plan,pin=checks.fixture('read-parent')
    c=P.Controller(plan,pin)
    try:
        channel=c.channel();channel.authenticate(checks.sign(c,channel.challenge));result=c.rehearsal(channel,'ownedread')
        require(result['store_created'],'owned constructor failed')
        # Changed absolute parent may contain an attractive same-byte store;
        # controller must reject parent attachment before reading any leaf.
        (root/'target').rename(root/'retained-target');(root/'target').mkdir(mode=0o700)
        calls=[];original_open=os.open
        def observed_open(path,*args,**kwargs):
            if str(path) in {'config.json','baseline.json','HEAD.json','0000000000.json'}:calls.append(str(path))
            return original_open(path,*args,**kwargs)
        try:
            with patch.object(P.os,'open',observed_open):
                with c.captured_target(result['store_pins']):raise AssertionError('replacement parent capture accepted')
        except (ValueError,OSError):pass
        else:raise AssertionError('parent replacement not refused')
        require(calls==[],'store leaf read before selected-parent attachment refusal')
        return {'case':'replaced absolute parent refuses before store leaf read','result':'PASS','leaf_reads':calls,'foreign_parent_empty':list((root/'target').iterdir())==[],'original_target_retained':(root/'retained-target/store/HEAD.json').exists(),'root':str(root)}
    finally:c.close()


def original_callbacks():
    original=P.ORIGINAL/'loader.py';revised=Path(P.__file__).parent/'engine_capture.py'
    def method(path,name):
        tree=ast.parse(path.read_bytes());klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LoadedEngine')
        return ast.dump(next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
    require(method(original,'replay_owned')==method(revised,'replay_owned'),'original replay callback changed')
    return {'case':'unchanged original replay_owned AST and Store source identity','result':'PASS','replay_ast_unchanged':True,'Store_source_sha256':P.sha((P.ORIGINAL/'runtime/lab_runtime/store.py').read_bytes()),'loader_adapter_origin':str(revised.relative_to(P.ROOT))}



def lock_replacement():
    root,plan,pin=checks.fixture('lock-replace')
    c=P.Controller(plan,pin)
    try:
        with c.locked():
            selected=c.lock_identity
            (root/'channel/controller-lock').rename(root/'retained-controller-lock')
            checks.write(root/'channel/controller-lock',b'lab-T34-controller-lock/v2-candidate\n')
            require(P.identity((root/'channel/controller-lock').stat())!=selected,'fixture replacement retained inode')
            try:c.guard()
            except ValueError as error:require('lock attachment changed' in str(error),'wrong replacement refusal')
            else:raise AssertionError('replaced active lock accepted')
    except ValueError as error:require('controller lock changed during operation' in str(error),'lock exit failed for another reason')
    finally:c.close()
    return {'case':'replaced live controller lock inode refuses at guard and exit','result':'PASS-refused','old_lock_retained':(root/'retained-controller-lock').is_file(),'target_effect':(root/'target/store').exists(),'root':str(root)}


def cached_modules():
    cases=[]
    for name in ['checks','qualify','provisioning','capture_io','engine_capture','revision_checks','startup']:
        cmd=checks.command(Path('/tmp/cal-T34-cached-module-no-constructor'),'0'*64,'rehearse')
        injection="import types;m=types.ModuleType("+repr(name)+");m.__file__='/unselected/owned-review-placeholder.py';m.worker=lambda *a:print('UNSELECTED-CACHED-WORKER-EXECUTED');sys.modules["+repr(name)+"]=m;"
        replacement=injection+"\ntry:ns['main'](*sys.argv[1:])\nexcept ValueError as e:\n assert 'unselected preexisting component cache:' in str(e) and "+repr(name)+" in str(e);print('EXPECTED-CACHED-MODULE-REFUSAL')\nelse:raise AssertionError('cached module accepted')"
        cmd[11]=cmd[11].replace("ns['main'](*sys.argv[1:])",replacement)
        process=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,text=True,timeout=25)
        require(process.returncode==0 and 'EXPECTED-CACHED-MODULE-REFUSAL' in process.stdout and 'UNSELECTED-CACHED-WORKER-EXECUTED' not in process.stdout,'unselected cached module ran or wrong refusal: '+name)
        cases.append({'case':'unselected preexisting absolute module '+name,'result':'PASS-refused','terminal_exit':process.returncode,'unselected_callback_executed':False,'runtime_constructor_executed':False})
    return cases

def main(name):
    evidence={'schema_version':'lab-T34-revision-race-checks/v2-candidate','checks':[concurrency(),*captures(),replay_parent_race(),original_callbacks(),lock_replacement(),*cached_modules()],'result':'PASS','authority_effect':'none','task_complete':False}
    checks.write(checks.RUN/name,json.dumps(evidence,indent=2,sort_keys=True).encode()+b'\n');print(json.dumps({'revision_checks':len(evidence['checks']),'result':'PASS'}))
