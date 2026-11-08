"""Fixed qualification worker; live issuance follows complete owned supervision."""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import time
import uuid
from ..p03.context import BASE,C,binding,check,require
from .supervisor import Supervisor,HERE

WORKER_FILES=('api.py','supervisor.py','bootstrap.py','worker_context.py',
              'pipeline.py','generate_pipeline.py','evaluation_worker.py','qualification_worker.py')

class SupervisedQualifier:
    def __init__(self,run_root,policy,*,cgroup_parent=None,pids_max=None):
        self.supervisor=Supervisor(Path(run_root),policy,cgroup_parent,pids_max)
        self.session=uuid.uuid4().hex;self._events={}
        self.sources=[binding(HERE/name) for name in WORKER_FILES]
        self.sources += [binding(BASE/'p03/task-acceptance.json')]

    def qualify(self,raw,*,cancel=None):
        started=time.monotonic()
        require(isinstance(raw,bytes),'qualification input must be raw bytes')
        policy=copy.deepcopy(self.supervisor.policy)
        base={'schema':'relational.supervised-qualification/v3','status':'invalid',
              'qualified_result':None,'claims':[],'complete_closure':False,
              'application_authorized':False,'authority_effect':'none',
              'policy_identity':C.identity(policy),'supervised_run':None}
        if len(raw)>policy['work_limits']['input_bytes']:
            return {**base,'status':'unknown-resource','reason':'Raw input byte ceiling before decoding.'}
        raw_sha=hashlib.sha256(raw).hexdigest();base['request_bytes_sha256']=raw_sha
        for ref in self.sources:check(ref)
        run=self.supervisor.run([sys.executable,str(HERE/'qualification_worker.py')],cancel,
                                raw_input=raw,worker_sources=self.sources,started=started)
        base['supervised_run']=run
        if not run['complete']:
            status={'cancelled':'cancelled','policy-unavailable':'unsupported-policy',
                    'timeout':'unknown-resource','oom':'unknown-resource','output-limit':'unknown-resource'}.get(run['outcome'],'invalid')
            return {**base,'status':status,'reason':run['reason']}
        issued_path=None;completion_path=None
        try:
            job=Path(run['job']).resolve();require(job.is_relative_to(self.supervisor.run_root),'unexpected owned job')
            candidate=job/'candidate.json'
            # Returned metadata is bounded before allocation and counted once as
            # worker IPC in addition to its streamed stdout/stderr.
            remaining=min(policy['output_bytes']-run['output_bytes_observed'],policy['work_limits']['input_bytes'])
            require(remaining>=0 and candidate.stat().st_size<=remaining,'Returned metadata/output ceiling.')
            with candidate.open('rb') as f:packet_raw=f.read(remaining+1)
            require(len(packet_raw)<=remaining,'Returned metadata grew beyond output ceiling.')
            packet=C.decode(packet_raw)
            for ref in self.sources:check(ref)
            require(packet.get('state')=='unissued','worker packet already claims issuance')
            if packet['schema']=='relational.worker-refusal/v3':
                require(packet['status']=='invalid' and not packet['claims'] and packet['application_authorized'] is False,'malformed worker refusal')
                return {**base,'reason':packet['reason']}
            require(packet['schema']=='relational.unissued-candidate/v3','unexpected worker packet')
            require(packet['request_bytes_sha256']==raw_sha,'worker input bytes differ')
            result=packet['proposed_result'];C.validate('result',result)
            require(result['resource_report']['policy_identity']==C.identity(policy),'worker policy identity differs')
            require(result['application_authorized'] is False,'worker elevated application authority')
            if result['status']!='qualified-candidate':
                return {**base,'status':result['status'],'reason':result['reason'],'failure_result':result}
            require(result['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'incomplete fixed obligation inventory')
            require(result['complete_closure'] and result['claims'],'worker qualification lacks closure/claims')
            result['resource_report']={'enforcement':run['enforcement'],'outcome':'completed',
                                      'events':run['events'],'policy_identity':C.identity(policy)}
            C.validate('result',result)
            if cancel is not None and cancel.is_set():
                return {**base,'status':'cancelled','reason':'Cancelled before final issuance.'}
            if time.monotonic()-started>policy['run_seconds']:
                return {**base,'status':'unknown-resource','reason':'Whole-run deadline exceeded before final issuance.'}
            issued=(json.dumps(result,allow_nan=False,ensure_ascii=False)+'\n').encode()
            issued_path=job/'result.json'
            with issued_path.open('xb') as f:f.write(issued)
            os.chmod(job/'result.json',0o600)
            completion={'schema':'relational.supervisor-completion/v3','session':self.session,
                        'request_bytes_sha256':raw_sha,'result':binding(job/'result.json'),
                        'run_record':binding(job/'run-record.json'),'worker_sources':self.sources,
                        'output_bytes_including_returned_metadata':run['output_bytes_observed']+len(packet_raw),
                        'seconds_including_issuance':time.monotonic()-started,
                        'authority_effect':'none','application_authorized':False}
            if (cancel is not None and cancel.is_set()) or time.monotonic()-started>policy['run_seconds']:
                (job/'result.json').unlink()
                return {**base,'status':'cancelled' if cancel is not None and cancel.is_set() else 'unknown-resource',
                        'reason':'Issuance interrupted; unissued result removed.'}
            completion_path=job/'completion.json'
            with completion_path.open('x') as f:json.dump(completion,f,allow_nan=False)
            require(cancel is None or not cancel.is_set(),'Cancelled during final completion recording.')
            require(time.monotonic()-started<=policy['run_seconds'],'Whole-run deadline exceeded during final completion recording.')
            # The event is process-local. Reading either saved JSON file cannot
            # create it or authorize application of a candidate.
            self._events[result['run_id']]={'result_identity':C.identity(result),
                                           'completion':binding(job/'completion.json'),'session':self.session}
            return {**base,'status':'qualified-candidate','qualified_result':result,
                    'claims':result['claims'],'complete_closure':True,
                    'completion':binding(job/'completion.json')}
        except Exception as e:
            for path in [completion_path,issued_path]:
                if path is not None and path.exists():path.unlink()
            status='cancelled' if str(e).startswith('Cancelled') else 'unknown-resource' if any(x in str(e) for x in ['ceiling','deadline']) else 'invalid'
            return {**base,'status':status,
                    'reason':str(e).splitlines()[0][:300]}

    def live_event(self,result):
        event=self._events.get(result.get('run_id'))
        if not event or event['session']!=self.session or event['result_identity']!=C.identity(result):return False
        try:
            path=check(event['completion']);completion=C.decode(path.read_bytes())
            check(completion['result']);check(completion['run_record'])
            for ref in completion['worker_sources']:check(ref)
        except Exception:return False
        return True
