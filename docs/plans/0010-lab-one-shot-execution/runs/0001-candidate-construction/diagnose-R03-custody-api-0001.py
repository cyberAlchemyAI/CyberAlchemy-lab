"""Independent owned eight-call diagnostic; never a full-suite qualification."""
import argparse, hashlib, importlib.util, json, os, sys, tempfile
from contextlib import ExitStack
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v17'
SOURCE='99f1d11bbb28f86cd2a745caed8849a6a14fc9753566b36fc11241e65c6d7740'
PROFILE='2d6841dd6e33ef67909579de2674386542322b1271a481573dff435d9c8db3ed'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def guard(pin):
    p=HERE/'custody-api-diagnostic-source-0001.json';assert sha(p.read_bytes())==pin
    m=json.loads(p.read_bytes())
    for row in m['files']:
        path=ROOT/row['path'];assert path.is_file() and not path.is_symlink() and sha(path.read_bytes())==row['sha256'],row['path']
    return m
def load(name,path,package=False):
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);a=parser.parse_args();guard(a.source_sha256)
    load('_cal_api17_diagnostic',API/'__init__.py',True)
    guard_api=__import__('_cal_api17_diagnostic.guard',fromlist=['verify']);guard_api.verify(SOURCE)
    F=__import__('_cal_api17_diagnostic.example_fixture',fromlist=['*'])
    S=__import__('_cal_api17_diagnostic.service',fromlist=['*'])
    P=__import__('_cal_api17_diagnostic.projection_refresh',fromlist=['control'])
    M=__import__('_cal_api17_diagnostic.artifact_model',fromlist=['artifact_ref'])
    C=__import__('_cal_api17_diagnostic.custody_context_sessions',fromlist=['R'])
    events=[]
    with ExitStack() as stack:
        view=stack.enter_context(F.source.replay_source('custody-participation'));schemas=F.Schemas(PROFILE)
        materials,metadata,target=F.materials_for(view)
        root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-api17-diagnostic-')));root.chmod(0o700)
        key,policy,pin=F.provision(root,'custody-participation',materials,metadata,principal=C.R.PRINCIPAL,projection_control=P.control(view))
        channel=F.ReaderChannel(policy,pin,schemas);challenge=channel.challenge;proof=F.proof(key,challenge);authenticated=channel.authenticate(proof)
        service=S.Service(view,channel,schemas);stack.callback(service.close)
        def invoke(call):
            raw=F.compact(call);result=service.call(raw)
            events.append({'original_call':json.loads(raw),'original_call_sha256':sha(raw),'reply':result,'valid_reply':schemas.valid('api-reply',result)})
            print(json.dumps({'operation':call['operation'],'kind':result.get('kind'),'code':result.get('message',{}).get('code'),'public_message':result.get('message',{}).get('message')}),flush=True)
            return result
        for op in ['lab.status','catalog.get','artifact.query']:invoke(F.call(channel.context,op,F.cut(view)))
        subject=next(s for s in view.subjects.values() if s['identity']==C.R.WORK)
        invoke(F.call(channel.context,'artifact.inspect',F.cut(view),artifact=M.artifact_ref(view,subject),include=['body','contract','gaps']))
        invoke(F.candidate_call(service,target,'change.prepare','fixture:prepare'))
        invoke(F.candidate_call(service,target,'change.validate','validate:integrated'))
        invoke(F.call(channel.context,'operation.inspect',None,lookup={'operation':'change.prepare','idempotency_key':'fixture:prepare'}))
        call=F.call(channel.context,'lab.status',F.cut(view));budget=call['message']['budget'];budget['max_actions']=1
        grant=channel.policy['projection_control'];prior=service.handlers.generations.get(F.source.sha(F.compact(F.cut(view))))
        call.update(operation='projection.refresh',idempotency_key='projection:diagnostic',message={
            'schema_version':'lab-projection-refresh-request/v1-candidate','request_ref':'request:projection:diagnostic',
            'source_cut':F.cut(view),'projector_binding':grant['projector_binding'],'contract_catalog_binding':grant['contract_catalog_binding'],
            'expected_generation_binding':None if prior is None else prior.binding,'budget':budget,'authority_effect':'none'})
        invoke(call)
        original_source_cut=view.custody_signed_sources.source_cut
        public_policy=F.source.parse(policy.read_bytes())
    assert not root.exists();guard_api.verify(SOURCE);guard(a.source_sha256)
    report={'schema_version':'lab-original-source-API-diagnostic/v1-candidate','result':'OBSERVED','source_sha256':SOURCE,'profile_sha256':PROFILE,
        'nonce_challenge':challenge,'signed_nonce_proof':json.loads(proof),'authenticated_reply':authenticated,'independent_public_policy':public_policy,
        'events':events,'source_cut':original_source_cut,'owned_host_removed':True,'full_suite_qualification':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    fd=os.open(HERE/'custody-api-diagnostic-result-0001.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'OBSERVED','actual_calls':len(events),'error_operations':[e['original_call']['operation'] for e in events if e['reply'].get('kind')!='result'],'owned_host_removed':True}),flush=True)
if __name__=='__main__':main()
