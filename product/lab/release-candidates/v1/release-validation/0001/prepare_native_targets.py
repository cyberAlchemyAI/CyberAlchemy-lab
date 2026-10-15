"""Prepare explicit selections from actual frozen declarations; no native effect."""
import ast
import base64
import copy
import json
from pathlib import Path
import build_runtime as B
import materialize_targets_v3 as T

def prepare():
    here=B.HERE;api=B.BASE/'api-integration-v14'
    source_pin='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
    profile_pin='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
    B.exact(api/'source-manifest.json',source_pin);B.exact(api/'contract-profile.json',profile_pin)
    declaration=B.declared_source(api);row=declaration['source_selection']
    archive=B.load(B.ROOT/row['archive_binding']['path'])
    config=json.loads(base64.b64decode(archive['files']['config.json']['base64_original_bytes'],validate=True))
    baseline=json.loads(base64.b64decode(archive['files']['baseline.json']['base64_original_bytes'],validate=True))
    runtime=copy.deepcopy(B.load(here/'runtime-implementation.json'))
    old_scope=runtime['scope_ref'];runtime['scope_ref']=config['scope_ref']
    B.emit(here/'runtime-native-target.json',runtime)
    member=copy.deepcopy(B.load(here/'review-member.json'))
    member['member_id']='protocol:S02:final-common-operator-native-target:api-integration-v14'
    member['targets']=[B.bind(here/'runtime-native-target.json')]
    member['postimage_binding']=member['targets'][0]
    member['native_source_scope_alignment']={'prior_draft_binding':B.bind(here/'runtime-implementation.json'),
        'prior_scope_ref':old_scope,'selected_scope_ref':config['scope_ref'],
        'changed_fields':['scope_ref'],'source_config_sha256':row['config_sha256'],
        'authority_effect':'none','actual_owner_outcome':None}
    B.emit(here/'review-member-native-target.json',member)
    common={'schema_version':'lab-explicit-final-target-selection/v3-candidate',
        'inventory_binding':B.bind(B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-review-0247/inventory.json'),
        'additional_member_binding':B.bind(here/'review-member-native-target.json'),
        'API_source_binding':B.bind(api/'source-manifest.json'),'API_profile_binding':B.bind(api/'contract-profile.json'),
        'source_name':'source8-session-participation','source_selection':row,
        'helper_bindings':[B.bind(Path(T.__file__)),B.bind(Path(T.M.__file__)),B.bind(Path(B.__file__))],
        'authority_effect':'none','actual_owner_outcome':None}
    def header(name):
        path=here/('native-header-'+name+'.json')
        B.emit(path,{'schema_version':'lab-runtime-original-json-proposal/v2-candidate',
            'proposal_id':'final-native-target-'+name+'-0254','expected_head':row['expected_head'],
            **{k:config[k] for k in ('source_snapshot_digest','scope_ref','policy_ref','challenge_route')}})
        return B.bind(path)
    def target(member_id,carrier_ref,record_binding,version,decision,category='artifact-instance',contract=None):
        c=baseline['contracts'][carrier_ref]
        return {'member_ref':member_id,'operation':'admit','category':category,'carrier_ref':carrier_ref,
            'version_ref':version,'decision_ref':decision,'record_binding':record_binding,
            'record_origin_binding':None,'record_origin_selector':None,
            'schema_binding':{'path':c['schema_path'],'sha256':c['schema_sha256']},
            'descriptor_binding':{'path':c['artifact_path'],'sha256':c['artifact_sha256']},
            'predecessor_binding':None,'contract_binding':contract}
    rt=target(member['member_id'],'cal.artifact-type.implementation/v1',B.bind(here/'runtime-native-target.json'),
        runtime['node_id']+'@native-review-0254.candidate.1','decision:final-runtime-native-review-0254')
    B.emit(here/'typed-selection-runtime-v3.json',{**common,'targets':[rt],'schema_inputs':[],
        'proposal_header_binding':header('runtime')})
    method=B.ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method'
    descriptor=B.load(method/'artifact.json');mechanics=B.load(method/'mechanics.json')
    # This is an independently bound proposed contract. The original mechanics
    # do not declare relation roles; the empty proposal asserts no new roles.
    contract={k:descriptor[k] for k in ('semantic_kind','schema_path','schema_sha256','schema_selector')}
    contract.update(instance_discriminator=mechanics['instance_discriminator'],
        identity_field=mechanics['identity_selector'].removeprefix('/'),
        allowed_relation_kinds=mechanics['relation_surface'],relation_roles=[])
    B.emit(here/'native-method-contract-proposal.json',contract)
    mt=target('protocol:C10:method-type','cal.artifact-type.artifact-type/v3',B.bind(method/'artifact.json'),
        descriptor['artifact_type_ref'],'decision:final-method-native-review-0254','artifact-type',
        B.bind(here/'native-method-contract-proposal.json'))
    B.emit(here/'typed-selection-method-v3.json',{**common,'targets':[mt],'schema_inputs':[],
        'proposal_header_binding':header('method')})
    B.emit(here/'native-selection-preparation.json',{'schema_version':'lab-final-native-selection-preparation/v1-candidate',
        'preparer_binding':B.bind(Path(__file__)),'original_mechanics_binding':B.bind(method/'mechanics.json'),
        'original_registry_binding':B.bind(B.ROOT/'implementation/lab-review/candidates/v1/packages/0001/registry.json'),
        'runtime_scope_alignment':member['native_source_scope_alignment'],
        'method_schema_absent_from_original_baseline':descriptor['schema_path'] not in baseline['documents'],
        'method_roles_proposed':[],'method_roles_not_inferred_from_relation_surface':True,
        'native_review_executed':False,'owner_authority_resolved':False,'authority_effect':'none',
        'actual_owner_outcome':None,'task_complete':False,
        'selections':[B.bind(here/'typed-selection-runtime-v3.json'),B.bind(here/'typed-selection-method-v3.json')]})
    for file in ('materialize_targets_v3.py','prepare_native_targets.py'):
        ast.parse(B.read(here/file),filename=file)
    print(json.dumps({'result':'PREPARED-NATIVE-SELECTIONS','selection_bindings':[
        B.bind(here/'typed-selection-runtime-v3.json'),B.bind(here/'typed-selection-method-v3.json')]}),flush=True)

if __name__=='__main__':prepare()
