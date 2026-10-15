"""Exact candidate package joins; no dispatch, admission or implied global edge."""
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE/'workflows'))
import research as contracts
from research import ROOT,byte_sha,encoded,parse,require,SCOPE

UPSTREAM={
    'W03':('examples/engineering/receipts/0002.json','fd088051c598beda2e186c0186b0d922bf06b06782e937fc8f14639b5a442004'),
    'W04':('examples/research/receipts/0002.json','20fb853bbf599d567c2723fc0734a37fd1bdaf7b20211c5cd26a358ff4edf742'),
    'W05':('failures/receipts/0004.json','809855809498495ce6595e4a41c9cb6313a3b8126b82c06557505eac3b0c7fc3'),
    'W06':('learning/receipts/0002.json','b1bce82b765b9f22a525dee0fa74d96f96ae3a8fe0b7fc0201e7325f695a9cd4')}
DOMAINS=frozenset({'engineering','research','failure','learning'})


def binding(path):
    path=Path(path)
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':byte_sha(path.read_bytes())}


def bound(row):
    require(type(row)==dict and set(row)=={'path','sha256'},'closed exact byte binding required')
    p=ROOT/row['path']
    require(not Path(row['path']).is_absolute() and p.resolve().is_relative_to(ROOT)
        and p.is_file() and not p.is_symlink() and not any(x.is_symlink() for x in p.parents),'selected original path unsafe')
    raw=p.read_bytes();require(byte_sha(raw)==row['sha256'],'selected original bytes changed')
    return raw


def emit(path,value):
    p=Path(path)
    with p.open('xb') as stream:stream.write(encoded(value))


def row(path,ref,kind,role):
    value=parse(Path(path).read_bytes());contracts.validate(value,kind)
    require(ref.startswith(contracts.ident(value)+'@'),'exact row identity differs')
    return {**binding(path),'version_ref':ref,'kind':kind,'role':role}


def verify_upstream():
    selected={}
    for task,(rel,sha) in UPSTREAM.items():
        path=PACKAGE/rel;require(byte_sha(path.read_bytes())==sha,'independent upstream receipt differs')
        receipt=parse(path.read_bytes())
        require(receipt['result']=='PASS' and receipt['task_complete'] and receipt['actual_owner_outcome'] is None,'upstream scope incomplete/authority differs')
        for r in receipt['files']+receipt.get('source_bindings',[])+[binding(path)]:
            selected_raw=bound({'path':r['path'],'sha256':r['sha256']})
            require(r['path'] not in selected or selected[r['path']]['sha256']==byte_sha(selected_raw),'conflicting combined source pins')
            selected[r['path']]={'path':r['path'],'sha256':r['sha256']}
    return list(selected.values())


def verify_records(case):
    require(case['domain'] in DOMAINS and case['authority_effect']=='none' and case['actual_owner_outcome'] is None,'case authority/domain differs')
    require(case['canonical_effects_applied']==0 and case['case_id'],'candidate case boundary differs')
    records={};rows={}
    for r in case['records']:
        require(r['role'] in {'input','output','actor'},'case row role undeclared')
        value=parse(bound({'path':r['path'],'sha256':r['sha256']}));contracts.validate(value,r['kind'])
        ref=r['version_ref'];require(ref.startswith(contracts.ident(value)+'@') and ref not in records,'case exact revision ambiguous')
        if 'version' in value:require(ref==contracts.ref(value),'case literal version differs')
        if r['role']=='output':
            require(value.get('authority_effect')=='none','output supplies admission authority')
            if 'lifecycle_state' in value:require(value['lifecycle_state']=='candidate','output carrier lifecycle promoted')
            else:require(value.get('status')=='candidate-unadmitted','legacy output lacks explicit candidate package posture')
        records[ref]=value;rows[ref]=r
    if 'actor_evidence' in case:
        for actor in parse(bound(case['actor_evidence'])):
            value=actor['original_record'];require(byte_sha(encoded(value))==actor['sha256'],'compound actor original differs')
            contracts.validate(value,value['kind']);ref=actor['version_ref']
            require(ref.startswith(contracts.ident(value)+'@') and ref not in records,'actor revision ambiguous')
            records[ref]=value;rows[ref]={'role':'actor','kind':value['kind']}
    typed=[];kind_gaps=[]
    for ref,value in records.items():
        if value.get('kind')!='typed-relation':continue
        p=value['payload']
        checked=contracts.typed('W07-exact-endpoint',p['relation_kind_ref'],p['source']['version_ref'],p['target']['version_ref'],records,p['qualifiers'])
        require(checked['payload']['source']==p['source'] and checked['payload']['target']==p['target'],'case endpoint identity/kind differs')
        typed.append({'version_ref':ref,'relation_kind_ref':p['relation_kind_ref'],'source':p['source']['version_ref'],
            'target':p['target']['version_ref'],'qualifiers':p['qualifiers'],'result':'PASS'})
        for endpoint in [p['source'],p['target']]:
            source_row=rows[endpoint['version_ref']]
            if source_row['kind'] != endpoint['kind']:
                kind_gaps.append({'relation_ref':ref,'endpoint_ref':endpoint['version_ref'],'declared_endpoint_kind':endpoint['kind'],
                    'selected_carrier_semantic_kind':source_row['kind'],'contract_shape_result':'PASS','signed_runtime_kind_join':'FAIL',
                    'reason':'The explicit C14 represented-subject proposal is not an admitted alias or implemented signed-runtime mapping; compatibility helper normalization cannot supply that implementation.',
                    'route':'O02/O05/R03 declared represented-subject adapter and coupling proof; W08/S02 exact mapping/code review; W07 completion remains open'})
    require(typed,'domain-specific existing typed connections absent')
    # Inline roles select contract-defined participants; they do not create edges.
    inline=[]
    for ref,value in records.items():
        if rows[ref]['role']!='output':continue
        for hint in value.get('relation_refs',[]):
            counterpart=hint['counterpart_ref']
            matches=[r for r in records if r==counterpart or contracts.ident(records[r])==counterpart]
            if matches:
                other=records[matches[0]]
                require(all(contracts.kind(records[r])==hint['counterpart_kind'] for r in matches),'inline role counterpart kind differs')
                left,right=(value,other) if hint['direction']=='source' else (other,value)
                signature=(hint['relation_kind_ref'],contracts.kind(left),contracts.kind(right))
                declared=[r for r in contracts.read(contracts.PAIRS)['exact_pairs'] if
                    (r['relation_kind_ref'],r['source_kind'],r['target_kind'])==signature]
                require(len(declared)==1,'inline candidate hint attempts undeclared global pair')
                disposition='resolved-declared-inline-role' if len(matches)==1 else 'declared-identity-role-multiple-proposed-revisions'
            else:
                require(counterpart.startswith('protocol:'),'unresolved nonprotocol inline counterpart')
                disposition='explicit-unresolved-protocol-role'
            inline.append({'subject_ref':ref,'counterpart_ref':counterpart,'disposition':disposition,
                'candidate_revision_refs':matches,'exact_revision_selected':False,'global_edge_created':False})
    return records,{'records':len(records),'typed_connections':typed,'inline_roles':inline,'runtime_kind_join_gaps':kind_gaps,
        'unqualified_global_merge':False}


def audit_axes(axes):
    require(set(axes)=={'workflow_progress','carrier_lifecycle','admission','commitment','outcome_satisfaction','action_permission'},'status axes collapsed or missing')
    require(axes['carrier_lifecycle']=='candidate' and axes['admission']=='candidate-unadmitted' and axes['commitment'] is None,'candidate axes promoted')
    require(axes['action_permission']=='separate-explicit-host-development-grant','workflow status supplies action authority')


def audit_case(case):
    records,closure=verify_records(case);audit_axes(case['status_axes'])
    for r in case['original_evidence']:bound(r)
    output_refs={r['version_ref'] for r in case['records'] if r['role']=='output'}
    outputs={ref:value for ref,value in records.items() if ref in output_refs}
    kinds={v.get('kind') for v in outputs.values()};domain=case['domain']
    facts=case['facts']
    require(facts['actual_execution'] is True,'generic persistence cannot establish domain execution')
    if domain=='engineering':
        require({'generated-output','implementation','work-outcome-assessment','agent-action','work'}<=kinds,'engineering evidence missing')
        require(facts['assessment_disposition']=='supported' and facts['default_regression_tests']==42,'engineering scoped assessment/regression absent')
        require(facts['implementation_sha256']==byte_sha(bound(case['generated_source'])),'engineering generated original bytes differ')
        require(case['status_axes']['outcome_satisfaction']=='supported','engineering outcome differs')
    elif domain=='research':
        require({'experiment-run','research-run','observation','measurement-result','finding','evaluation'}<=kinds,'research domain evidence missing')
        observations=parse(bound(case['observations']));procedure=parse(bound(case['procedure']))
        evaluated=contracts.evaluate(observations['trials'],procedure)
        require(evaluated==parse(bound(case['assessment'])),'finite research original evidence/assessment differs')
        require(len(observations['trials'])==3 and evaluated['labels']==['parity']*3,'fresh signed comparison incomplete')
        require(case['status_axes']['outcome_satisfaction'] is None,'hypothesis outcome became Work satisfaction')
        require(facts['cache_enabled'] is False and facts['Product_benefit_established'] is False,'finite result overstated')
    elif domain=='failure':
        require({'failure-occurrence','failure-assessment','hypothesis','challenge-event','decision','authority-claim'}<=kinds,'failure/challenge evidence missing')
        index=parse(bound(case['episode_index']));selected=index['selected_refs']
        cause=records[selected['cause']]['payload'];assessment=records[selected['assessment']]['payload']
        resolved=records[selected['challenge_resolved']]['payload']
        require(cause['disposition']=='open' and not records[selected['control']]['payload']['effectiveness_evidence_refs'],'cause/control improperly confirmed')
        require(resolved['resolution_decision_ref']==selected['decision'] and index['challenge_state']=='resolved','exact local contest unresolved')
        require(facts['production_incident_claimed'] is False and facts['owner_outcome'] is None,'controlled fixture promoted to production/owner outcome')
        require(assessment['recovery_posture']=='successor-verified-old-revision-unresolved','old source silently fixed')
    else:
        require({'lesson-application','lesson-outcome-assessment','improvement-target','effect'}<=kinds,'later learning evidence missing')
        index=parse(bound(case['episode_index']))
        require(index['signed_lesson_persisted'] and index['first_Agent_invalidated'] and index['first_memory_erased'],'L1 signed context boundary absent')
        require(index['applications_after_selection']==0 and index['actual_later_application'],'selection collapsed into application')
        require(records[index['application_ref']]['payload']['lesson_revision_ref']==index['lesson_ref'],'exact later lesson differs')
        require(records[index['outcome_ref']]['payload']['lesson_application_ref']==index['application_ref'],'later outcome absent')
        require(index['later_memory_erased'] and index['lesson_promoted'] is False and not index['general_benefit_established'],'learning exceeds scoped evidence')
        require(records[index['unapplied_effect_ref']]['payload']['effective_when'].startswith('only a future exact'),'improvement supplied authority')
    return {'domain':domain,'case_id':case['case_id'],'result':'FLAG' if closure['runtime_kind_join_gaps'] else 'PASS',
        'evidence_coverage':'PASS','status_axes':case['status_axes'],'closure':closure,'facts':facts}


def audit_join(cases):
    require(len(cases)==4 and {c['domain'] for c in cases}==DOMAINS,'all four distinct domain cases required')
    require(len({c['case_id'] for c in cases})==4,'one case reused to establish several domains')
    results=[audit_case(c) for c in cases];by={c['domain']:c for c in cases}
    engineering_sha=by['engineering']['facts']['implementation_sha256']
    require(engineering_sha==byte_sha((PACKAGE/'examples/engineering/packages/0004/registered_evaluator.py').read_bytes()),'new engineering output does not match downstream exact evaluator')
    for domain in ['research','failure','learning']:
        require(by[domain]['facts']['host_evaluator_sha256']==engineering_sha,'consumer used a different host evaluator')
    failed_sha=by['failure']['facts']['old_builder_sha256']
    require(failed_sha==by['learning']['facts']['old_builder_sha256'],'later repair has another source family')
    require(by['learning']['facts']['lesson_source_W05_receipt_sha256']==UPSTREAM['W05'][1],'later lesson source changed')
    collisions=distinguish_proposed_postimages(cases)
    gaps=[gap for case in results for gap in case['closure']['runtime_kind_join_gaps']]
    return {'result':'FLAG' if gaps else 'PASS','evidence_coverage':'PASS','runtime_kind_join_gaps':gaps,
        'cases':results,'case_count':4,'shared_code_join_sha256':engineering_sha,
        'shared_failed_source_sha256':failed_sha,'candidate_postimage_collisions':collisions,
        'canonical_effects_applied':0,'actual_owner_outcome':None,'global_merge_performed':False,
        'general_effectiveness_or_Product_benefit':False}


def distinguish_proposed_postimages(cases):
    """Advisory classification after exact case verification; never merges state."""
    proposed={};collisions=[]
    for case in cases:
        for r in case['records']:
            key=r['version_ref'];old=proposed.get(key)
            if old and old['sha256']!=r['sha256']:
                collisions.append({'version_ref':key,'left_case':old['case_id'],'right_case':case['case_id'],
                    'posture':'separate-uncommitted-proposed-postimages','global_merge_allowed':False,
                    'route':'W08/S02 exact selected targets; R03/W09 run identity adaptation'})
            else:proposed[key]={'case_id':case['case_id'],'sha256':r['sha256']}
    return collisions


def endpoint_inventory_audit():
    registry=contracts.read(contracts.shared.REGISTRY);inventory=contracts.read(contracts.PAIRS)
    current=set(registry['current_by_identity'].values())
    carrier_kinds={r['semantic_kind'] for r in registry['admitted_contracts'] if r['artifact_type_ref'] in current}
    endpoint_kinds={r[k] for r in inventory['exact_pairs'] for k in ['source_kind','target_kind']}
    missing=sorted(endpoint_kinds-carrier_kinds)
    proposals={r['endpoint_kind']:r for r in inventory['endpoint_proposals']}
    require(missing==['method','product','project'],'closed inventory changed; audit new missing kinds explicitly')
    return {'result':'FLAG','current_carrier_semantic_kinds':len(carrier_kinds),'declared_endpoint_kinds':len(endpoint_kinds),
        'without_current_exact_carrier_kind':missing,'explicit_existing_candidate_proposals':[proposals[k] for k in missing],
        'method_route':'S01/C10/S02/R08 exact new carrier admission; no implicit current Method authority',
        'identity_representation_route':'O02/O05/R03 implemented exact represented-subject mapping and coupling proof; S02/R08 review',
        'canonical_aliases_created':0}
