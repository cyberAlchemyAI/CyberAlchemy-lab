"""Independent source, observation, typed-connection and cold-context reconstruction."""
from control import *
import tempfile
from dataclasses import asdict
from referencing import Registry,Resource
from jsonschema import Draft202012Validator
sys.path.insert(0,str(PACKAGE/'tests'))
import integration_support as parent
from signed import coupling,engine_pins
CASE_PATHS={'engineering':HERE/'runs/0003/scenarios/engineering','research':HERE/'runs/0001/scenarios/research','learning':HERE/'runs/0004/scenarios/learning'}
SIGNED_PATHS={'engineering':HERE/'runs/0003/signed/engineering','research':HERE/'runs/0001/signed/research'}

def checked(condition,message):require(condition,message)
def original_value(binding):return load(ROOT/binding['path']) if original(binding) else None

def validate_protocol(p):
    paths=[ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json']
    registry=Registry().with_resources([(load(q)['$id'],Resource.from_contents(load(q))) for q in paths])
    Draft202012Validator(load(PACKAGE/'schemas/workflow-run.schema.json'),registry=registry).validate(p)

def corrected_protocol(domain,folder):
    source=load(CASE_PATHS[domain]/'current-workflow-run.json');before=bind(CASE_PATHS[domain]/'current-workflow-run.json');v=copy.deepcopy(source)
    v['gaps'][0]['reason']='The actual signed current D75 context is separate from this run-scoped selection and proposed domain postimages. Those selections remain uncommitted candidate files.'
    validate_protocol(v);emit(folder/(domain+'-current-workflow-run.json'),v)
    emit(folder/(domain+'-protocol-correction.json'),{'original_binding':before,'corrected_binding':bind(folder/(domain+'-current-workflow-run.json')),
        'exact_change':'Replace only the inherited C12 gap explanation; preserve actual source cut, actor, events, selected refs and independent status axes.',
        'domain_actions_reexecuted':0,'canonical_effects_applied':0,'actual_owner_outcome':None,'authority_effect':'none'})
    return bind(folder/(domain+'-current-workflow-run.json'))

def signed_closure(domain,case):
    root=SIGNED_PATHS[domain];result=load(root/'result.json');expected=load(root/'expected-replay.json');metadata=load(root/'original-source-witnesses.json')
    case_binding=bind(CASE_PATHS[domain]/'case.json');pins=engine_pins()
    require(result['result']=='PASS' and result['source_case_binding']==metadata['case_binding']==expected['case_binding']==case_binding
        and result['owned_store_and_key_removed'] and result['idempotent_retry'] and result['signed_transactions']==1 and result['distinct_Decision_cores']==3,
        'real exact selected signed coupling evidence differs')
    with tempfile.TemporaryDirectory(prefix='cal-W09-signed-cold-') as tmp,coupling.engine(pins) as handle:
        data=coupling.restore_archive(root/'branch.snapshot',expected['archive_binding']['sha256'],Path(tmp)/'store',pins);p=data['projection']
        require(handle.common.digest(p)==expected['projection_sha256'] and [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],
            'fresh signed replay differs from observed projection/transactions')
        tx=data['transactions'][-1];require(tx['proposal']==load(root/'proposal.json') and tx['approval']==load(root/'approval.json'),'actual signed cores/postimages differ')
        refs={t['version_ref'] for t in tx['proposal']['targets']};cores=tx['decision_cores']
        require(len(refs)==len(cores)==3 and len({c['decision_ref'] for c in cores})==3,'signed Decision partition collapsed')
        relation=p['subjects'][expected['relation_ref']]['record'];handle.operations.validate_relation(relation,p)
        payload=relation['payload'];require(refs=={expected['relation_ref'],payload['source']['version_ref'],payload['target']['version_ref']},'signed target/endpoints differ')
        views=[]
        for ref in refs:
            rows=[r for r in case['records'] if r['version_ref']==ref];require(len(rows)==1,'case endpoint/relation ambiguous')
            r=rows[0];binding={k:r[k] for k in ['path','sha256']};value=original_value(binding);actual=p['subjects'][ref]
            w=next(w for w in metadata['selected_records'] if w['version_ref']==ref)
            require(actual['record']==value and actual['kind']==r['kind'] and actual['effective_state']=='local-admitted-current'
                and w['source_binding']==binding and w['record_rewritten'] is False and w['original_structural_sha256']==handle.common.digest(value),
                'selected original bytes/raw carrier kind or source eligibility differs')
            carrier=p['contracts'][actual['carrier_ref']];require(carrier['lifecycle_state'] in ['admitted-current','local-admitted-current'],'carrier not eligible')
            if r['kind']=='typed-relation':continue
            if r['kind']=='project-identity':require(value['project_id']==data['config']['scope_ref'] and 'scope_ref' not in value,'Project identity namespace changed')
            else:require(value['scope_ref']==data['config']['scope_ref'],'endpoint scope changed')
            mapping=handle.mapping.mapping_for(actual['carrier_ref'],p)
            if mapping:
                b=mapping['descriptor_binding'];require(carrier['artifact_path']==b['path'] and carrier['artifact_sha256']==b['sha256']
                    and carrier['artifact']==original_value(b)==p['documents'][b['path']],'mapped exact descriptor differs')
            view=handle.mapping.explain(actual,p);require(view['raw_subject_rewritten'] is False,'source carrier kind rewritten');views.append(view)
        require(sorted(views,key=lambda r:r['version_ref'])==sorted(expected['endpoint_views'],key=lambda r:r['version_ref']),'represented endpoint views differ')
    return {'result':'PASS','domain':domain,'case_binding':case_binding,'archive_binding':expected['archive_binding'],'relation_ref':expected['relation_ref'],
        'raw_Project_kind_preserved':True,'endpoint_views':views,'distinct_Decision_cores':3,'domain_actions_reexecuted':0,'private_keys_restored':False}


def restore_genesis(path,pin,dest,pins):
    import base64
    from lab_runtime.replay import ReplayPins,full_replay
    raw=Path(path).read_bytes();require(sha(raw)==pin and len(raw)<=20971520,'bounded independent genesis archive pin differs')
    v=load(path);require(v['schema_version']=='lab-public-original-branch-archive/v1-candidate' and v['project_pins']==pins
        and v['authority_effect']=='none' and v['actual_owner_outcome'] is None and not v['private_key_included'] and not v['Session_memory_included'],
        'public original archive authority/custody differs')
    names={'config.json','baseline.json','HEAD.json','transactions/0000000000.json'}
    require(set(v['files'])==names and not dest.exists() and not dest.is_relative_to(ROOT),'exact fresh genesis-only archive closure required')
    dest.mkdir();(dest/'transactions').mkdir()
    for name,b in v['files'].items():
        require(set(b)=={'sha256','base64_original_bytes'},'closed original archive file binding required')
        original_bytes=base64.b64decode(b['base64_original_bytes'],validate=True);require(sha(original_bytes)==b['sha256'],'archived original bytes differ')
        with (dest/name).open('xb') as stream:stream.write(original_bytes)
    data=full_replay(dest,ROOT,ROOT,ReplayPins(**pins),require_current=True)
    require(data['head']['sequence']==0 and len(data['transactions'])==1,'archive was not actual signed genesis')
    return data

def cold_context(domain):
    sys.path.insert(0,str(PACKAGE/'examples/learning-loop'));sys.path.insert(0,str(ROOT/'implementation/lab-continuity/candidates/v1'))
    from run_episode import continuity,VerifiedLegacyReadStore,NativeReadStore,NativePins,ReplayPins
    root=CASE_PATHS[domain];meta=load(root/'result.json');original(meta['context_archive_binding']);oldpack=load(root/'execution-context.json')
    native_root=root/'native-originals';native=NativeReadStore(native_root/'semantic',native_root/'governance',load(native_root/'request.json'),
        Path(selection()['native_executable_binding']['path']),NativePins(**load(root/'native-pins.json')['pins']))
    with tempfile.TemporaryDirectory(prefix='cal-W09-context-cold-') as tmp:
        dest=Path(tmp)/'store';data=restore_genesis(ROOT/meta['context_archive_binding']['path'],meta['context_archive_binding']['sha256'],dest,meta['replay_pins'])
        require(data['head']['transaction_digest']==oldpack['head'],'archived current context cut differs')
        _,_,snapshot=continuity.selected_source();store=VerifiedLegacyReadStore(dest,ROOT,ROOT,ReplayPins(**meta['replay_pins']))
        agent=continuity.session_for(store,snapshot,native,'product:cyberalchemy-lab')
        try:
            fresh=agent.context();require(fresh['head']==oldpack['head'] and fresh['session_id']!=oldpack['session_id']
                and fresh['instance_id']!=oldpack['instance_id'] and not agent.core._memory and fresh['short_memory_persisted'] is False,'cold Agent inherited memory/handles or different Project state')
        finally:agent.close()
        require(agent.closed and not agent.core._memory,'cold Agent memory remains')
    return {'result':'PASS','domain':domain,'verified_current_Project_cut':oldpack['head'],'new_Agent_context':True,'Agent_closed':True,
        'memory_erased':True,'private_key_restored':False,'domain_actions_reexecuted':0,'native_domain_mapping':False}

def audit():
    s=selection();cases={d:load(p/'case.json') for d,p in CASE_PATHS.items()};checks=[];audits=[];handles=[]
    for d,p in CASE_PATHS.items():
        meta=load(p/'result.json');require(meta['result']=='PASS' and meta['domain']==d and meta['owned_store_and_key_removed'] and not meta['private_key_exported']
            and not meta['Session_memory_exported'] and meta['actual_owner_outcome'] is None and meta['canonical_effects_applied']==0 and not meta['human_pilot'],
            'actual candidate execution boundary not closed')
        for h in meta['hosts']:require(h['Session_closed'] and h['memory_erased'],'actual host memory remains')
        require(meta.get('Agent_closed',meta.get('later_Agent_closed')) and meta.get('Agent_memory_erased',meta.get('later_memory_erased')),'Agent memory remains')
        handles.append(meta['new_Agent_handles']['session_ref']);audits.append(parent.audit_case(cases[d]))
        checks.append({'test':'actual '+d+' candidate and exact observation/contract closure','result':'PASS'})
    require(len(set(handles))==3,'one runtime Agent reused across domains')
    collisions=parent.distinguish_proposed_postimages(list(cases.values()));require(not collisions,'fresh candidate postimages still conflict')
    gaps=[g for a in audits for g in a['closure']['runtime_kind_join_gaps']];require(len(gaps)==2 and all(g['selected_carrier_semantic_kind']=='project-identity' for g in gaps),'new undeclared runtime kind gap')
    signed=[signed_closure(d,cases[d]) for d in ['engineering','research']]
    require({r['relation_ref'] for r in signed}=={r['relation_ref'] for r in gaps},'not every actual runtime gap closed')
    checks.append({'test':'exact raw carrier/represented endpoint coupling and independent signed cold replay','result':'PASS'})
    context=[cold_context(d) for d in ['engineering','research']]
    checks.append({'test':'independent actual Engineering/Research Project/native context reconstruction and erased Sessions','result':'PASS'})
    # Select the exact successor constructors before the Learning cold consumer imports its helpers.
    import control_v2
    ls=control_v2.selection();runtime,_,_=control_v2.select_sources(ls,'learning');root=CASE_PATHS['learning']
    index=load(root/'episode-index.json');records={r['version_ref']:load(root/r['path']) for r in index['records']}
    lesson=records[index['lesson_ref']];expiry=datetime.fromisoformat(lesson['payload']['expires_at']).timestamp()
    began=datetime.fromisoformat(load(root/'context-before.json')['generated_at'].replace('Z','+00:00')).timestamp()
    require(index['lesson_ref']!=load(ROOT/s['historical_Lesson_binding']['path'])['node_id']+'@candidate.1' and ':learning-retry:' in index['lesson_ref']
        and 3300<expiry-began<3900,'historical Lesson expiry/identity reused or fresh clock not bound')
    require(index['applications_after_selection']==0 and index['actual_later_application'] and index['first_Agent_invalidated']
        and index['first_memory_erased'] and index['later_memory_erased'] and index['new_Agent_handles']!=index['first_Agent_handles'],'selection/application or Session boundary collapsed')
    cold=runtime.cold(root/'episode-index.json',sha((root/'episode-index.json').read_bytes()),Path(s['native_executable_binding']['path']))
    require(cold['result']=='PASS' and cold['applications_reexecuted']==0 and cold['new_Agent_lesson_context'],'fresh cold Learning replay failed')
    checks.append({'test':'new current scoped Lesson, actual later repair, bounded assessment, cold state and Session erasure','result':'PASS'})
    require(load(CASE_PATHS['research']/'assessment.json')['disposition'] in ['positive','negative','inconclusive'],'research outcome absent')
    require(not index['general_benefit_established'] and not index['lesson_promoted'] and index['causal_claim_ceiling']==runtime.CAUSAL_CEILING,'cause/benefit/promotion fabricated')
    checks.append({'test':'negative Research result and retained Learning counterevidence with one-case causal ceiling','result':'PASS'})
    return {'schema_version':'lab-W09-actual-integration-audit/v1-candidate','result':'PASS','cases':audits,'case_bindings':[bind(p/'case.json') for p in CASE_PATHS.values()],
        'new_runtime_handles_distinct':True,'candidate_postimage_collisions':collisions,'typed_connections_checked':sum(len(a['closure']['typed_connections']) for a in audits),
        'signed_closures':signed,'context_reconstruction':context,'cold_Learning':cold,'checks':checks,'remaining_runtime_gaps':0,
        'canonical_effects_applied':0,'actual_owner_outcome':None,'authority_effect':'none','human_pilot':False,'all_Sessions_closed':True,'candidate_only':True}
if __name__=='__main__':
    require(len(sys.argv)==2,'usage: audit.py fresh-output');folder=Path(sys.argv[1]).resolve();require(folder.is_relative_to(HERE/'runs') and not folder.exists(),'fresh audit output required');folder.mkdir(parents=True)
    result=audit();result['corrected_protocols']=[corrected_protocol(d,folder) for d in ['engineering','research']]
    emit(folder/'result.json',result);print(encoded({'result':'PASS','result_binding':bind(folder/'result.json'),'typed_connections':result['typed_connections_checked']}).decode(),end='')
