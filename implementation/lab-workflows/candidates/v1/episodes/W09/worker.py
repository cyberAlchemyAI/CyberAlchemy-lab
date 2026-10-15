"""Fresh actual case execution in owned branches with current Agent/Tool guards."""
from dataclasses import asdict
import shutil
import sys
import time
from control import *


def scoped_case(domain,output,selected,inputs=None):
    # Reuse the original catalog implementation; it binds each actual selected input and output.
    sys.path.insert(0,str(PACKAGE/'tests'))
    import integration_worker
    if domain=='learning':return integration_worker.prepare_case(domain,output)
    original_contract=integration_worker.prepare_case
    # The catalog's hard-coded original input selection is retained separately.
    case=original_contract(domain,output)
    old_paths={(PACKAGE/('examples/engineering/packages/0004' if domain=='engineering' else 'examples/research/packages/0007')/r['path']).as_posix()
        for r in load(PACKAGE/('examples/engineering/packages/0004/input-manifest.json' if domain=='engineering' else 'examples/research/packages/0007/selection.json'))['records']}
    case['records']=[r for r in case['records'] if (ROOT/r['path']).as_posix() not in old_paths]
    fresh=load(inputs/('input-manifest.json' if domain=='engineering' else 'selection.json'))
    for r in fresh['records']:
        case['records'].append(integration_worker.row(inputs/r['path'],r['version_ref'],r['kind'],'input'))
    if domain=='research':case['procedure']=bind(inputs/fresh['procedure']['path'])
    return case


def runtime_sources(selected,domain):
    rows=[r['generated_binding'] for r in selected['constructor_recipes']]+[bind(HERE/'control.py'),bind(Path(__file__)),bind(SELECTION_PATH),selected['execution_authorization_binding']]
    # Exact guard inputs include the inspected executable helpers and carrier registry.
    paths=list((PACKAGE/'authority').glob('*.py'))+list((PACKAGE/'learning').glob('*.py'))+[PACKAGE/'receipts/action-boundaries/fixtures.py',
        PACKAGE/'tools/counter.py',PACKAGE/'examples/engineering/behavior.py',PACKAGE/'examples/engineering/run_episode.py',
        PACKAGE/'examples/research/run_episode.py',PACKAGE/'design/transition-contracts.json',
        ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json']
    rows += [bind(p) for p in paths]
    model=load(ROOT/selected['workflow_review_binding']['path']);member=next(m for m in model['members'] if m['scope'].get('workflow')==domain)
    rows += member['targets']+[selected['workflow_review_binding']]
    if domain in selected['inputs']:
        b=selected['inputs'][domain]['selection_binding'];rows.append(b);folder=(ROOT/b['path']).parent
        for r in load(ROOT/b['path'])['records']:rows.append({'path':str((folder/r['path']).relative_to(ROOT)),'sha256':r['sha256']})
    return list({r['path']:r for r in rows}.values())


def run(domain,output):
    selected=selection();output=Path(output).resolve();require(domain in ('engineering','research','learning') and output.is_relative_to(HERE/'runs')
        and not output.exists(),'fresh selected W09 domain output required')
    output.parent.mkdir(parents=True,exist_ok=True);start=time.perf_counter();runtime,engine,research=select_sources(selected,domain)
    sources=runtime_sources(selected,'operational-learning' if domain=='learning' else domain)
    if domain=='learning':
        original_factory=runtime.host_fixture;hosts=[]
        def fresh_host(**kwargs):
            f=original_factory(**kwargs);phase='first' if not hosts else 'later'
            f=rebind(f,selected['run_namespace'],phase,guard=kwargs.get('context_guard'),handles=kwargs.get('handles'),clock=kwargs.get('now'),
                owned_store_scope=kwargs.get('store_scope'),source_bindings=sources)
            hosts.append(f);return f
        runtime.host_fixture=fresh_host
        index=runtime.perform(output,Path(selected['native_executable_binding']['path']))
        require(len(hosts)==2 and all(f.session.closed and not f.session._memory for f in hosts),'actual Learning host Sessions remain')
        case=scoped_case(domain,output,selected)
        actual=load(output/'episode-index.json');fresh_ref=actual['lesson_ref']
        require(selected['run_namespace'] in fresh_ref and fresh_ref!=load(ROOT/selected['historical_Lesson_binding']['path'])['node_id']+'@candidate.1',
            'fresh scoped Lesson reused expired revision identity')
        result={'result':'PASS','domain':domain,'source_context_mode':'real-signed-Lesson-new-Agent-context','fresh_Lesson_ref':fresh_ref,
            'new_Agent_handles':actual['new_Agent_handles'],'first_Agent_handles':actual['first_Agent_handles'],'actual_later_application':actual['actual_later_application'],
            'first_memory_erased':actual['first_memory_erased'],'later_memory_erased':actual['later_memory_erased'],'later_Agent_closed':actual['later_Agent_closed'],
            'owned_store_and_key_removed':True,'historical_expired_Lesson_changed':False,'hosts':[{'grant_original_sha256':sha(f.grant.evidence_original),
                'actor_refs':{k:f.ref(k) for k in f.by_kind},'Session_closed':f.session.closed,'memory_erased':not f.session._memory} for f in hosts]}
    else:
        sys.path.insert(0,str(PACKAGE/'examples/learning-loop'));sys.path.insert(0,str(ROOT/'implementation/lab-continuity/candidates/v1'))
        from run_episode import continuity,provision,VerifiedLegacyReadStore,CurrentCutGuard,public_archive
        _,_,snapshot=continuity.selected_source();store_id='W09-'+domain+'-'+selected['run_namespace']
        scope=provision.CandidateScope(store_id,'role:candidate-W09-operator','scope:lab-runtime-local:'+store_id)
        branch=provision.CandidateBranch(scope);agent=None;hosts=[]
        try:
            native_root=branch.root/'native';native_root.mkdir();native=continuity.diagnostic_native_fixture(native_root,Path(selected['native_executable_binding']['path']),snapshot)
            store=VerifiedLegacyReadStore(branch.store_path,ROOT,ROOT,branch.pins)
            agent=continuity.session_for(store,snapshot,native,'product:cyberalchemy-lab');clock=[time.time()]
            guard=CurrentCutGuard(agent,branch.store_path,native_root,clock=clock);pack=guard.pack
            require(not agent.core._memory and pack['short_memory_persisted'] is False,'new Agent did not start empty')
            agent.note('W09 ephemeral case thought')
            factory=runtime.fixture_for if domain=='engineering' else runtime.fixture
            def fresh_factory(*args,**kwargs):
                f=factory(*args,**kwargs)
                if domain=='engineering' and kwargs.get('registered') is False:return f
                f=rebind(f,selected['run_namespace'],domain,guard=guard,handles=(agent.instance_id,agent.session_id),clock=clock,
                    owned_store_scope=scope.scope_ref,source_bindings=sources,
                    adapter_binding=bind(SELECTION_PATH.parent/'sources'/('engineering.py' if domain=='engineering' else 'research.py')))
                f.session.note('W09 ephemeral host thought');hosts.append(f);return f
            if domain=='engineering':runtime.fixture_for=fresh_factory
            else:runtime.fixture=fresh_factory
            row=selected['inputs'][domain];inputs=(ROOT/row['selection_binding']['path']).parent
            if domain=='engineering':
                manifest=load(inputs/'input-manifest.json');regression=runtime.run_default_regression(inputs/'registered_evaluator.py',manifest['output_source_sha256'],output.parent/'engineering-default-regression.log')
                require(regression['result']=='PASS' and regression['tests']==42,'fresh preserved authority regression failed')
                emit(output.parent/'engineering-default-regression.json',regression)
                runtime.execute_episode(inputs,row['selection_binding']['sha256'],output,regression)
            else:runtime.execute_episode(inputs,row['selection_binding']['sha256'],output)
            require(len(hosts)==1 and hosts[0].session.closed and not hosts[0].session._memory,'actual case host Session remains')
            # The old wrapper records its blueprint cut. The separate execution context and current run make both cuts inspectable.
            legacy=load(output/'workflow-run.json');protocol=copy.deepcopy(legacy);protocol['run_ref']='protocol:W09:'+selected['run_namespace']+':'+domain
            model=load(ROOT/selected['workflow_review_binding']['path']);member=next(m for m in model['members'] if m['scope'].get('workflow')==domain)
            protocol['definition_binding']={'ref':member['targets'][0]['path'],'sha256':member['targets'][0]['sha256']}
            data=branch.store.replay(require_current=True)
            profile_path=ROOT/'implementation/lab-runtime/v2/profile.json'
            require(load(profile_path)==load(branch.store_path/'baseline.json')['profile'],'actual source profile differs')
            protocol['source_cut']={'store_ref':data['config']['store_id'],'branch_ref':'protocol:W09:'+selected['run_namespace']+':'+domain,
                'commit_sequence':data['head']['sequence'],'commit_sha256':data['head']['transaction_digest'],'source_profile_sha256':sha(profile_path.read_bytes()),'streams':[]}
            emit(output/'current-workflow-run.json',protocol)
            emit(output/'execution-context.json',pack);emit(output/'host-permission.json',load_bytes(hosts[0].grant.evidence_original))
            guard();pins=branch.pins;public_archive(branch,pins,data,output/'context-branch.snapshot');shutil.copytree(native_root,output/'native-originals')
            emit(output/'native-pins.json',{'pins':asdict(native.pins)})
            agent.close();require(agent.closed and not agent.core._memory,'actual Agent memory remains')
            case=scoped_case(domain,output,selected,inputs)
            result={'result':'PASS','domain':domain,'source_context_mode':'actual-current-D75-Project-native-Context-Ontology','source_context_binding':bind(output/'execution-context.json'),
                'blueprint_protocol_binding':bind(output/'workflow-run.json'),'current_workflow_protocol_binding':bind(output/'current-workflow-run.json'),
                'context_archive_binding':bind(output/'context-branch.snapshot'),'candidate_scope':asdict(scope),'replay_pins':asdict(pins),
                'new_Agent_handles':{'instance_ref':pack['instance_id'],'session_ref':pack['session_id']},'Agent_closed':agent.closed,'Agent_memory_erased':not agent.core._memory,
                'hosts':[{'grant_original_sha256':sha(f.grant.evidence_original),'actor_refs':{k:f.ref(k) for k in f.by_kind},'Session_closed':f.session.closed,'memory_erased':not f.session._memory} for f in hosts]}
        finally:
            if agent:agent.close()
            for f in hosts:f.session.close()
            branch.close()
        require(branch.closed and not branch.root.exists(),'owned context branch/private key remains');result['owned_store_and_key_removed']=True
    emit(output/'case.json',case);result.update(case_binding=bind(output/'case.json'),selection_binding=bind(SELECTION_PATH),
        run_namespace=selected['run_namespace'],duration_seconds=time.perf_counter()-start,authority_effect='none',actual_owner_outcome=None,
        canonical_effects_applied=0,runtime_activation=False,human_pilot=False,private_key_exported=False,Session_memory_exported=False)
    emit(output/'result.json',result);print(encoded(result).decode(),end='')


def load_bytes(raw):
    import json
    return json.loads(raw)


if __name__=='__main__':
    require(len(sys.argv)==3,'usage: worker.py domain fresh-output');run(sys.argv[1],sys.argv[2])
