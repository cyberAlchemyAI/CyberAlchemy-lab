"""Fixed supervised candidate extension clients; no core authority transition."""
from pathlib import Path
import copy
import hashlib
import importlib
import json
import sys
import time
import uuid
from ..p03.context import BASE,C,ROOT,binding,check,require,write
from ..p06.supervisor import Supervisor
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
IDS={'E'+str(n).zfill(2) for n in range(7)}
def schema_validate(path,value,result=False):
    schema=C.decode(Path(path).read_bytes())
    if result:schema={'$schema':schema['$schema'],'$defs':schema['$defs'],'$ref':'#/$defs/result'}
    Draft202012Validator(schema).validate(value)

def source_inventory(extension):
    require(extension in IDS,'unsupported installed extension')
    folder=BASE/extension.lower();paths=[HERE/'extension_runtime.py',HERE/'extension_worker.py']
    paths += sorted(folder.glob('*.py'))+sorted(folder.glob('*.lean'))+sorted(folder.glob('*.schema.json'))
    refs=[binding(p) for p in paths]
    receipt=folder/'task-acceptance.json'
    if receipt.exists():
        accepted=C.decode(receipt.read_bytes());require(accepted['result']=='accepted','extension not accepted')
        expected={r['path']:r for r in accepted['artifacts']+accepted['inputs']}
        for ref in refs:require(expected.get(ref['path'])==ref,'extension trusted source changed after acceptance');check(ref)
    return refs

def load_extension(extension):
    require(extension in IDS,'unsupported extension')
    return importlib.import_module('v3.'+extension.lower()+'.adapter')

def lean_string(value):
    # Quoted strings remain data. Numeric construction covers control characters
    # whose JSON escapes are not part of the Lean string grammar.
    require(not any(0xD800<=ord(c)<=0xDFFF for c in value),'invalid Unicode scalar in Lean string')
    if any(ord(c)<32 for c in value):
        return '(String.ofList ['+', '.join('Char.ofNat '+str(ord(c)) for c in value)+'])'
    return json.dumps(value,ensure_ascii=False)

def lean_ref(value):return '⟨'+lean_string(value['id'])+', '+lean_string(value['version'])+'⟩'

class Client:
    def __init__(self,extension,policy):
        self.extension=extension;self.sources=source_inventory(extension)
        self.policy=copy.deepcopy(policy);C.validate('resource-policy',policy)
        self.supervisor=Supervisor(BASE/extension.lower()/'runs',policy)
        self.events={};self.session=uuid.uuid4().hex

    def qualify(self,raw,*,cancel=None):
        start=time.monotonic();base={'extension':self.extension,'status':'invalid','reason':'','authority_effect':'none','application_authorized':False}
        try:
            require(isinstance(raw,bytes) and len(raw)<=self.policy['work_limits']['input_bytes'],'raw input byte ceiling')
            for ref in self.sources:check(ref)
            run=self.supervisor.run([sys.executable,str(HERE/'extension_worker.py'),self.extension],cancel,
                raw_input=raw,worker_sources=self.sources,started=start)
            if not run['complete']:
                status={'cancelled':'cancelled','policy-unavailable':'unsupported-policy','timeout':'unknown-resource','oom':'unknown-resource','output-limit':'unknown-resource'}.get(run['outcome'],'invalid')
                return {**base,'status':status,'reason':run['reason'],'supervised_run':run}
            job=Path(run['job']);packet_path=job/'candidate.json'
            require(packet_path.stat().st_size<=min(self.policy['work_limits']['input_bytes'],self.policy['output_bytes']-run['output_bytes_observed']),'extension IPC/output envelope')
            packet=C.decode(packet_path.read_bytes())
            require(packet['state']=='unissued' and packet['extension']==self.extension,'worker capability/extension mismatch')
            if packet['status']!='checked':return {**base,'status':packet['status'],'reason':packet['reason'],'supervised_run':run}
            require(set(packet)=={'state','extension','status','input_sha256','request_identity','request','value','kernel','witness','imports','scope','authority_effect','application_authorized'},'extension result fields')
            require(packet['input_sha256']==hashlib.sha256(raw).hexdigest(),'extension exact input mismatch')
            require(check(packet['request']).is_relative_to(job),'extension request escaped owned run')
            for ref in packet['imports']:check(ref)
            for record in packet['kernel']:check(record['source']);check(record['olean'])
            require(check(packet['witness']).is_relative_to(job),'extension witness escaped job')
            mod=load_extension(self.extension);schema_validate(mod.SCHEMA,packet['value'],True)
            for ref in self.sources:check(ref)
            require(cancel is None or not cancel.is_set(),'cancelled before issuance')
            require(time.monotonic()-start<=self.policy['run_seconds'],'whole-run deadline before issuance')
            value={**packet,'state':'fresh-process-local','run_id':uuid.uuid4().hex,'session':self.session,
                'supervised_record':binding(job/'run-record.json'),'worker_sources':self.sources}
            completion=write(job/'extension-completion.json',value)
            self.events[value['run_id']]={'identity':C.identity(value),'completion':completion}
            return {**base,'status':'fresh-extension-candidate','value':value,'completion':completion,'supervised_run':run}
        except Exception as e:return {**base,'reason':str(e).splitlines()[0][:800]}

    def live_event(self,answer):
        try:
            value=answer['value'];event=self.events.get(value['run_id'])
            require(event and value['session']==self.session and event['identity']==C.identity(value),'extension live event unavailable')
            require(answer['completion']==event['completion'],'completion substitution')
            check(event['completion']);check(value['request']);check(value['witness']);check(value['supervised_record'])
            for ref in value['worker_sources']+value['imports']:check(ref)
            for record in value['kernel']:check(record['source']);check(record['olean'])
            return True
        except Exception:return False
