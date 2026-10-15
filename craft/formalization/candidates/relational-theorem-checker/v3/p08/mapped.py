"""Process-local issuance for separately named, freshly checked mapped contexts."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import time
import uuid
from ..p03.context import BASE,C,binding,check,require
from ..p06.supervisor import Supervisor
from .metadata import HERE,immutable

class MappedQualifier:
    def __init__(self,policy,sources):
        self.policy=copy.deepcopy(policy);self.sources=list(sources)+[binding(HERE/'mapped.py'),binding(HERE/'mapped_worker.py')]
        self.supervisor=Supervisor(HERE/'mapped-runs',policy);self.session=uuid.uuid4().hex;self.events={}

    def qualify(self,request,*,cancel=None):
        started=time.monotonic()
        base={'status':'invalid','authority_effect':'none','application_authorized':False}
        try:
            raw=json.dumps({'request':request,'resource_policy':self.policy},ensure_ascii=False,allow_nan=False).encode()
            require(len(raw)<=self.policy['work_limits']['input_bytes'],'mapped input byte ceiling')
            for ref in self.sources:check(ref)
            run=self.supervisor.run([sys.executable,str(HERE/'mapped_worker.py')],cancel,raw_input=raw,worker_sources=self.sources,started=started)
            if not run['complete']:
                status={'cancelled':'cancelled','policy-unavailable':'unsupported-policy','timeout':'unknown-resource','oom':'unknown-resource','output-limit':'unknown-resource'}.get(run['outcome'],'invalid')
                return {**base,'status':status,'reason':run['reason'],'supervised_run':run}
            job=Path(run['job']);path=job/'candidate.json'
            remaining=min(self.policy['output_bytes']-run['output_bytes_observed'],self.policy['work_limits']['input_bytes'])
            require(0<=path.stat().st_size<=remaining,'mapped output/IPC byte ceiling')
            packet=C.decode(path.read_bytes())
            require(packet.get('state')=='unissued','mapped worker issued its own capability')
            if packet['schema']=='relational.mapped-worker-refusal/v3':
                require(packet['status'] in ['invalid','unknown-resource'],'mapped refusal outcome changed')
                return {**base,'status':packet['status'],'reason':packet['reason'],'supervised_run':run}
            require(packet['schema']=='relational.unissued-mapped-check/v3',packet.get('reason','mapped refusal'))
            require(packet['request_bytes_sha256']==hashlib.sha256(raw).hexdigest() and packet['policy_identity']==C.identity(self.policy),'mapped input/policy changed')
            require(packet['request_identity']==C.identity(request),'mapped identity differs')
            for key in ['request','result','dependencies']:require(check(packet[key]).is_relative_to(job),'mapped result escaped owned job')
            for ref in self.sources:check(ref)
            require(cancel is None or not cancel.is_set(),'cancelled before mapped issuance')
            require(time.monotonic()-started<=self.policy['run_seconds'],'mapped whole-run deadline')
            value={**packet,'schema':'relational.fresh-mapped-check/v3','state':'fresh-process-local','run_id':uuid.uuid4().hex,'session':self.session,
                   'supervised_record':binding(job/'run-record.json'),'worker_sources':self.sources}
            receipt=immutable(job/'mapped-completion.json',value)
            self.events[value['run_id']]={'identity':C.identity(value),'receipt':receipt}
            return {**base,'status':'fresh-mapped-candidate','value':value,'completion':receipt,'supervised_run':run}
        except Exception as e:return {**base,'reason':str(e).splitlines()[0][:500]}

    def live_event(self,answer):
        try:
            value=answer['value'];event=self.events.get(value['run_id'])
            require(event and value['session']==self.session and event['identity']==C.identity(value),'mapped live event unavailable')
            require(event['receipt']==answer['completion'],'mapped completion changed');check(event['receipt'])
            for key in ['request','result','dependencies','supervised_record']:check(value[key])
            for ref in value['worker_sources']:check(ref)
            for m in C.decode(check(value['dependencies']).read_bytes())['modules']:check(m['source']);check(m['olean'])
            for m in C.decode(check(value['result']).read_bytes())['kernel_evidence']:check(m['source']);check(m['olean'])
            return True
        except Exception:return False
