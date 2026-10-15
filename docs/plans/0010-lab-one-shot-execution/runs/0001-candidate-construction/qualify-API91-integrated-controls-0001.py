"""Actual authenticated integrated public resolution, exact retry and guard refusals."""
import base64
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v91'
SOURCE='b007a3251489936135b1dcdbb3c46657706bbb651678d11fcaf2280fb09fc92e'
PROFILE='ba8650f6067c89ade5717b2a6e5c3d0d5b8631c76dc3b66bbd42024d8c790e35'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def snapshot(root):return {path.relative_to(root).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob('*') if path.is_file()}


def main():
    report=RUN/'API91-integrated-controls-0001.json';assert not report.exists()
    spec=importlib.util.spec_from_file_location('_cal_API91_selected_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(SOURCE)
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    name='_cal_API91_actual_resolution'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    P=__import__(name+'.protocol',fromlist=['*']);A=__import__(name+'.auth',fromlist=['*'])
    S=__import__(name+'.service',fromlist=['Service']);F=__import__(name+'.fixtures',fromlist=['*'])
    H=__import__(name+'.handlers',fromlist=['cut']);IG=__import__(name+'.integrated_guard',fromlist=['pure'])
    package_path=BASE/'current-participation-v8/packages/0001'
    plan=load(package_path/'resolution-qualification-plan.json');period=load(package_path/'period.json')
    checks=[];calls=[];failed=None;owned=None;evidence_originals=[]
    try:
        schemas=P.Schemas(PROFILE)
        with P.source.replay_source('integrated-participation') as view,tempfile.TemporaryDirectory(prefix='cal-API91-integrated-resolution-') as temporary:
            owned=Path(temporary);owned.chmod(0o700);workspace=owned/'workspace';workspace.mkdir(mode=0o700)
            source_workspace=package_path/'qualification-workspace'
            for directory in ('inputs','objects','journal'):(workspace/directory).mkdir(mode=0o700)
            for path in source_workspace.rglob('*'):
                if path.is_file():
                    target=workspace/path.relative_to(source_workspace);target.write_bytes(path.read_bytes());target.chmod(0o600)
            key=Ed25519PrivateKey.generate()
            policy={'schema_version':'lab-local-integrated-challenge-resolution-policy/v3-candidate',
                'principal_ref':plan['principal_ref'],'reader_public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),
                'host_uid':os.getuid(),'source_name':'integrated-participation','scope_refs':[view.data['config']['scope_ref']],
                'expires_at':period['expires_at'],'max_request_bytes':1048576,'max_response_bytes':4194304,'max_calls':128,
                'allowed_operations':list(P.RESOLUTION_SUPPORTED),'revoked':False,'scope_posture':'isolated-candidate-preparation',
                'purpose':'durable-metadata-and-exact-integrated-challenge-resolution',
                'development_authorization_binding':P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),
                'scope_control':None,'session_control':None,'projection_control':None,
                'workspace':{'root':str(workspace),'manifest_sha256':P.source.sha((workspace/'workspace.json').read_bytes()),'max_actions':64},
                'resolution_control':{'routing_binding':plan['routing_binding'],
                    'method_binding':P.binding(str((BASE/'challenge-resolution-v6/preparation.py').relative_to(ROOT)),(BASE/'challenge-resolution-v6/preparation.py').read_bytes())},
                'resolution_reference_control':{'resolver_binding':P.binding(str((BASE/'challenge-resolution-v6/reference_roles.py').relative_to(ROOT)),(BASE/'challenge-resolution-v6/reference_roles.py').read_bytes()),'contract_binding':P.binding(str((BASE/'challenge-resolution-v6/reference-role-contract.json').relative_to(ROOT)),(BASE/'challenge-resolution-v6/reference-role-contract.json').read_bytes())},
                'integrated_source_control':P.source.integrated_bindings(),'authority_effect':'none','actual_owner_outcome':None}
            assert schemas.valid('reader-authentication',policy),'closed integrated policy invalid'
            policy_path=owned/'reader-policy.json';policy_raw=P.compact(policy);policy_path.write_bytes(policy_raw);policy_path.chmod(0o600)
            channel=A.ReaderChannel(policy_path,P.source.sha(policy_raw),schemas)
            context=channel.authenticate(F.proof(key,channel.challenge))['context'];key=None
            service=S.Service(view,channel,schemas)
            try:
                assert H.cut(view)==plan['source_cut'],'actual independently selected source cut differs from signed plan'
                assert context['principal_ref']==plan['principal_ref'] and context['agent_instance_ref'] is None and context['session_ref'] is None
                checks.append({'check':'actual-channel-source-and-owner','result':'PASS'})
                call=F.call(context,'lab.status',H.cut(view));call.update(operation='challenge.resolve',
                    idempotency_key=plan['idempotency_key'],message=copy.deepcopy(plan['message']),
                    max_response_bytes=4194304,deadline=(datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat())
                call['expected_contract_profile_binding']=schemas.profile_binding
                before=snapshot(workspace)
                malformed=copy.deepcopy(call);malformed['call_id']+=':schema';malformed['message']['unexpected_field']=True
                response=service.call(P.compact(malformed));calls.append({'call':malformed,'reply':response})
                assert response.get('code')=='invalid-envelope',response
                assert snapshot(workspace)==before
                checks.append({'check':'closed-public-schema-refused-before-journal','result':'PASS'})
                expired=copy.deepcopy(call);expired['call_id']+=':deadline';expired['deadline']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
                response=service.call(P.compact(expired));calls.append({'call':expired,'reply':response})
                assert response['kind']=='error' and response['message']['code']=='deadline-exceeded',response
                assert snapshot(workspace)==before
                checks.append({'check':'actual-expired-deadline-refused-before-journal','result':'PASS'})
                stale=copy.deepcopy(call);stale['call_id']+=':stale';stale['message']['source_cut']['commit_sha256']='0'*64
                response=service.call(P.compact(stale));calls.append({'call':stale,'reply':response})
                assert response['kind']=='error',response
                assert snapshot(workspace)==before
                checks.append({'check':'different-request-source-cut-refused-before-journal','result':'PASS','observed_code':response['message']['code']})
                changed=copy.deepcopy(policy);changed['revoked']=True;policy_path.write_bytes(P.compact(changed))
                try:
                    withdrawn=copy.deepcopy(call);withdrawn['call_id']+=':withdrawn'
                    response=service.call(P.compact(withdrawn));calls.append({'call':withdrawn,'reply':response})
                    assert response.get('code')=='unauthenticated-channel',response
                    assert snapshot(workspace)==before
                finally:policy_path.write_bytes(policy_raw)
                channel.guard()
                checks.append({'check':'actual-private-policy-change-refused-before-journal','result':'PASS'})
                assert H.cut(view)==plan['source_cut'] and service.handlers.current()
                checks.append({'check':'source-preserved-and-no-candidate-journal-effects','result':'PASS'})
            finally:service.close();channel.close()
        assert owned is not None and not owned.exists(),'owned private fixture remains'
        checks.append({'check':'owned-fixture-and-transport-key-disposed','result':'PASS'})
    except Exception as error:
        chain=[];current=error
        while current is not None and len(chain)<8:
            chain.append({'error_class':type(current).__name__,'reason':str(current)})
            current=current.__cause__
        failed=chain
    guard.verify(SOURCE)
    value={'schema_version':'lab-actual-integrated-public-controls-qualification/v1-candidate',
        'result':'PASS' if failed is None and len(checks)==7 else 'FAIL','actual_cases':4,'checks':checks,
        'actual_calls':calls,'failure_chain':failed,'validation_evidence_originals':evidence_originals,'source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'files':[bind(path) for path in (API/'source-manifest.json',API/'contract-profile.json',
            package_path/'manifest.json',RUN/'authorization.json',Path(__file__).resolve())],
        'source_guarded_exit_completed':True,'fixture_removed':owned is not None and not owned.exists(),
        'private_keys_exported':False,'canonical_admissions':0,'actual_owner_outcome':None,
        'positive_resolution_qualified':False,'original323API_methods_requalified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'authority_effect':'none',
        'claim_ceiling':'Four actual public input/deadline/cut/private-policy refusal cases before journal effects only; no positive resolution, full API or canonical admission.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'checks':checks,'failure_chain':failed,'report_binding':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
