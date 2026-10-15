"""Fixed trusted worker: raw decoding through the final exact proof inspection."""
from pathlib import Path
import hashlib
import json
import os
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C,BASE,require
from v3.p06.worker_context import WorkerContext
from v3.p06.pipeline import qualify_checked

job=Path(os.environ['RELATIONAL_SUPERVISOR_JOB']).resolve()
try:
    os.umask(0o077)
    require(job.is_relative_to(BASE),'invalid owned job')
    raw=(job/'request.raw').read_bytes();request=C.decode(raw);C.validate('request',request)
    context=WorkerContext(job,request['resource_policy'])
    result=qualify_checked(request,context)
    if result['status']!='qualified-candidate' and context.last_outcome:
        result['resource_report']['outcome']=context.last_outcome
    result['resource_report']['enforcement']=context.description['enforcement']
    result['resource_report']['events']=[{'kind':'worker','detail':'Original request policy retained; candidate is unissued until supervisor completion.'}]
    C.validate('result',result)
    packet={'schema':'relational.unissued-candidate/v3','state':'unissued','request_bytes_sha256':hashlib.sha256(raw).hexdigest(),'proposed_result':result}
except Exception as e:
    packet={'schema':'relational.worker-refusal/v3','state':'unissued','status':'invalid','reason':str(e).splitlines()[0][:300],'claims':[],'application_authorized':False}
with (job/'candidate.json').open('x') as f:json.dump(packet,f,allow_nan=False)
