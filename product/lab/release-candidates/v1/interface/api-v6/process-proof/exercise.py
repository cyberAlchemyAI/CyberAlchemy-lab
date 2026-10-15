"""Original wire stdio, cold idempotency and actual post-claim process interruptions."""
from contextlib import ExitStack
import base64
import copy
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from example_fixture import *
from service import *

OUTPUT=BASE/'receipts/processes/0001'
checks=[];children=[];transcripts={}

def check(name,value):
    checks.append({'test':name,'result':'PASS' if value else 'FAIL'})
    source.require(value,name)

class Child:
    def __init__(self,name,key,policy,pin):
        self.name=name;self.frames=[]
        self.stderr=OUTPUT/(name+'.stderr');self.error=self.stderr.open('xb')
        self.p=subprocess.Popen([sys.executable,str(BASE/'serve.py'),'--policy',str(policy),'--policy-sha256',pin,
            '--protocol-profile-sha256',source.sha((BASE/'contract-profile.json').read_bytes())],cwd=BASE,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.error)
        self.selection=selectors.DefaultSelector();self.selection.register(self.p.stdout,selectors.EVENT_READ)
        challenge=self.receive();self.send(proof(key,challenge));self.auth=self.receive()
        check(name+': actual cryptographic authentication',self.auth['schema_version']=='lab-local-reader-authenticated/v1-candidate')
        self.context=self.auth['context']
    def send(self,raw):
        self.frames.append({'direction':'request','base64_original_bytes':base64.b64encode(raw).decode(),'sha256':source.sha(raw)})
        self.p.stdin.write(raw+b'\n');self.p.stdin.flush()
    def receive(self):
        source.require(self.selection.select(timeout=55),'bounded child response timed out')
        raw=self.p.stdout.readline().removesuffix(b'\n');source.require(raw,'child closed without complete JSON response')
        self.frames.append({'direction':'response','base64_original_bytes':base64.b64encode(raw).decode(),'sha256':source.sha(raw)})
        return frame_parse(raw)
    def invoke(self,c):self.send(compact(c));return self.receive()
    def stop(self,kill=False):
        if kill:self.p.kill()
        else:self.p.stdin.close()
        code=self.p.wait(timeout=55);self.error.close();self.selection.close()
        self.p.stdout.close()
        if kill:self.p.stdin.close()
        children.append({'name':self.name,'pid':self.p.pid,'exit_code':code,'terminal':True,'intentional_interruption':kill})
        raw=source.encoded({'schema_version':'lab-original-wire-transcript/v1-candidate','frames':self.frames,'authority_effect':'none'})
        (OUTPUT/(self.name+'.json')).write_bytes(raw);transcripts[self.name]=source.bind(OUTPUT/(self.name+'.json'))
        check(self.name+': terminal process observed',code==-signal.SIGKILL if kill else code==0)

def proposal_for(child,view,policy,target,operation='change.prepare',key='fixture:prepare'):
    pv=source.parse(policy.read_bytes());manifest=source.parse((Path(pv['workspace']['root'])/'workspace.json').read_bytes())
    fake=SimpleNamespace(channel=SimpleNamespace(context=child.context),handlers=SimpleNamespace(view=view),
        vault=SimpleNamespace(control_binding={'ref':'workspace:'+manifest['workspace_ref'],'sha256':pv['workspace']['manifest_sha256']}))
    return candidate_call(fake,target,operation,key)

def inspected(child,key='fixture:prepare'):
    c=call(child.context,'operation.inspect',None,lookup={'operation':'change.prepare','idempotency_key':key});return child.invoke(c)

def main():
    source.require(not OUTPUT.exists(),'fresh selected process evidence output required');OUTPUT.mkdir(parents=True)
    result={'schema_version':'lab-R03-preparation-process-proof/v1-candidate','result':'FAIL','task_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'active_Sessions_created':0,'private_keys_exported':False,'Session_memory_exported':False}
    owned=[];open_children=[]
    try:
        with ExitStack() as stack:
            view=stack.enter_context(source.replay_source('reference-corrected'));materials,metadata,target=materials_for(view)
            root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-preparation-wire-')));owned.append(str(root))
            key,policy,pin=provision(root,'reference-corrected',materials,metadata)
            warm=Child('warm',key,policy,pin);open_children.append(warm)
            c=proposal_for(warm,view,policy,target);review=warm.invoke(c)
            check('actual change.prepare exact schema and blocked admission',review['kind']=='result' and review['message']['posture']=='blocked')
            validation=warm.invoke(proposal_for(warm,view,policy,target,'change.validate','validate:actual'))
            check('actual semantic reference gaps retained',validation['message']['result']=='not-evaluable' and bool(validation['message']['reference_checks']))
            observed=inspected(warm);check('actual completed operation inspection',observed['message']['posture']=='completed' and observed['message']['result_binding'] is not None)
            warm.stop();open_children.remove(warm)
            cold=Child('cold-retry',key,policy,pin);open_children.append(cold)
            retry=copy.deepcopy(c);retry['call_id']='call:cold-retry';retry['caller_context_ref']=cold.context['context_ref'];retry['deadline']=call(cold.context,'lab.status')['deadline']
            same=cold.invoke(retry);check('cold identical outcome without candidate redispatch',same['kind']=='result' and same['message']==review['message'])
            cold_observed=inspected(cold);check('cold durable exact result and original call binding',cold_observed['message']['result_binding']==observed['message']['result_binding']
                and cold_observed['message']['original_call_binding']==observed['message']['original_call_binding'])
            conflict=copy.deepcopy(retry);conflict['call_id']='call:conflict';conflict['message']['proposal_ref']='proposal:changed-cold'
            denied=cold.invoke(conflict);check('cold changed material conflict',denied['message']['code']=='idempotency-conflict')
            cold.stop();open_children.remove(cold)
            for stage in ('claim','evidence'):
                ownedroot=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-interruption-'+stage+'-')));owned.append(str(ownedroot))
                key2,p2,pin2=provision(ownedroot,'reference-corrected',materials,metadata)
                worker=Child('interrupted-'+stage,key2,p2,pin2);open_children.append(worker)
                request=proposal_for(worker,view,p2,target);worker.send(compact(request))
                deadline=time.monotonic()+55;found=False
                while time.monotonic()<deadline:
                    if stage=='claim':found=bool(list((ownedroot/'workspace/journal').glob('*.claim.json')))
                    else:
                        found=any(source.parse(p.read_bytes()).get('schema_version')=='lab-validation-report/v1-candidate' for p in (ownedroot/'workspace/objects').glob('*.json'))
                    if found:break
                    source.require(worker.p.poll() is None,'producer exited before observed interruption stage');time.sleep(0.001)
                check('real '+stage+' stage observed before kill',found)
                worker.stop(kill=True);open_children.remove(worker)
                recovery=Child('inspect-after-'+stage,key2,p2,pin2);open_children.append(recovery)
                inspect=inspected(recovery)
                check(stage+': verified incomplete result remains indeterminate',inspect['kind']=='result' and inspect['message']['posture']=='indeterminate'
                    and inspect['message']['reconciliation_required'] and not inspect['message']['retry_allowed'])
                attempted=copy.deepcopy(request);attempted['call_id']='call:after-kill';attempted['caller_context_ref']=recovery.context['context_ref']
                attempted['deadline']=call(recovery.context,'lab.status')['deadline']
                blocked=recovery.invoke(attempted)
                check(stage+': no blind retry after actual process interruption',blocked['message']['code']=='recovery-required')
                recovery.stop();open_children.remove(recovery)
            otherroot=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-other-principal-')));owned.append(str(otherroot))
            key3,p3,pin3=provision(otherroot,'reference-corrected',materials,metadata,principal='principal:independent-other')
            other=Child('other-principal',key3,p3,pin3);open_children.append(other)
            notfound=inspected(other);check('actual other principal cannot enumerate prior operation',notfound['message']['code']=='not-found')
            other.stop();open_children.remove(other)
        check('all owned fixture roots and private keys removed',all(not Path(p).exists() for p in owned))
        result['result']='PASS';result['owned_fixture_roots_removed']=True
    except Exception as error:
        result['failure']=str(error)
        for child in open_children:
            try:child.stop(kill=True)
            except Exception:pass
    result['checks']=checks;result['children']=children;result['transcript_bindings']=list(transcripts.values())
    result['producer_binding']=source.bind(Path(__file__).resolve());result['profile_binding']=source.bind(BASE/'contract-profile.json')
    (OUTPUT/'result.json').write_bytes(source.encoded(result))
    print(json.dumps({'result':result['result'],'checks':len(checks),'children':len(children),'failure':result.get('failure')}))
    return 0 if result['result']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
