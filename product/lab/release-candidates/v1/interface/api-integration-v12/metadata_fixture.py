"""New owned metadata-only grants; original Assignment and signers stay historical."""
import copy,json,uuid
from .protocol import *
from .fixtures import provision as legacy_provision,proof,call
from .workspace import atomic
from .example_fixture import candidate_call

def materials(view):
    profile=source.parse((HERE/'scope-preparation-profile.json').read_bytes());rows={};metadata={};targets=[]
    manifest=source.parse((HERE.parent/'owner-core-preparation-v1/artifacts/manifest.json').read_bytes())
    for group in manifest['scope_proposals']:
        p=source.parse(source.original(group['runtime_proposal_binding']))
        for t in p['targets']:
            version=t['version_ref'];name=source.sha(version.encode());raw=view.handle.custody.decode_content(t['content']);core=next(m for m in manifest['members'] if m['version_ref']==version)['independent_core_binding'];core_raw=source.original(core)
            refs={k:'candidate:owner-'+k+':'+name for k in ['body','metadata','core']};meta={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance','decision_ref':t['decision_ref'],'contract':None}
            rows.update({refs['body']:raw,refs['metadata']:source.encoded(meta),refs['core']:core_raw});binding_meta=binding(refs['metadata'],rows[refs['metadata']]);metadata[version]=binding_meta
            contract=view.data['projection']['contracts'][t['carrier_ref']];h={'scope_ref':view.data['config']['scope_ref'],'identity_ref':t['record']['node_id'],'version_ref':version,'carrier_ref':t['carrier_ref'],'byte_sha256':source.sha(raw),'candidate_contract_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']}}
            targets.append({'operation':'admit','artifact':h,'predecessor':None,'content':{'content_ref':refs['body'],'byte_sha256':source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'},'candidate_binding':binding_meta,'requested_effect':'Prepare exact owner representation for final review; no current owner permission or runtime scope activation','decision_core_binding':binding(refs['core'],core_raw)})
    rows['candidate:owner-scope-profile']=(HERE/'scope-preparation-profile.json').read_bytes();return rows,metadata,targets

def provision(root,rows,metadata,*,scoped=True):
    principal='principal:R03-metadata-reader:'+uuid.uuid4().hex
    key,path,pin=legacy_provision(root,'reference-corrected',rows,metadata,principal=principal)
    policy=source.parse(path.read_bytes());authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
    policy.update(schema_version='lab-local-metadata-candidate-policy/v1-candidate',source_name='custody-participation',allowed_operations=list(METADATA_SUPPORTED),purpose='durable-metadata-and-exact-candidate-preparation',development_authorization_binding=binding(str(authority.relative_to(ROOT)),authority.read_bytes()),scope_control={'profile_binding':binding('candidate:owner-scope-profile',rows['candidate:owner-scope-profile']),'max_targets':42} if scoped else None,max_request_bytes=1048576)
    raw=compact(policy);path.write_bytes(raw);return key,path,source.sha(raw)

def candidate(service,targets,operation='change.prepare',key='fixture:owner-prepare'):
    c=candidate_call(service,targets[0],operation,key);c['message']['targets']=copy.deepcopy(targets);c['message']['idempotency_key']=key;c['message']['proposal_ref']='proposal:R03-exact-owner-representation';return c
