"""Owned phases/resume provenance; all fresh checking remains inside supervision."""
from pathlib import Path
import hashlib
import json
import os
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C,BASE,require
from v3.p06.pipeline import qualify_checked
from v3.p07.worker_context import WorkerContext
from v3.p07.runs import owner,record_phase,inspect_resume,prepare_final,exclusive

job=Path(os.environ['RELATIONAL_SUPERVISOR_JOB']).resolve();context=None
try:
    os.umask(0o077);require(job.is_relative_to(BASE/'p07'),'invalid owned P07 job')
    owner(job);record_phase(job,'raw-input-prepared')
    raw=(job/'request.raw').read_bytes();request=C.decode(raw);C.validate('request',request)
    if len(sys.argv)>1:
        resume=C.decode(sys.argv[1].encode());checked=inspect_resume(resume,job)
        exclusive(job/'resume-validation.json',checked)
    context=WorkerContext(job,request['resource_policy'],request['layout'])
    result=qualify_checked(request,context)
    if result['status']!='qualified-candidate' and context.last_outcome:result['resource_report']['outcome']=context.last_outcome
    result['resource_report']['enforcement']=context.description['enforcement']
    result['resource_report']['events']=[{'kind':'worker','detail':'Owned phases and independently anchored cache; candidate remains unissued until supervision completes.'}]
    C.validate('result',result)
    packet={'schema':'relational.unissued-candidate/v3','state':'unissued',
            'request_bytes_sha256':hashlib.sha256(raw).hexdigest(),'proposed_result':result}
except Exception as e:
    packet={'schema':'relational.worker-refusal/v3','state':'unissued','status':'invalid',
            'reason':str(e).splitlines()[0][:300],'claims':[],'application_authorized':False}
with (job/'candidate.json').open('x') as f:json.dump(packet,f,allow_nan=False)
prepare_final(job,packet.get('proposed_result',{}),context.cache_check if context else None)
