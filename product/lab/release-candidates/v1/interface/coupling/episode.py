"""Real owned signed transactions over exact W07 endpoint postimages."""
from dataclasses import asdict
import base64
import copy
import importlib
import re
import subprocess
import time
from loader import *

JOIN = ROOT / 'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0003/join-index.json'
JOIN_SHA = '181cc2f808558db0909768df19eff5297fcd1c4ba9607a9031bad60e4b78e910'
EXAMPLES = ROOT / 'product/lab/release-candidates/v1/examples/operator-journeys/coupling'


def emit(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value))


def proposal_for(store, proposal_id, targets):
    data = store.replay(require_current=True); cfg = data['config']
    return {'schema_version':'lab-runtime-proposal/v1','proposal_id':proposal_id,
        'expected_head':data['head']['transaction_digest'],'source_snapshot_digest':cfg['source_snapshot_digest'],
        'scope_ref':cfg['scope_ref'],'policy_ref':cfg['policy_ref'],'challenge_route':cfg['challenge_route'],
        'schemas':{},'targets':targets}


def target(ref, carrier, record, decision, *, category='artifact-instance', predecessor=None):
    return {'category':category,'operation':'revise' if predecessor else 'admit','version_ref':ref,
        'carrier_ref':carrier,'record':record,'predecessor_ref':predecessor,'decision_ref':decision,'contract':None}


def selected_cases():
    require(sha(JOIN.read_bytes()) == JOIN_SHA, 'independent W07 join pin differs')
    join = parse(JOIN.read_bytes()); cases = {}
    for binding in join['cases']:
        case = parse(original(binding)); cases[case['domain']] = (binding,case)
    require(set(cases) == {'engineering','research','failure','learning'}, 'exact original case partition required')
    return cases


def carrier_for(projection, kind):
    rows = [(ref,c) for ref,c in projection['contracts'].items()
        if c['semantic_kind'] == kind and c['lifecycle_state'] in ('admitted-current','local-admitted-current')]
    require(len(rows)==1, 'current exact source carrier unresolved: '+kind)
    return rows[0][0]


def case_targets(handle, store, domain, case):
    wanted = {'engineering':'typed-relation:lab-engineering:engineering-evidence-membership@candidate.1',
        'research':'typed-relation:lab-research:experiment-project@candidate.1'}[domain]
    relation_row = next(r for r in case['records'] if r['version_ref']==wanted)
    relation = parse(original({k:relation_row[k] for k in ('path','sha256')}))
    projection = store.replay()['projection']; targets=[]; selected=[]
    for endpoint in (relation['payload']['source'], relation['payload']['target']):
        row = next(r for r in case['records'] if r['version_ref']==endpoint['version_ref'])
        binding = {k:row[k] for k in ('path','sha256')}; record = parse(original(binding))
        current = [s for s in projection['subjects'].values() if s['identity']==endpoint['ref']
            and s['effective_state'] in ('admitted-current','local-admitted-current')]
        require(len(current)<=1, 'ambiguous original source identity')
        predecessor = current[0]['version_ref'] if current else None
        require(endpoint['version_ref'] not in projection['subjects'], 'case revision already has different source provenance')
        targets.append(target(endpoint['version_ref'], carrier_for(projection,row['kind']), record,
            'decision:R03:'+domain+':endpoint:'+str(len(targets)), predecessor=predecessor))
        selected.append({'version_ref':endpoint['version_ref'],'kind':row['kind'],'source_binding':binding,
            'original_structural_sha256':handle.common.digest(record),'record_rewritten':False,
            'predecessor_ref':predecessor})
    targets.append(target(wanted,carrier_for(projection,'typed-relation'),relation,
        'decision:R03:'+domain+':relation',category='typed-relation'))
    selected.append({'version_ref':wanted,'kind':'typed-relation',
        'source_binding':{k:relation_row[k] for k in ('path','sha256')},
        'original_structural_sha256':handle.common.digest(relation),'record_rewritten':False,'predecessor_ref':None})
    return targets,selected,wanted


def product_targets(handle, store):
    data = store.replay(); p=data['projection']; project=p['state']['payload']['project_ref']
    product=handle.sources.resolve(p['subjects'],'product:cyberalchemy-lab')
    record=copy.deepcopy(product['record']); version=record['product_id']+'@'+record['version']
    require(version not in p['subjects'], 'Product exact body revision already present')
    cap = next(s for s in p['subjects'].values() if s['kind']=='product-capability'
        and s['effective_state']=='admitted-current' and s['record']['product_ref']==product['identity'])
    pair={'source_kind':'product-capability','target_kind':'product'}
    require(pair in p['relation_contracts']['relation.member-of']['payload']['allowed_endpoint_pairs'],
        'selected Product pair not declared')
    relation=copy.deepcopy(p['documents']['authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-project-state.json'])
    typed=carrier_for(p,'typed-relation'); ident='typed-relation:R03:capability-product-membership'
    relation.update(schema_version=p['contracts'][typed]['instance_discriminator']['value'],node_id=ident,
        name='Controlled declared capability membership in exact Product revision',scope_ref=data['config']['scope_ref'],
        lifecycle_state='candidate',owner_ref=data['config']['owner_ref'],evidence_refs=[cap['source']['path'],product['source']['path']],
        claim_ceiling='Controlled signed local coupling example; no Product benefit, capability use, source repository admission or actual owner outcome.')
    relation['payload'].update(relation_kind_ref='relation.member-of',
        source={'kind':'product-capability','ref':cap['identity'],'version_ref':cap['version_ref']},
        target={'kind':'product','ref':product['identity'],'version_ref':version},
        qualifiers={'membership_role':'declared-product-capability'},relation_lifecycle_state='candidate',
        relation_evidence_refs=[product['source']['path']])
    targets=[target(version,product['carrier_ref'],record,'decision:R03:product:identity',predecessor=product['version_ref']),
        target(ident+'@candidate.1',typed,relation,'decision:R03:product:relation',category='typed-relation')]
    witnesses=[{'version_ref':version,'kind':'product-identity','source_binding':product['source'],
        'original_structural_sha256':handle.common.digest(record),'record_rewritten':False,'predecessor_ref':product['version_ref']},
        {'version_ref':ident+'@candidate.1','kind':'typed-relation','source_binding':None,
        'construction_rule':'Exact existing member-of capability/Product pair with closed membership_role; new controlled relation, no original workflow claim.',
        'original_structural_sha256':None,'record_rewritten':False,'predecessor_ref':None}]
    return targets,witnesses,ident+'@candidate.1'


def archive(store, pins):
    data=store.replay(); path=store.path
    names=['config.json','baseline.json','HEAD.json']+[f'transactions/{i:010d}.json' for i in range(data['head']['sequence']+1)]
    return {'schema_version':'lab-R03-private-signed-branch-archive/v1-candidate','authority_effect':'none',
        'actual_owner_outcome':None,'visibility':'private-candidate-store-originals','engine_pins':asdict(pins),
        'config_sha256':sha((path/'config.json').read_bytes()),'baseline_snapshot_digest':data['baseline']['snapshot_digest'],
        'expected_head':data['head']['transaction_digest'],
        'files':{name:{'sha256':sha((path/name).read_bytes()),
            'base64_original_bytes':base64.b64encode((path/name).read_bytes()).decode()} for name in names},
        'private_key_included':False,'Session_memory_included':False,'repository_admission_effect':'none',
        'runtime_activation':False,'source_effects_applied':0}


def restore_archive(path, expected_sha, destination, pins):
    require(sha(Path(path).read_bytes())==expected_sha, 'independent signed archive pin differs')
    value=parse(Path(path).read_bytes()); destination=Path(destination)
    require(value['engine_pins']==asdict(pins), 'archive candidate engine pins differ')
    require(value['authority_effect']=='none' and value['actual_owner_outcome'] is None
        and value['private_key_included'] is value['Session_memory_included'] is value['runtime_activation'] is False
        and value['source_effects_applied']==0, 'archive asserts forbidden state or effects')
    require(not destination.exists() and not destination.is_relative_to(ROOT), 'fresh external cold destination required')
    destination.mkdir(); (destination/'transactions').mkdir()
    for name,b in value['files'].items():
        require(name in ('config.json','baseline.json','HEAD.json')
            or re.fullmatch(r'transactions/[0-9]{10}\.json',name) is not None, 'unselected archived file')
        require(set(b)=={'sha256','base64_original_bytes'}, 'closed archived byte binding required')
        raw=base64.b64decode(b['base64_original_bytes'],validate=True)
        require(sha(raw)==b['sha256'], 'original signed archive bytes differ')
        with (destination/name).open('xb') as stream:stream.write(raw)
    with engine(pins) as handle:
        data=handle.replay_owned(destination,value['config_sha256'],value['baseline_snapshot_digest'],value['expected_head'])
    return data


def frozen_kind_rejection(handle, projection, relation):
    sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation'))
    from lab_runtime.replay import ReplayPins,legacy_runtime
    original_archive=ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
    archive_pins=ReplayPins(**parse(original_archive.read_bytes())['project_pins'])
    name,_,stage=legacy_runtime(ROOT,archive_pins)
    try:
        operations=importlib.import_module(name+'.operations'); rejected=None
        try:operations.validate_relation(relation,projection)
        except Exception as error:rejected=str(error)
        require(rejected is not None and 'endpoint identity/kind mismatch' in rejected,
            'original frozen runtime did not reproduce the raw carrier/endpoint mismatch')
        return {'result':'PASS','original_runtime_rejection':rejected,'original_runtime_modified':False}
    finally:
        stage.cleanup()
        for key in list(sys.modules):
            if key==name or key.startswith(name+'.'):sys.modules.pop(key,None)


def run_one(domain, destination, pins):
    start=time.perf_counter(); destination=Path(destination).resolve(); destination.mkdir(parents=True)
    cases=selected_cases(); case_binding=None
    with tempfile.TemporaryDirectory(prefix='cal-R03-'+domain+'-owned-') as temp,engine(pins) as handle:
        owned=Path(temp); store,key=handle.create_owned(owned,'R03-'+domain,selected_project_scope=True)
        if domain in ('engineering','research'):
            case_binding,case=cases[domain]; targets,witnesses,relation_ref=case_targets(handle,store,domain,case)
        else:
            targets,witnesses,relation_ref=product_targets(handle,store)
        proposal=proposal_for(store,'R03-'+domain,targets)
        before=store.replay(); post,cores=handle.operations.prepare(before['projection'],proposal,
            before['head']['transaction_digest'],before['config'])
        relation=next(t['record'] for t in targets if t['version_ref']==relation_ref)
        rejection=frozen_kind_rejection(handle,post,relation)
        review=store.review(proposal); require(review['target_count']==len(targets),'actual exact review incomplete')
        raw_kind_before=[{k:s[k] for k in ('identity','version_ref','kind','carrier_ref','effective_state')}
            for s in post['subjects'].values() if s['version_ref'] in [t['version_ref'] for t in targets]]
        approval=store.authorize(proposal,key)
        require((key.stat().st_mode&0o777)==0o600,'fixture key permissions incorrect')
        applied=store.apply(proposal,approval); retried=store.apply(proposal,approval)
        require(retried['idempotent'] is True and retried['transaction_digest']==applied['transaction_digest'],
            'same exact signed retry duplicated or changed effect')
        after=store.replay(require_current=True)
        actual=after['projection']['subjects'][relation_ref]
        handle.operations.validate_relation(actual['record'],after['projection'])
        require(actual['record']==relation,'signed local relation body differs from exact target')
        actual_targets=[]
        for t in targets:
            entry=after['projection']['subjects'][t['version_ref']]
            require(entry['record']==t['record'],'signed record differs from original selected postimage')
            actual_targets.append({'version_ref':entry['version_ref'],'carrier_kind':entry['kind'],
                'carrier_ref':entry['carrier_ref'],'identity_ref':entry['identity'],'source_binding':entry['source'],
                'effective_state':entry['effective_state'],'record_structural_sha256':handle.common.digest(entry['record'])})
        endpoint_views=[handle.mapping.explain(handle.sources.resolve(after['projection']['subjects'],
            endpoint['version_ref']),after['projection']) for endpoint in actual['record']['payload'].values()
            if isinstance(endpoint,dict) and set(endpoint)=={'kind','ref','version_ref'}]
        signed_archive=archive(store,pins)
        emit(destination/'branch.snapshot',signed_archive)
        emit(destination/'proposal.json',proposal);emit(destination/'review.json',review)
        emit(destination/'approval.json',approval);emit(destination/'application.json',applied)
        emit(destination/'original-source-witnesses.json',{'case_binding':case_binding,'selected_records':witnesses,
            'original_domain_cases_reexecuted':0,'raw_source_records_rewritten':False,'actual_owner_outcome':None})
        emit(destination/'expected-replay.json',{'projection_sha256':handle.common.digest(after['projection']),
            'transaction_sha256s':[handle.common.digest(tx) for tx in after['transactions']],
            'config_sha256':signed_archive['config_sha256'],'baseline_snapshot_digest':signed_archive['baseline_snapshot_digest'],
            'expected_head':signed_archive['expected_head'],'relation_ref':relation_ref,
            'actual_targets':actual_targets,'endpoint_views':endpoint_views,'engine_pins':asdict(pins),
            'source_binding':bind(destination/'branch.snapshot')})
        result={'result':'PASS','domain':domain,'authority_effect':'none','actual_owner_outcome':None,
            'scope_ref':before['config']['scope_ref'],'source_case_binding':case_binding,
            'exact_targets':actual_targets,'endpoint_views':endpoint_views,'raw_post_subjects':raw_kind_before,
            'frozen_rejection':rejection,'fixture_signature_verified':True,'signed_transactions':1,
            'signature_basis':'Independent fresh controlled operator key for this owned fixture scope; no human/canonical owner outcome.',
            'idempotent_retry':True,'semantic_history_before':len(before['projection']['histories']['project-semantic-event-history']['payload']['events']),
            'semantic_history_after':len(after['projection']['histories']['project-semantic-event-history']['payload']['events']),
            'governance_history_before':len(before['projection']['histories']['project-governance-event-history']['payload']['events']),
            'governance_history_after':len(after['projection']['histories']['project-governance-event-history']['payload']['events']),
            'original_domain_cases_reexecuted':0,'source_effects_applied':0,'source_record_bytes_preserved':True,
            'canonical_admission':False,'live_operation':False,'runtime_activation':False,
            'private_key_exported':False,'Session_memory_exported':False,'duration_seconds':time.perf_counter()-start}
    require(not owned.exists(),'owned signed fixture/key cleanup incomplete')
    result['owned_store_and_key_removed']=True;emit(destination/'result.json',result)
    return result


if __name__=='__main__':
    if len(sys.argv)!=4 or sys.argv[1] not in ('engineering','research','product'):
        raise SystemExit('usage: episode.py engineering|research|product selected-output-path pins-json')
    pins=EnginePins(**parse(Path(sys.argv[3]).read_bytes()))
    destination=Path(sys.argv[2]);require(destination.resolve().is_relative_to(EXAMPLES),'episode output outside selected example root')
    require(not destination.exists(),'existing episode cannot be overwritten')
    result=run_one(sys.argv[1],destination,pins)
    print(json.dumps({'result':result['result'],'domain':result['domain'],'targets':len(result['exact_targets']),
        'owned_store_and_key_removed':True,'authority_effect':'none','actual_owner_outcome':None},sort_keys=True))
