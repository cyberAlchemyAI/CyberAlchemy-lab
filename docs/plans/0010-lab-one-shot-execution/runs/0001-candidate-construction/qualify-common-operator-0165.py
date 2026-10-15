"""Actual shared-profile dispatcher calls over three independent nonce channels."""
import argparse,base64,copy,hashlib,importlib,importlib.util,json,sys,tempfile,traceback,uuid
from contextlib import ExitStack
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def install(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
def module(name,suffix):return importlib.import_module(name+'.'+suffix)
def snapshot(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--profile',required=True);args=parser.parse_args()
    api=BASE/'api-integration-v10';report=RUN/'Common-operator-0165.json';assert not report.exists()
    install('_cal_common_0165',api);P=module('_cal_common_0165','protocol');G=module('_cal_common_0165','guard')
    G.verify(args.source);schemas=P.Schemas(args.profile);members=json.loads((api/'integration-members.json').read_bytes())['members']
    install('_cal_common_actions_0165',BASE/members['actions']['directory']);AF=module('_cal_common_actions_0165','fixture');AS=module('_cal_common_actions_0165','service')
    install('_cal_common_governance_0165',BASE/members['governance']['directory']);GF=module('_cal_common_governance_0165','fixture');GS=module('_cal_common_governance_0165','service')
    S=module('_cal_common_0165','service');A=module('_cal_common_0165','auth');F=module('_cal_common_0165','fixtures');H=module('_cal_common_0165','handlers');I=module('_cal_common_0165','integration_dispatch')
    class SharedGovernanceFixture(GF.Fixture):
        def open(self):
            self.host=GF.GovernanceHost(self.root,self.policy_pin,self.schemas,members['governance']['source_sha256'],members['governance']['profile_sha256'],integration_profile_binding=self.schemas.profile_binding)
            self.channel=GF.GovernanceChannel(self.host)
            self.channel.authenticate({'challenge':self.channel.challenge,'signature_base64':base64.b64encode(self.reader.sign(GF.encoded(self.channel.challenge))).decode()})
            self.service=GS.GovernanceService(self.host,self.channel)
    checks=[];calls=[];failure=None;owned=None
    def check(label,condition):
        assert condition,label;checks.append({'check':label,'result':'PASS'});print(label,flush=True)
    try:
        with ExitStack() as stack:
            owned=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-common-0165-')));owned.chmod(0o700)
            view=stack.enter_context(P.source.replay_source('engineering'))
            root=owned/'base';root.mkdir(mode=0o700);key,path,pin=F.provision(root,'engineering')
            channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None
            base=S.Service(view,channel,schemas);stack.callback(base.close)
            ar=owned/'actions';action=AF.OwnedActor(ar,schemas,integration_profile_binding=schemas.profile_binding);stack.callback(action.close)
            actions=AS.ActionService(action.runtime,action.channel,schemas,source_sha256=members['actions']['source_sha256'],profile_sha256=members['actions']['profile_sha256'],integration_profile_binding=schemas.profile_binding)
            gr=owned/'governance';gr.mkdir(mode=0o700);governance=SharedGovernanceFixture(gr,schemas);stack.callback(governance.service.close)
            common=I.IntegrationService(base,action_service=actions,governance_service=governance.service)
            check('three-independent-real-nonces-and-one-selected-schema',len({channel.context['context_ref'],action.channel.context['context_ref'],governance.channel.context['context_ref']})==3 and all(s.schemas is schemas for s in common.branches))
            def invoke(call,indent=False):
                raw=(json.dumps(call,indent=2)+'\n').encode() if indent else P.compact(call)
                reply=common.call(raw);calls.append({'original_call':call,'original_call_sha256':P.source.sha(raw),'reply':reply})
                if reply.get('schema_version')=='lab-api-reply/v2-candidate':
                    assert schemas.valid('api-reply',reply),reply
                    assert reply['contract_profile_binding']==schemas.profile_binding and reply['request_binding']['sha256']==P.source.sha(raw),reply
                return reply
            for operation in ('lab.status','catalog.get'):
                reply=invoke(F.call(channel.context,operation,H.cut(view)),True);check('base-'+operation+'-original-wire-and-shared-profile',reply['kind']=='result')
            check('original-all-34-operation-catalog-preserved',len(schemas.operations)==34 and len(P.SUPPORTED)==34 and set(P.SUPPORTED)==set(schemas.operations))
            def action_call(operation,message):return {'schema_version':'lab-api-call/v2-candidate','call_id':'call:common:'+uuid.uuid4().hex,'operation':operation,'caller_context_ref':action.channel.context['context_ref'],'expected_source_cut':copy.deepcopy(action.cut),'deadline':action.deadline,'max_response_bytes':1048576,'idempotency_key':message.get('idempotency_key') if operation=='action.dispatch' else None,'message':copy.deepcopy(message),'expected_contract_profile_binding':schemas.profile_binding}
            request=action.request(increment=3);call=action_call('action.dispatch',request)
            bad=copy.deepcopy(call);bad['call_id']='call:common:foreign-actor';bad['message']['actor']['principal_ref']='principal:foreign'
            before=snapshot(ar);reply=invoke(bad);check('action-foreign-actor-refused-before-effect',reply.get('kind')=='error' and reply['message']['code']=='unauthorized' and snapshot(ar)==before)
            reply=invoke(action_call('action.evaluate',request),True);check('action-real-permission-evaluation',reply.get('kind')=='result' and reply['message']['posture']=='permitted')
            reply=invoke(call,True);check('action-real-tool-through-common-surface',reply.get('kind')=='result' and reply['message']['posture']=='completed' and AS.regular_json(ar/'ledger/counter.json')['value']==3)
            result=copy.deepcopy(reply['message']);before=snapshot(ar);again=copy.deepcopy(call);again['call_id']='call:common:exact-retry';reply=invoke(again)
            check('action-shared-profile-exact-retry-no-redispatch',reply.get('kind')=='result' and reply['message']==result and snapshot(ar)==before)
            bad=action_call('action.evaluate',request);bad['expected_contract_profile_binding']={'ref':'profile:foreign','sha256':'0'*64};before=snapshot(ar);reply=invoke(bad)
            check('action-other-profile-refused-without-effect',reply.get('kind')=='error' and reply['message']['code']=='invalid-contract' and snapshot(ar)==before)
            checkpoint=governance.checkpoint_call('common-checkpoint');reply=invoke(checkpoint,True)
            check('governance-real-signed-checkpoint-shared-profile',reply.get('kind')=='result' and reply['message']['result']=='pass' and governance.host.document(reply['message']['checks'][0]['evidence_bindings'][0])['all_required_members_authorized'] is True)
            result=copy.deepcopy(reply['message']);before=snapshot(gr);again=copy.deepcopy(checkpoint);again['call_id']='call:common:governance-retry';reply=invoke(again)
            check('governance-exact-retry-no-new-record',reply.get('kind')=='result' and reply['message']==result and snapshot(gr)==before)
            reply=invoke(governance.capability_call('common-capability'),True)
            check('governance-candidate-capability-without-activation',reply.get('kind')=='result' and reply['message']['authority_effect']=='none')
            inspected={'schema_version':'lab-operation-inspect-request/v1-candidate','request_ref':'request:common:inspect','actor':copy.deepcopy(action.actor),'lookup':{'operation':'action.dispatch','idempotency_key':request['idempotency_key']},'budget':{'max_actions':0,'max_input_bytes':65536,'max_output_bytes':1048576,'deadline':action.deadline},'authority_effect':'none'}
            reply=invoke(action_call('operation.inspect',inspected),True)
            check('action-owned-generic-inspection-through-common-surface',reply.get('kind')=='result' and reply['message']['posture']=='completed' and reply['message']['operation']=='action.dispatch')
            inspected=copy.deepcopy(inspected);inspected['actor']=governance.actor;inspected['lookup']={'operation':'checkpoint.resolve','idempotency_key':'common-checkpoint'}
            reply=invoke(governance.call('operation.inspect',inspected,None),True)
            check('governance-owned-generic-inspection-through-common-surface',reply.get('kind')=='result' and reply['message']['posture']=='completed' and reply['message']['operation']=='checkpoint.resolve')
            foreign=action_call('action.evaluate',request);foreign['caller_context_ref']=channel.context['context_ref'];before=snapshot(ar);reply=invoke(foreign)
            check('base-context-cannot-inherit-action-authority',reply.get('kind')!='result' and snapshot(ar)==before)
            class Impostor:
                pass
            fake=Impostor();fake.schemas=schemas;fake.profile_binding=schemas.profile_binding;fake.call=actions.call;fake.channel=action.channel
            try:I.IntegrationService(base,action_service=fake)
            except ValueError:check('duck-typed-branch-implementation-refused',True)
            else:raise AssertionError('impostor accepted')
            action.runtime.source();governance.host.guard();schemas.guard()
    except BaseException:failure=traceback.format_exc()
    guard_failure=None
    try:G.verify(args.source)
    except BaseException:guard_failure=traceback.format_exc()
    value={'schema_version':'lab-common-operator-qualification/v1-candidate','result':'PASS' if failure is None and guard_failure is None and len(checks)==16 else 'FAIL','checks':checks,'actual_calls':calls,'failure':failure,'exit_guard_error':guard_failure,'owned_fixture_removed':owned is not None and not owned.exists(),'files':[bind(api/'source-manifest.json'),bind(api/'contract-profile.json'),bind(Path(__file__).resolve())],'whole_API_qualified':False,'human_pilot_complete':False,'actual_owner_outcome':None,'task_complete':False,'goal_complete':False,'authority_effect':'none','claim_ceiling':'Actual selected shared-profile dispatcher, base reads, owned Action dispatch/retry, signed checkpoint and candidate capability only. Full regression, all-operation paths, machine transport and human pilot remain separate.'}
    with report.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'checks':len(checks),'failure':failure,'exit_guard_error':guard_failure,'report':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
