"""Exact final member axes and actual signed-source owner/state inspection.

Keep unlike native event intents and protocol control models distinct. This
construction grants no owner authority and never changes a retained body scope.
"""
import argparse
import ast
import hashlib
import json
import os
import fcntl
from pathlib import Path
from datetime import datetime,timezone
from jsonschema import Draft202012Validator
import materialize_targets_v2 as M
B=M.B

def identity(row):return row.get('member_id') or row.get('member_ref')

def core_axes(view,row,record,binding,schemas):
    errors=[]
    candidates=[(ref,c) for ref,c in view.data['projection']['contracts'].items()
        if c.get('instance_discriminator',{}).get('value')==record.get('schema_version')
        and c['lifecycle_state'] in ('admitted-current','local-admitted-current')]
    if len(candidates)!=1:return {'body_binding':binding,'operation':None,'carrier_ref':None,
        'stable_core':None,'blockers':['Exactly one current declared carrier for the original schema_version is absent.'],
        'observed_carrier_choices':[r for r,_ in candidates]}
    ref,contract=candidates[0]
    descriptor=json.loads(M.original({'path':contract['artifact_path'],'sha256':contract['artifact_sha256']}))
    field=descriptor.get('instance_contract',{}).get('identity_field')
    if not field:errors.append('Original carrier lacks an explicitly bound identity selector.')
    rid=view.handle.common.identity(record,field) if field else None
    current=[s for s in view.subjects.values() if s['identity']==rid and s['effective_state'] in ('admitted-current','local-admitted-current')]
    if len(current)>1:errors.append('Original current identity is ambiguous.')
    same=bool(len(current)==1 and current[0]['record']==record)
    operation='retain-current-candidate-source-evidence' if same else 'revise' if current else 'admit'
    member_ref=identity(row);start=member_ref.find(rid+'@') if rid else -1
    version=(current[0]['version_ref'] if same else member_ref[start:] if start>=0
        else rid+'@'+record.get('version','S02-final-candidate.0276')) if rid else None
    try:
        schema=json.loads(M.original({'path':contract['schema_path'],'sha256':contract['schema_sha256']}))
        Draft202012Validator(schema,registry=schemas.registry,format_checker=schemas.checker).validate(record)
    except Exception as exc:errors.append('Original body schema validation: '+str(exc))
    if record.get('scope_ref') is not None and record['scope_ref']!=view.data['config']['scope_ref']:
        errors.append('Original domain scope is outside current Python O.prepare grant; unchanged body requires its proper original producer/source scope or an independently selected original reviewed-correction route.')
    if contract.get('schema_selector'):errors.append('Exact carrier fragment resolver must be selected for final consumer.')
    return {'body_binding':binding,'identity_ref':rid,'original_body_scope_ref':record.get('scope_ref'),
        'operation':operation,'category':{'typed-relation':'typed-relation','definition':'definition','relation-kind':'relation-kind','artifact-type':'artifact-type'}.get(contract['semantic_kind'],'artifact-instance'),
        'carrier_ref':ref,'version_ref':version,'decision_ref':'decision:S02-final:'+hashlib.sha256(identity(row).encode()).hexdigest(),
        'schema_binding':{'path':contract['schema_path'],'sha256':contract['schema_sha256']},
        'descriptor_binding':{'path':contract['artifact_path'],'sha256':contract['artifact_sha256']},
        'schema_selector':contract.get('schema_selector'),'identity_selector':field,
        'predecessor':{'version_ref':current[0]['version_ref'],'source_binding':current[0]['source'],
            'body_value_sha256':view.handle.common.digest(current[0]['record'])} if len(current)==1 else None,
        'body_byte_sha256':binding['sha256'],'stable_core':None,
        'stable_core_axes':['category','operation','version_ref','decision_ref','exact_original_target_digest'],
        'blockers':errors,'original_body_scope_changed':False,'owner_authority_resolved':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--api-directory',required=True)
    parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--inventory',required=True);parser.add_argument('--inventory-sha256',required=True)
    args=parser.parse_args();here=B.HERE;api=Path(args.api_directory).resolve()
    inv=B.exact(Path(args.inventory),args.inventory_sha256)
    B.need(inv['authority_effect']=='none' and inv['actual_owner_outcome'] is None,'inventory cannot grant authority')
    members=inv['members'];B.need(len(members)==363 and len({identity(r) for r in members})==363,'complete original363 unique members required')
    fd=os.open(B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock',os.O_RDWR|os.O_NOFOLLOW)
    started=datetime.now(timezone.utc).isoformat();rows=[];owner=[];protocol=[];materialized=[]
    try:
        fcntl.flock(fd,fcntl.LOCK_SH)
        guard,bridge,schemas=M.family(api,args.source_sha256,args.profile_sha256)
        with bridge.replay_source('source8-session-participation') as view:
            before=view.handle.common.digest(view.data['projection'])
            role_objects=[s for s in view.subjects.values() if s['kind'] in ('role','role-assignment','principal','principal-reference','person-reference','person','team')]
            for i,row in enumerate(members):
                member=identity(row);bindings=row['targets']
                for binding in bindings:M.original(binding)
                chosen=row.get('postimage_binding');body=json.loads(M.original(chosen)) if chosen else None
                if body is None:
                    bodies=[]
                    for binding in bindings:
                        raw=M.original(binding)
                        if raw.lstrip().startswith(b'{'):
                            try:value=json.loads(raw)
                            except json.JSONDecodeError:continue
                            if value.get('schema_version') and value.get('kind'):bodies.append((value,binding))
                    if bodies:body,chosen=bodies[0]
                base={'member_ref':member,'member_class':row['member_class'],'original_target_bindings':bindings,
                    'original_preparation_binding':row['preparation_input_binding'],'proposed_owner_roles':row['proposed_owner_roles']}
                if body and body.get('schema_version')=='lab-O06-representation-adoption-intent/v1-candidate':
                    axes={'consumer_route':'original-native-ontology-governance-event','operation':'append-owner-governance-event-after-R08-only',
                        'category':'native-governance-effect','carrier_ref':body['subject_carrier_version_ref'],
                        'body_binding':chosen,'semantic_tuple':body['semantic_tuple'],'predecessor_governance_tuple':body['predecessor_governance_tuple'],
                        'metadata_record_binding':body['metadata_record_binding'],'archive_binding':body['archive_binding'],
                        'stable_core':None,'blockers':['Actual owner core and final governance event bytes are explicitly deferred to S02/R08 by the original intent; it is not an Artifact instance and cannot be O.admit-wrapped.'],
                        'protocol_not_admitted_as_Artifact':True}
                elif body and body.get('kind'):
                    axes=core_axes(view,row,body,chosen,schemas)
                elif member=='protocol:C10:method-type':
                    axes={'consumer_route':'native-artifact-type-registered-item','operation':'admit-new-technical-candidate-revision',
                        'category':'artifact-type','carrier_ref':'cal.artifact-type.artifact-type/v3',
                        'original_unadmitted_candidate_binding':B.bind(B.ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method/artifact.json'),
                        'proposed_member_binding':B.bind(here/'method-native-revision-review-member.json'),
                        'technical_revision_proposal_binding':B.bind(here/'method-native-namespace-translation-proposal.json'),
                        'historical_native_core_binding':B.bind(here/'native-method-namespace-revision-0001/materialization.json'),
                        'final_family_native_core':None,'blockers':['Final16 selection must independently bind this new technical candidate revision and choose the originalv1 disposition; no14 core transfer.']}
                else:
                    # These are models of actual control rules, not file admissions.
                    useful=[]
                    for binding in bindings:
                        raw=M.original(binding)
                        if raw.lstrip().startswith(b'{'):
                            try:value=json.loads(raw)
                            except json.JSONDecodeError:continue
                            useful.append((binding,value))
                    if useful:
                        title=member.removeprefix('protocol:').removeprefix('review:')
                        token=hashlib.sha256(member.encode()).hexdigest();node='governed-model:S02:control:'+token
                        record={'schema_version':'cyberalchemy-lab-governed-model/v1','node_id':node,'kind':'governed-model',
                            'name':'Candidate control model of '+title,'lifecycle_state':'candidate','authority_effect':'none',
                            'owner_ref':row['proposed_owner_roles'][0],'scope_ref':view.data['config']['scope_ref'],
                            'evidence_refs':[b['path'] for b in bindings]+[row['preparation_input_binding']['path']],
                            'challenge_route':view.data['config']['challenge_route'],'successor_refs':[],'relation_refs':[],
                            'payload':{'model_kind':'exact-original-control-rules:'+title,
                                'contract_ref':useful[0][0]['path'],'version_ref':node+'@candidate.0276',
                                'rule_refs':[b['path']+'#' for b,_ in useful],
                                'extension_policy_ref':view.data['config']['policy_ref']},
                            'claim_ceiling':'Candidate governed representation of the selected existing control rules only. Original files remain evidence/control inputs; this is not their generic admission, a semantic alias, permission grant, code activation or proven behavior. Proposed model fit and actual owner review remain separate.'}
                        path=here/'final-member-models-0276'/('model-'+token+'.json');B.emit(path,record)
                        binding=B.bind(path);extra={**row,'targets':[binding],'postimage_binding':binding}
                        axes=core_axes(view,extra,record,binding,schemas)
                        axes.update(consumer_route='governed-model-of-original-control-rules',original_control_bindings=bindings,
                            semantic_fit='Versioned explicit rules/structures/behavior with scope, owner, sources, validation and challenge route, under the original declared GovernedModel/v1 Definition; does not stand in for executable code or implicit semantic effect.',
                            model_fit_is_owner_review_candidate=True,original_protocol_is_not_admitted=True)
                        axes['blockers'].append('GovernedModel/v1 requires at least one actual permitted relationship. No conformance, implementation instance or predecessor relationship is inferred merely to satisfy minItems; exact model-specific counterpart/meaning remains to be selected.')
                        materialized.append(binding)
                    else:
                        axes={'operation':None,'carrier_ref':None,'stable_core':None,'blockers':['No exact structured rule/model or original governed body supplies the required semantic representation; raw code is not an Artifact.']}
                    protocol.append({'member_ref':member,**axes})
                rows.append({**base,'axes':axes})
                matched=[s for s in role_objects if s['identity'] in row['proposed_owner_roles'] or s['version_ref'] in row['proposed_owner_roles']]
                assignments=[s for s in role_objects if s['kind']=='role-assignment'
                    and (s['record'].get('role_ref') or s['record'].get('payload',{}).get('role_ref')) in row['proposed_owner_roles']]
                owner.append({'member_ref':member,'required_roles':row['proposed_owner_roles'],
                    'declared_role_objects':[{'version_ref':s['version_ref'],'source':s['source'],'effective_state':s['effective_state'],'record':s['record']} for s in matched],
                    'matching_retained_assignment_objects':[{'version_ref':s['version_ref'],'source':s['source'],'effective_state':s['effective_state'],'record':s['record']} for s in assignments],
                    'actual_answering_principal_ref':None,'current_owner_authority_verified':False,
                    'reason':'Source presence/retained assignment metadata is separate from independently verified current owner identity, scope, period, actual response and authority; no literal role string grants authority.'})
            state={'source_selection':bridge.source_selection('source8-session-participation'),
                'original_head':view.data['head'],'original_config':view.data['config'],
                'projection_value_digest':before,'original_state':view.data['projection']['state'],
                'original_histories':view.data['projection']['histories'],
                'original_contracts':view.data['projection']['contracts'],
                'original_role_Principal_objects':role_objects,'actual_owner_outcome':None,'authority_effect':'none',
                'claimed_canonical_global_State':False,'source_scope':'Exact independently selected signed candidate branch; no canonical readiness or human owner inference.'}
            view.handle.guard();B.need(view.handle.common.digest(view.data['projection'])==before,'source projection changed')
        schemas.guard();guard.verify(args.source_sha256);B.exact(api/'contract-profile.json',args.profile_sha256)
        B.exact(Path(args.inventory),args.inventory_sha256)
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    common={'API_source_binding':B.bind(api/'source-manifest.json'),'API_profile_binding':B.bind(api/'contract-profile.json'),
        'inventory_binding':B.bind(Path(args.inventory)),'caller_binding':B.bind(Path(__file__)),
        'authority_effect':'none','actual_owner_outcome':None,'release_ready':False,'task_complete':False,'goal_complete':False}
    B.emit(here/'base-state-registry-history-0276.json',{'schema_version':'lab-exact-signed-candidate-base-state-inspection/v1-candidate',**common,**state})
    B.emit(here/'S02-owner-effect-matrix-0276.json',{'schema_version':'lab-final-member-owner-effect-matrix/v1-candidate',**common,'members':owner,'source_Principal_objects':[s for s in role_objects if s['kind'] in ('principal','principal-reference','person-reference','person','team')],'current_owner_authority_inferred_from_source_presence':False})
    B.emit(here/'final-materializer-selection-0276.json',{'schema_version':'lab-final-all-member-explicit-axes-selection/v1-candidate',**common,
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'original_member_count':len(rows),
        'members':rows,'new_control_model_bindings':materialized,'native_proposal_ready':False,
        'all_original_members_accounted':True,'all_native_effects_materialized':False,
        'new_Runtime16_binding':None,'new_Runtime16_gap':'Current R06/environment closure for exact16 is required;14 privacy conformance is historical and cannot be silently reused.',
        'new_Method_native_revision_binding':B.bind(here/'method-native-revision-review-member.json'),
        'first_exact_protocol_gap':next((r for r in protocol if r['blockers']),None),
        'representation_adoption_requires_original_native_event_materializer':True,
        'full_current_source_entry_exit_guards':True,'whole_package_qualified':False})
    print(json.dumps({'result':'EXACT-363-AXES-CANDIDATE','members':len(rows),'control_models':len(materialized),
        'selection_binding':B.bind(here/'final-materializer-selection-0276.json'),
        'first_protocol_gap':next((r['member_ref'] for r in protocol if r['blockers']),None)}),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
