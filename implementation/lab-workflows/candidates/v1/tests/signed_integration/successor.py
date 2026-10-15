"""Exact W07 case joins to independently replayed signed coupling witnesses."""
from contextlib import contextmanager,ExitStack
import copy
import importlib.util
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import integration_support as parent
from integration_support import ROOT,PACKAGE,encoded,parse,require,bound,binding,byte_sha,emit
COUPLING=ROOT/'product/lab/release-candidates/v1/interface/coupling'
sys.path.insert(0,str(COUPLING))
spec=importlib.util.spec_from_file_location('_W07_exact_signed_coupling',COUPLING/'episode.py')
coupling=importlib.util.module_from_spec(spec);sys.modules[spec.name]=coupling;spec.loader.exec_module(coupling)
SELECTION=HERE/'selection.json'
SELECTION_SHA='6e5d8e24325e45c6801d64161b23539190c78befb2bf9d8f1a9d0f2819ffb1db'
EXPECTED_DOMAINS={'engineering','research','failure','learning'}


def selection():
    require(byte_sha(SELECTION.read_bytes())==SELECTION_SHA,'independent W07 signed selection differs')
    selected=parse(SELECTION.read_bytes())
    require(selected['schema_version']=='lab-W07-signed-integration-selection/v1-candidate' and selected['authority_effect']=='none'
        and selected['actual_owner_outcome'] is None,'selected join cannot confer owner authority')
    require(len(selected['cases'])==4 and len(selected['signed_coupling_witnesses'])==2
        and {r['domain'] for r in selected['signed_coupling_witnesses']}=={'engineering','research'},'complete closed original domain partition required')
    original= parse(bound(selected['parent_join_binding']))
    require(original['cases']==selected['cases'] and original['model_kind_closure']=='FLAG','original incomplete case cut differs')
    workflow=parse(bound(selected['parent_workflow_proof_binding']));proof=parse(bound(selected['parent_coupling_proof_binding']))
    require(workflow['result']=='PASS' and workflow['task_complete'] is False and workflow['model_integration_result']=='FLAG'
        and workflow['tests']==263 and workflow['actual_owner_outcome'] is None,'original W07 scope/observations differ')
    require(proof['result']=='PASS' and proof['task_complete'] is False and proof['tests']==73 and proof['actual_owner_outcome'] is None
        and proof['authority_effect']=='none' and proof['canonical_effects_applied']==0,'independent signed coupling proof differs')
    return selected


def original_cases(selected=None):
    selected=selected or selection();cases=[parse(bound(b)) for b in selected['cases']]
    require({c['domain'] for c in cases}==EXPECTED_DOMAINS and len({c['case_id'] for c in cases})==4,'four independent original cases required')
    return cases


@contextmanager
def signed_witness(row,selected):
    pins=coupling.EnginePins(**selected['engine_pins']);manifest=coupling.verify_engine(pins)
    require(selected['engine_manifest_binding']==binding(COUPLING/'engine-manifest.json'),'selected executable manifest differs')
    expected=parse(bound(row['expected_replay_binding']));result=parse(bound(row['result_binding']))
    metadata=parse(bound(row['original_source_witnesses_binding']));proposal=parse(bound(row['proposal_binding']));approval=parse(bound(row['approval_binding']))
    require(expected['engine_pins']==selected['engine_pins'] and expected['source_binding']==row['archive_binding'],'independently pinned archive/executable differs')
    require(result['result']=='PASS' and result['domain']==row['domain'] and result['source_case_binding']==metadata['case_binding']==row['case_binding']
        and result['fixture_signature_verified'] and result['signed_transactions']==1 and result['idempotent_retry'] and result['owned_store_and_key_removed']
        and result['actual_owner_outcome'] is None and result['authority_effect']=='none' and not result['canonical_admission']
        and not result['runtime_activation'] and result['original_domain_cases_reexecuted']==0 and not result['private_key_exported'],
        'signed witness does not retain independent candidate execution boundary')
    with tempfile.TemporaryDirectory(prefix='cal-W07-signed-read-') as temporary,coupling.engine(pins) as handle:
        owned=Path(temporary);data=coupling.restore_archive(ROOT/row['archive_binding']['path'],row['archive_binding']['sha256'],owned/'store',pins)
        require(handle.common.digest(data['projection'])==expected['projection_sha256'] and
            [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],'signed witness replay/postimages differ')
        require(len(data['transactions'])==2 and data['transactions'][-1]['proposal']==proposal and data['transactions'][-1]['approval']==approval,
            'exact original signed transaction/core/approval differs')
        require(data['freshness']['status']=='current','signed witness source closure is stale')
        yield {'row':row,'data':data,'expected':expected,'result':result,'metadata':metadata,'handle':handle,'manifest':manifest}
    require(not owned.exists(),'owned public witness read directory remains')


def close_gap(case,gap,witness):
    row=witness['row'];data=witness['data'];handle=witness['handle'];p=data['projection'];expected=witness['expected']
    require(case['domain']==row['domain'] and byte_sha(encoded(case))==row['case_binding']['sha256'],'signed witness belongs to another exact domain case')
    ref=gap['relation_ref'];require(ref==expected['relation_ref'],'signed witness belongs to another exact relation')
    relation_row=next(r for r in case['records'] if r['version_ref']==ref);relation=parse(bound({k:relation_row[k] for k in ['path','sha256']}))
    signed=p['subjects'].get(ref)
    require(signed and signed['category']=='typed-relation' and signed['record']==relation and signed['effective_state']=='local-admitted-current',
        'signed relation body/eligibility differs from original case')
    evidence=witness['metadata']['selected_records'];targets=witness['result']['exact_targets'];target_refs={r['version_ref'] for r in targets}
    require(len(targets)==len(evidence)==3 and len(target_refs)==3,'complete independent relation and both endpoint postimages required')
    require(target_refs=={ref,relation['payload']['source']['version_ref'],relation['payload']['target']['version_ref']},'signed target partition differs from exact relation endpoints')
    endpoint_views=[]
    for endpoint in (relation['payload']['source'],relation['payload']['target']):
        original_row=next(r for r in case['records'] if r['version_ref']==endpoint['version_ref'])
        original_binding={k:original_row[k] for k in ['path','sha256']};record=parse(bound(original_binding));actual=p['subjects'][endpoint['version_ref']]
        target=next(r for r in targets if r['version_ref']==actual['version_ref']);source=next(r for r in evidence if r['version_ref']==actual['version_ref'])
        require(source['source_binding']==original_binding and source['kind']==original_row['kind'] and source['record_rewritten'] is False
            and source['original_structural_sha256']==handle.common.digest(record),'original endpoint byte witness/carrier row differs')
        require(actual['record']==record and actual['identity']==endpoint['ref'] and actual['kind']==original_row['kind']==target['carrier_kind']
            and actual['carrier_ref']==target['carrier_ref'] and actual['source']==target['source_binding']
            and handle.common.digest(record)==target['record_structural_sha256'] and actual['effective_state']=='local-admitted-current',
            'signed exact endpoint postimage/raw carrier/eligibility differs')
        contract=p['contracts'][actual['carrier_ref']]
        require(contract['lifecycle_state'] in {'admitted-current','local-admitted-current'},'signed endpoint carrier eligibility differs')
        mapping_row=handle.mapping.mapping_for(actual['carrier_ref'],p)
        if mapping_row is not None:
            descriptor=mapping_row['descriptor_binding']
            require(contract['artifact_path']==descriptor['path'] and contract['artifact_sha256']==descriptor['sha256']
                and contract['artifact']==parse(bound(descriptor))==p['documents'][descriptor['path']],
                'mapped endpoint exact descriptor binding/body differs')
        if actual['kind']=='project-identity':
            require(record['project_id']==actual['identity']==data['config']['scope_ref'] and 'scope_ref' not in record,
                'Project Identity namespace differs from the signed Project scope')
            scope_basis={'field':'project_id','value':record['project_id'],'coordination_scope':record['coordination_scope']}
        else:
            require(record['scope_ref']==data['config']['scope_ref'],'signed endpoint declared scope differs')
            scope_basis={'field':'scope_ref','value':record['scope_ref']}
        view=handle.mapping.explain(actual,p)
        require(view['represented_endpoint_kind']==endpoint['kind'] and view['raw_subject_rewritten'] is False,'explicit endpoint mapping did not preserve typed axes')
        endpoint_views.append({**view,'original_case_binding':original_binding,'signed_record_source_binding':actual['source'],
            'record_scope_basis':scope_basis})
    original_relation_binding={k:relation_row[k] for k in ['path','sha256']};relation_source=next(r for r in evidence if r['version_ref']==ref)
    require(relation_source['source_binding']==original_relation_binding and relation_source['record_rewritten'] is False
        and relation_source['original_structural_sha256']==handle.common.digest(relation),'original relation witness differs')
    cores=data['transactions'][-1]['decision_cores'];require(len(cores)==3 and len({c['decision_ref'] for c in cores})==3
        and {c['version_ref'] for c in cores}==target_refs,'independent endpoint/relation Decision cores collapsed')
    handle.operations.validate_relation(relation,p)
    project=next(v for v in endpoint_views if v['version_ref']==gap['endpoint_ref'])
    require(project['represented_endpoint_kind']==gap['declared_endpoint_kind']=='project'
        and project['carrier_kind']==project['source_projection_kind']==gap['selected_carrier_semantic_kind']=='project-identity'
        and project['mapping_binding']==witness['manifest']['mapping_binding'],'gap is not exactly closed by declared source/schema/Definition mapping')
    return {'domain':case['domain'],'case_id':case['case_id'],'relation_ref':ref,'endpoint_ref':gap['endpoint_ref'],'result':'PASS',
        'original_case_binding':row['case_binding'],'original_relation_binding':original_relation_binding,
        'original_gap':copy.deepcopy(gap),'signed_archive_binding':row['archive_binding'],'signed_transaction_digest':data['head']['transaction_digest'],
        'signed_store_ref':data['config']['store_id'],'signed_scope_ref':data['config']['scope_ref'],'engine_manifest_binding':selection()['engine_manifest_binding'],
        'mapping_binding':witness['manifest']['mapping_binding'],'endpoint_views':endpoint_views,
        'independent_decision_refs':[c['decision_ref'] for c in cores],'original_case_admission':'candidate-unadmitted','signed_witness_admission':'local-admitted-current',
        'original_records_rewritten':False,'original_domain_effects_reexecuted':0,'unqualified_global_merge':False,'canonical_effects_applied':0,'actual_owner_outcome':None}


def validate_join(cases,selected=None):
    selected=selected or selection();baseline=parent.audit_join(cases)
    require(baseline['result']=='FLAG' and baseline['evidence_coverage']=='PASS' and len(baseline['runtime_kind_join_gaps'])==2,'original two-gap integration cut changed')
    exact={parse(bound(b))['domain']:b for b in selected['cases']};by={c['domain']:c for c in cases}
    require(set(by)==EXPECTED_DOMAINS and all(byte_sha(encoded(c))==exact[c['domain']]['sha256'] for c in cases),'selected original case bytes differ')
    closures=[]
    for row in selected['signed_coupling_witnesses']:
        case=by[row['domain']];gaps=next(c for c in baseline['cases'] if c['domain']==case['domain'])['closure']['runtime_kind_join_gaps']
        require(len(gaps)==1,'signed witness requires one exact original Project gap')
        with signed_witness(row,selected) as witness:closures.append(close_gap(case,gaps[0],witness))
    require({c['relation_ref'] for c in closures}=={g['relation_ref'] for g in baseline['runtime_kind_join_gaps']},'not every original runtime gap is closed')
    return {'schema_version':'lab-W07-signed-case-join/v1-candidate','result':'PASS','candidate_model_integration_result':'PASS',
        'original_join_result':'FLAG','original_join':baseline,'signed_gap_closures':closures,'original_unclosed_runtime_gaps':2,'remaining_runtime_gaps':0,
        'domain_case_count':4,'typed_connections_checked':sum(len(c['closure']['typed_connections']) for c in baseline['cases']),
        'candidate_postimage_collisions':baseline['candidate_postimage_collisions'],'global_merge_performed':False,'original_domain_cases_reexecuted':0,
        'canonical_effects_applied':0,'actual_owner_outcome':None,'authority_effect':'none',
        'claim_ceiling':'Complete selected candidate workflow integration with independently signed source-identical coupling witnesses. Original cases retain their candidate posture and separate outcomes; no canonical/global admission or general Product effectiveness.'}
