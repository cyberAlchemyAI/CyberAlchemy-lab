"""Closed exact owner-domain preparation; never an operational scope grant."""
import copy,json
from .protocol import source,HERE,ROOT
PROFILE_SHA='7e88a3ed9aa5b8a09edb81eeb4e791cc0f94f82b985c634025dadb1a9331f31e'

def prepare(view,proposal,vault,control):
    source.require(type(control) is dict and set(control)=={'profile_binding','max_targets'} and control['max_targets']==42,'closed independent scope control required')
    selected=control['profile_binding'];source.require(selected=={'ref':'candidate:owner-scope-profile','sha256':PROFILE_SHA},'scope profile is not independently selected')
    raw=vault.material(selected);local=(HERE/'scope-preparation-profile.json').read_bytes();source.require(raw==local and source.sha(raw)==PROFILE_SHA,'exact scope profile bytes differ')
    profile=source.parse(raw)
    source.require(profile['schema_version']=='lab-exact-domain-scope-preparation-profile/v1-candidate' and profile['authority_effect']=='none' and profile['actual_owner_outcome'] is None and profile['runtime_admission_authorized'] is False,'preparation profile cannot grant runtime admission')
    for key in ['source_owner_core_proof_binding','source_legacy_registry_binding','source_legacy_decision_binding']:source.original(profile[key])
    config=view.data['config'];source.require(profile['storage_scope_ref']==proposal['scope_ref']==config['scope_ref'],'declared storage scope differs')
    source.require(view.selected['name']=='custody-participation' and type(view) is source.custody_delivery().reader.Inspection,'selected original-byte source required for scoped preparation')
    allowed={m['version_ref']:m for m in profile['members']};source.require(len(allowed)==42 and len(profile['groups'])==21,'closed exact owner profile required')
    targets=proposal['targets'];versions={t['version_ref'] for t in targets};source.require(len(versions)==len(targets) and 0<len(targets)<=control['max_targets'] and versions<=allowed.keys(),'unknown or duplicate domain target')
    for group in profile['groups']:
        members=set(group['required_versions']);source.require(not versions.intersection(members) or members<=versions,'partial coupled owner scope group')
    for t in targets:
        m=allowed[t['version_ref']];raw=view.handle.custody.decode_content(t['content'])
        source.require(t['category']==profile['permitted_category'] and t['operation']==profile['permitted_effect'] and t['contract'] is None and t['predecessor_ref'] is None,'unreviewed domain category/effect')
        source.require(t['record']['node_id']==m['identity_ref'] and t['record']['scope_ref']==m['domain_scope_ref'] and t['carrier_ref']==m['carrier_ref'] and t['decision_ref']==m['decision_ref'],'exact identity/carrier/domain scope differs')
        source.require(source.sha(raw)==m['original_body_sha256'] and view.handle.common.digest(t)==m['target_digest'],'complete raw domain target differs')
        core=source.parse(source.original(m['independent_core_binding']));source.require(core['target_digest']==m['target_digest'] and core['version_ref']==t['version_ref'],'independent materialized domain core differs')
    before=view.handle.common.digest(view.data['projection']);post=copy.deepcopy(view.data['projection']);by_version={};hypotheses=[]
    for group in profile['groups']:
        selected=[t for t in targets if t['version_ref'] in group['required_versions']]
        if not selected:continue
        hypothetical=copy.deepcopy(config);hypothetical['scope_ref']=group['domain_scope_ref'];scoped=copy.deepcopy(proposal);scoped['scope_ref']=group['domain_scope_ref'];scoped['targets']=selected
        part,cores=view.handle.operations.prepare(view.data['projection'],scoped,view.data['head']['transaction_digest'],hypothetical)
        for t,c in zip(selected,cores):
            post['subjects'][t['version_ref']]=copy.deepcopy(part['subjects'][t['version_ref']]);by_version[t['version_ref']]=c
        hypotheses.append({'domain_scope_ref':group['domain_scope_ref'],'configuration_status':'hypothetical-unprovisioned','configuration_sha256':source.sha(view.handle.common.encoded(hypothetical)),'version_refs':[t['version_ref'] for t in selected],'actual_runtime_grant':False})
    source.require(before==view.handle.common.digest(view.data['projection']),'scoped preparation changed actual source projection')
    view.custody_signed_sources.guard()
    evidence={'schema_version':'lab-exact-domain-scope-preparation-evidence/v1-candidate','profile_binding':selected,'storage_scope_ref':config['scope_ref'],'source_projection_unchanged':True,'hypotheses':hypotheses,'target_count':len(targets),'runtime_admission_authorized':False,'actual_owner_outcome':None,'authority_effect':'none'}
    return post,[by_version[t['version_ref']] for t in targets],evidence
