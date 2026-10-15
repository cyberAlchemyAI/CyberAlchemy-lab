"""Declared exact historical reference correction use; no general write alias."""
import copy
from pathlib import Path
from .common import byte_digest,digest,encoded,load,pointer,require
from .sources import resolve,validate_schema

ENGINE_ID='lab-operator-reference-correction/v1-candidate'
PROFILE_PATH='product/lab/release-candidates/v1/interface/corrections-v1/engine-next/write-profile.json'
PROFILE_SHA='00609ef4c881546c0f63bec905c3f03422ea42dd2e2154e3dc152141537822fd'
ELIGIBLE={'admitted-current','local-admitted-current','admitted-historical','local-admitted-historical'}
CURRENT={'admitted-current','local-admitted-current'}


def binding():return {'path':PROFILE_PATH,'sha256':PROFILE_SHA}


def profile():
    path=Path(__file__).resolve().parents[1]/'write-profile.json'
    require(path.is_file() and not path.is_symlink() and byte_digest(path.read_bytes())==PROFILE_SHA,'declared correction profile differs')
    value=load(path)
    require(value['schema_version']=='lab-reference-correction-write-profile/v1-candidate'
        and value['engine_id']==ENGINE_ID and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,
        'correction declaration cannot confer canonical authority')
    return value


def provision(repo,baseline,selected_binding,domains):
    from .sources import under
    require(selected_binding==binding(),'independently selected correction profile differs')
    value=profile()
    require(type(domains) is list and domains and len(set(domains))==len(domains)
        and set(domains)<=set(value['authorized_domain_scope_refs']),'explicit exact domain grant required')
    def collect(b):
        require(type(b) is dict and set(b)=={'path','sha256'},'closed correction dependency binding required')
        path=under(repo,b['path']);require(path.is_file() and not path.is_symlink(),'correction dependency unavailable')
        raw=path.read_bytes();require(byte_digest(raw)==b['sha256'],'exact correction dependency differs')
        doc=load(path)
        require(b['path'] not in baseline['materials'] or baseline['materials'][b['path']]==b['sha256'],'conflicting original correction dependency')
        baseline['materials'][b['path']]=b['sha256'];baseline['documents'][b['path']]=doc
        return doc
    collect(binding());collect(value['review_manifest_binding']);collect(value['source_proof_binding']);collect(value['parent_engine_binding'])
    for b in value['member_bindings']:
        member=collect(b)
        require(member['intended_scope_ref'] in value['authorized_domain_scope_refs'],'correction member scope is undeclared')
        for key in ['record_binding','original_source_binding','schema_binding']:collect(member[key])
        sig=member['signature_binding'];collect({'path':sig['ref'],'sha256':sig['sha256']})
        for witness in member['endpoint_witnesses']:
            collect(witness['source_binding']);collect(witness['admission_overlay']['binding'])
    baseline['snapshot_digest']=digest({k:v for k,v in baseline.items() if k!='snapshot_digest'})
    return value


def verify_config(config,projection):
    from .operations import protocol_check
    from .protocols import CONFIG_SCHEMA
    protocol_check(config,CONFIG_SCHEMA)
    require(config['schema_version']=='lab-runtime-store-config/v3-candidate'
        and config['correction_engine_id']==ENGINE_ID and config['correction_profile_binding']==binding(),
        'correction use requires independently provisioned exact engine/profile')
    value=profile()
    require(projection['documents'].get(PROFILE_PATH)==value,'correction declaration outside signed source snapshot')
    domains=config['authorized_domain_scope_refs']
    require(domains and set(domains)<=set(value['authorized_domain_scope_refs']),'domain grant outside declared correction profile')
    return value


def exact_document(projection,b):
    require(type(b) is dict and set(b)=={'path','sha256'} and b['path'] in projection['documents'],'exact correction witness is outside signed source closure')
    doc=projection['documents'][b['path']]
    require(byte_digest(encoded(doc))==b['sha256'],'exact captured correction witness bytes differ')
    return doc


def validate(projection,target,proposal,config):
    from .operations import endpoint_kind,validate_relation
    value=verify_config(config,projection)
    require(proposal['schema_version']=='lab-runtime-proposal/v2-candidate'
        and proposal['correction_profile_binding']==binding(),'explicit correction proposal/profile required')
    selected=target['reference_correction_binding']
    require(selected in value['member_bindings'],'unreviewed correction member')
    member=exact_document(projection,selected)
    require(member['authority_effect']=='none' and member['actual_owner_outcome'] is None
        and member['admission_posture']=='candidate','correction source review member cannot infer owner admission')
    require(target['category']==value['permitted_category']=='typed-relation'
        and target['operation']==value['permitted_operation']=='revise' and target['contract'] is None,
        'correction declaration belongs only to exact Typed Relation revision')
    require(target['version_ref']==member['version_ref'] and target['predecessor_ref']==member['predecessor_version_ref'],
        'correction version/predecessor differs from reviewed member')
    prior=resolve(projection['subjects'],member['predecessor_version_ref'])
    require(prior['version_ref']==member['predecessor_version_ref'] and prior['effective_state'] in CURRENT
        and prior['category']=='typed-relation' and prior['identity']==member['identity_ref'],'correction predecessor is not exact admitted current relation')
    before=exact_document(projection,member['original_source_binding'])
    require(prior['record']==before and prior['source']==member['original_source_binding'],'correction predecessor original source differs')
    after=exact_document(projection,member['record_binding'])
    require(target['record']==after,'correction postimage differs from exact reviewed body')
    domain=member['intended_scope_ref']
    require(before['scope_ref']==after['scope_ref']==domain and domain in config['authorized_domain_scope_refs'],
        'correction domain is outside independently provisioned grant')
    restored=copy.deepcopy(after);selectors=set()
    require(member['changes'],'correction must change an absent exact endpoint version')
    for change in member['changes']:
        selector=change['selector'];require(selector in value['allowed_selectors'] and selector not in selectors,'unreviewed correction selector')
        selectors.add(selector);side=selector.split('/')[2]
        require(pointer(before,selector)==change['before'] and pointer(after,selector)==change['after'],'exact correction endpoint change differs')
        require(change['before'] not in projection['subjects'],'original endpoint version is not missing in this cut')
        require(change['before']==before['payload'][side]['ref']+'@candidate.1','correction is not an absent original endpoint label')
        restored['payload'][side]['version_ref']=change['before']
    require(restored==before,'correction changes unreviewed semantics')
    contract=retained_carrier(projection,target['carrier_ref'])
    require(target['carrier_ref']==prior['carrier_ref'] and member['schema_binding']=={'path':contract['schema_path'],'sha256':contract['schema_sha256']},
        'correction changes original carrier/schema')
    validate_schema(after,contract['schema_path'],contract.get('schema_selector'),projection['documents'])
    relation=projection['relation_contracts'][after['payload']['relation_kind_ref']]
    signature=member['signature_binding']
    require(exact_document(projection,{'path':signature['ref'],'sha256':signature['sha256']})==relation,'correction signature witness differs')
    require(len(member['endpoint_witnesses'])==2 and {w['endpoint'] for w in member['endpoint_witnesses']}=={'source','target'},'complete independent endpoint witnesses required')
    observed=[]
    for witness in member['endpoint_witnesses']:
        side=witness['endpoint'];endpoint=after['payload'][side];subject=resolve(projection['subjects'],endpoint['version_ref'])
        require(subject['version_ref']==endpoint['version_ref']==witness['artifact']['version_ref']
            and subject['identity']==endpoint['ref']==witness['artifact']['identity_ref']
            and endpoint['kind']==witness['semantic_kind'] and subject['effective_state'] in ELIGIBLE,'correction endpoint is not exact eligible reviewed revision')
        require(subject['source']==witness['source_binding'] and subject['record']==exact_document(projection,witness['source_binding']),
            'correction endpoint original bytes/provenance differ')
        require(subject['carrier_ref']==witness['artifact']['carrier_ref'] and subject['source']['sha256']==witness['artifact']['byte_sha256']
            and witness['artifact']['scope_ref']==proposal['scope_ref'],'exact endpoint header/carrier differs')
        endpoint_contract=projection['contracts'][subject['carrier_ref']]
        require(endpoint_contract['lifecycle_state'] in ELIGIBLE,'endpoint carrier is not eligible for historical correction')
        validate_schema(subject['record'],endpoint_contract['schema_path'],endpoint_contract.get('schema_selector'),projection['documents'])
        require(endpoint_kind(subject,projection,allow_historical=True)==endpoint['kind'],'correction endpoint schema/kind differs')
        overlay=witness['admission_overlay'];doc=exact_document(projection,overlay['binding']);entry=pointer(doc,overlay['selector'])
        require(entry==overlay['entry'] and doc['decision_id']==overlay['decision_id'] and entry['version_ref']==endpoint['version_ref']
            and entry['admitted_instance_path']==subject['source']['path'],'correction endpoint independent admission witness differs')
        observed.append({'version_ref':subject['version_ref'],'identity_ref':subject['identity'],'semantic_kind':endpoint['kind'],
            'effective_state':subject['effective_state'],'source_binding':subject['source'],'admission_overlay_binding':overlay['binding']})
    validate_relation(after,projection,allow_historical=True)
    return {'carrier_use':'retained-reviewed-predecessor-carrier','carrier_ref':target['carrier_ref'],
        'carrier_lifecycle_state':contract['lifecycle_state'],'carrier_schema_binding':member['schema_binding'],
        'carrier_descriptor_binding':{'path':contract['artifact_path'],'sha256':contract['artifact_sha256']},
        'domain_scope_ref':domain,'reference_correction_binding':selected,'correction_profile_binding':binding(),
        'endpoint_witness_digest':digest(observed),'correction_use':'exact-missing-endpoint-version-correction'}


def retained_carrier(projection,ref):
    require(ref in projection['contracts'],'reviewed predecessor carrier missing')
    c=projection['contracts'][ref]
    require(c['semantic_kind']=='typed-relation' and c['lifecycle_state'] in ELIGIBLE,'reviewed predecessor carrier is not eligible for corrective use')
    descriptor=exact_document(projection,{'path':c['artifact_path'],'sha256':c['artifact_sha256']})
    require(descriptor==c['artifact'] and descriptor.get('semantic_kind',descriptor.get('classification',{}).get('semantic_kind'))=='typed-relation','reviewed predecessor carrier descriptor differs')
    return c
