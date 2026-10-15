"""Expose private validation cause without changing public refusals or sources."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v62'
SOURCE='b8b27e11edccaa98e9f3874cfd036bc6c82f0eba0c42c2855435eab897d40cf4'
PROFILE='72264eef13c73d143b104215beb408ac31547ea3d3a14947b0f26a927f62f33c'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    name='_cal_API62_challenge_diagnosis'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    G=importlib.import_module(name+'.guard');P=importlib.import_module(name+'.protocol');F=importlib.import_module(name+'.challenge_fixture')
    W=importlib.import_module(name+'.workspace');G.verify(SOURCE);schemas=P.Schemas(PROFILE);chain=[]
    with P.source.replay_source('custody-participation') as view:
        before=P.compact(view.data['projection'])
        with F.example(view,schemas) as (service,request,witness):
            files={p.relative_to(service.vault.root).as_posix():p.read_bytes() for p in service.vault.root.rglob('*') if p.is_file()}
            call=request()
            try:service.select_challenge(call['message'],call['expected_source_cut'],call['idempotency_key'])
            except Exception as error:
                seen=set()
                while error is not None and id(error) not in seen:
                    seen.add(id(error));chain.append({'class':type(error).__name__,'message':str(error)[:12000]})
                    error=error.__cause__
            assert files=={p.relative_to(service.vault.root).as_posix():p.read_bytes() for p in service.vault.root.rglob('*') if p.is_file()}
        assert not witness['root'].exists() and before==P.compact(view.data['projection'])
    G.verify(SOURCE)
    report={'schema_version':'lab-actual-preflight-diagnosis/v1-candidate','result':'DIAGNOSED' if chain else 'NO-REFUSAL',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'exception_chain':chain,'public_API_calls':0,'durable_effects':0,'owned_fixture_cleanup_completed':True,
        'source_guarded_exit_completed':True,'producer_binding':bind(Path(__file__).resolve()),
        'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False}
    W.privacy(report);path=RUN/'API62-challenge-preflight-diagnosis-0001.json'
    with path.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'report_binding':bind(path),'exception_chain':chain}),flush=True)
if __name__=='__main__':main()
