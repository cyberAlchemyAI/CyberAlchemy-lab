"""Owned exclusive phase records and finalized mediated run evidence."""
from pathlib import Path
import json
import os
import uuid
from jsonschema import Draft202012Validator
from ..p03.context import BASE,ROOT,C,check,binding,require

HERE=Path(__file__).resolve().parent

def validate(name,value):
    schema=C.decode((HERE/(name+'.schema.json')).read_bytes())
    Draft202012Validator(schema).validate(value);return value

def exclusive(path,value):
    path=Path(path).resolve();require(path.is_relative_to(HERE),'run metadata outside P07')
    raw=(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.chmod(path,0o400)
    return binding(path)

def files(job):
    result=[]
    for p in sorted(job.rglob('*')):
        require(not p.is_symlink(),'symlink in owned run')
        if p.is_file():result.append(binding(p))
    return result

def owner(job):
    job=Path(job).resolve();require(job.is_relative_to(HERE),'job outside owned P07 store')
    require(job.name.startswith('job-'),'invalid owned job name')
    require(not (job/'owner.json').exists(),'existing ownership record')
    return exclusive(job/'owner.json',{'schema':'relational.run-owner/v3','run_id':job.name,
                                      'ownership_token':uuid.uuid4().hex,'job':str(job.relative_to(ROOT)),
                                      'cleanup':'proposal-only; accepted and other runs excluded',
                                      'authority_effect':'none'})

def record_phase(job,name,*,request_identity=None,cache_check=None):
    job=Path(job).resolve();own=C.decode((job/'owner.json').read_bytes())
    phases=sorted(job.glob('phase-*.json'));index=len(phases)
    descriptor=C.decode((job/'supervision.json').read_bytes())
    raw_sha=binding(job/'request.raw')['sha256']
    return exclusive(job/('phase-'+str(index).zfill(4)+'.json'),{
        'schema':'relational.run-phase/v3','run_id':own['run_id'],'index':index,'name':name,
        'owner':binding(job/'owner.json'),'previous':binding(phases[-1]) if phases else None,
        'request_bytes_sha256':raw_sha,'request_identity':request_identity,
        'policy_identity':C.identity(descriptor['policy']),'inputs':descriptor['worker_sources'],
        'outputs':files(job),'cache_check':cache_check,'fresh_qualification':False,'authority_effect':'none'})

def inspect_resume(ref,job):
    path=check(ref);require(path.is_relative_to(HERE),'resume outside owned store')
    phase=validate('phase',C.decode(path.read_bytes()));source=path.parent
    require(phase['schema']=='relational.run-phase/v3','resume requires a phase record')
    require(path.name=='phase-'+str(phase['index']).zfill(4)+'.json','phase index/name mismatch')
    own_path=check(phase['owner']);require(own_path==source/'owner.json','transplanted phase owner')
    own=validate('owner',C.decode(own_path.read_bytes()))
    require(own['schema']=='relational.run-owner/v3' and own['run_id']==source.name==phase['run_id'],'run ownership mismatch')
    require(own['job']==str(source.relative_to(ROOT)),'owner path mismatch')
    descriptor=C.decode((Path(job)/'supervision.json').read_bytes())
    require(phase['policy_identity']==C.identity(descriptor['policy']),'resume policy changed')
    require(phase['request_bytes_sha256']==binding(Path(job)/'request.raw')['sha256'],'resume request bytes changed')
    require(phase['inputs']==descriptor['worker_sources'],'resume implementation/source set changed')
    for r in phase['inputs']:check(r)
    for r in phase['outputs']:
        p=check(r);require(p.is_relative_to(source),'phase output transplanted from another run')
    previous=phase['previous'];index=phase['index']
    while previous:
        p=check(previous);require(p.parent==source,'previous phase from another run')
        old=validate('phase',C.decode(p.read_bytes()));index-=1
        require(old['index']==index and old['run_id']==own['run_id'],'broken phase chronology')
        require(old['policy_identity']==phase['policy_identity'] and old['request_bytes_sha256']==phase['request_bytes_sha256'] and old['inputs']==phase['inputs'],'earlier phase inputs changed')
        previous=old['previous']
    require(index==0,'missing earlier phase provenance')
    return {'schema':'relational.resume-validation/v3','source_phase':ref,'source_run':phase['run_id'],
            'mode':'fresh-rerun-new-owned-job','reused_qualification':False,'authority_effect':'none'}

def prepare_final(job,result,cache_check=None):
    job=Path(job).resolve();phases=sorted(job.glob('phase-*.json'))
    packet=binding(job/'candidate.json')
    descriptor=C.decode((job/'supervision.json').read_bytes())
    value={'schema':'relational.owned-run-record/v3','run_id':job.name,'phase':'prepared',
           'request_identity':result.get('request_identity'),'request_bytes_sha256':binding(job/'request.raw')['sha256'],
           'policy_identity':C.identity(descriptor['policy']),'owner':binding(job/'owner.json'),
           'inputs':descriptor['worker_sources'],'outputs':files(job),'phases':[binding(p) for p in phases],
           'cache_check':cache_check,'resource_events':[],'timings':{},'result':packet,
           'application_authorized':False,'authority_effect':'none'}
    validate('run-record',value);ref=exclusive(job/'owned-run-prepared.json',value)
    # Keep the job root writable for parent-only final issuance; freeze worker
    # files and all proof subdirectories after they have stopped changing.
    for p in job.rglob('*'):
        if p.is_file():os.chmod(p,0o400)
    for p in sorted((p for p in job.rglob('*') if p.is_dir()),key=lambda x:len(x.parts),reverse=True):os.chmod(p,0o500)
    return ref

def seal(job,envelope):
    job=Path(job).resolve();require(job.is_relative_to(HERE),'seal outside owned store')
    if not (job/'owner.json').exists():owner(job)
    prepared=job/'owned-run-prepared.json'
    if prepared.exists():
        value=C.decode(prepared.read_bytes());require(value['run_id']==job.name,'prepared run transplant')
    else:
        descriptor=C.decode((job/'supervision.json').read_bytes())
        value={'schema':'relational.owned-run-record/v3','run_id':job.name,'request_identity':None,
               'request_bytes_sha256':binding(job/'request.raw')['sha256'],'policy_identity':C.identity(descriptor['policy']),
               'owner':binding(job/'owner.json') if (job/'owner.json').exists() else None,
               'inputs':descriptor['worker_sources'],'outputs':[],'phases':[binding(p) for p in sorted(job.glob('phase-*.json'))],
               'cache_check':None,'application_authorized':False,'authority_effect':'none'}
    value['phase']='completed' if envelope['status']=='qualified-candidate' else envelope['status']
    run=envelope['supervised_run'];value['resource_events']=run['events'];value['timings']={'supervised_seconds':run['seconds']}
    # Prepared outputs were byte-bound inside the worker. Parent additions are
    # bounded completion metadata; no proof generation or evaluation runs here.
    value['outputs'] += [binding(p) for p in [prepared,job/'run-record.json',job/'result.json',job/'completion.json'] if p.exists()]
    value['result']=binding(job/'result.json') if envelope['status']=='qualified-candidate' else None
    validate('run-record',value);ref=exclusive(job/'owned-run-record.json',value)
    for p in job.rglob('*'):
        if p.is_file():os.chmod(p,0o400)
    for p in sorted((p for p in job.rglob('*') if p.is_dir()),key=lambda x:len(x.parts),reverse=True):os.chmod(p,0o500)
    directory=os.open(job,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(directory)
    finally:os.close(directory)
    os.chmod(job,0o500);return ref

def inspect_record(ref):
    path=check(ref);require(path.is_relative_to(HERE) and path.name=='owned-run-record.json','not an owned final run record')
    record=validate('run-record',C.decode(path.read_bytes()));job=path.parent
    require(record['schema']=='relational.owned-run-record/v3' and record['run_id']==job.name,'run identity transplant')
    if record['owner']:
        own=validate('owner',C.decode(check(record['owner']).read_bytes()))
        require(own['run_id']==job.name and own['job']==str(job.relative_to(ROOT)),'final ownership mismatch')
    for r in record['inputs']:check(r)
    for r in record['outputs']:
        p=check(r);require(p.is_relative_to(job),'final output from another run')
    for r in record['phases']:require(check(r).parent==job,'phase from another run')
    if record['result']:require(check(record['result'])==job/'result.json','final result transplant')
    if record['cache_check']:
        # Revalidate direct source/import references as currentness only. The
        # expected cache metadata was independently anchored inside the worker.
        check(record['cache_check']['anchor'])
        for r in record['cache_check']['checked']:check(r)
    return {'status':'recorded-current','run_id':job.name,'phase':record['phase'],
            'fresh_qualification':False,'application_authorized':False,'authority_effect':'none'}

def execution_state(plan):
    required=[];optional=[];accepted=[];resolved=[]
    for t in plan['tasks']:
        opt=t['selection']=='optional-separate-profile'
        if t['status']=='accepted':accepted.append(t['id'])
        elif not t['selected']:
            require(opt,'required task cannot be not-needed');resolved.append({'id':t['id'],'resolution':'not-needed'})
        elif opt:optional.append(t['id'])
        else:required.append(t['id'])
    return {'schema':'relational.execution-state/v3','accepted':accepted,'remaining_required':required,
            'remaining_optional':optional,'resolved_optional':resolved,'complete':not(required or optional),'authority_effect':'none'}

def cleanup_proposal(ref,target):
    status=inspect_record(ref);job=check(ref).parent;target=Path(target).resolve()
    require(target==job,'cleanup may name only its exact owned run')
    require(status['phase']!='completed','completed accepted evidence excluded from cleanup')
    return {'schema':'relational.cleanup-proposal/v3','owner':binding(job/'owner.json'),
            'target':str(job.relative_to(ROOT)),'action':'review-only; no deletion','authority_effect':'none'}
