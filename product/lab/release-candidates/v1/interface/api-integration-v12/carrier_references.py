"""Typed original reference closure for independently selected workflow members."""
import copy
from pathlib import Path
from . import protocol as P, workspace as W, handlers as H
from .challenge_submission import ChallengeSubmission
from .review_preparation import ReviewPreparation, header
KIND='lab-local-reference-closed-review-policy/v1-candidate'
CARRIERS=['cal.artifact-type.evidence-set/v1','cal.artifact-type.challenge-event/v1',
          'cal.artifact-type.user-decision-preference/v1']
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
require=P.source.require

def validate_control(policy):
    control=policy['reference_control']
    require(set(control)=={'resolver_binding','routing_binding','supported_carriers'},'closed reference control required')
    require(control['resolver_binding']==P.binding(str((HERE/'carrier_references.py').relative_to(ROOT)),
                (HERE/'carrier_references.py').read_bytes()),'independent resolver code selection differs')
    require(control['routing_binding']==policy['challenge_control']['routing_binding']
            and control['supported_carriers']==CARRIERS,'typed original registry or carrier selection differs')
    return copy.deepcopy(control)

class CarrierReferences:
    def __init__(self,host,proposal):
        self.host=host;self.vault=host.vault;self.proposal=copy.deepcopy(proposal)
        self.control=validate_control(host.channel.policy_guard())
        require(host.channel.policy['schema_version']==KIND,'reference closure requires its independent policy')
    def producer(self,target):
        from .workflow_composition import validate_control as composition
        selected,_=composition(self.host.channel.policy_guard(),self.host.schemas)
        matches=[m for m in selected['members'] if m['source']=='completed-producer'
                 and m['target_version_ref']==target['version_ref']]
        require(len(matches)==1,'carrier has no unique independently selected producer member')
        member=matches[0]
        claim,record=self.vault.lookup({'operation':'challenge.submit','idempotency_key':member['idempotency_key']},
                                      self.host.channel.guard())
        require(claim is not None and record is not None and record['posture']=='completed','reference producer is absent or pending')
        call=P.frame_parse(self.vault.object_read(claim['original_call_material_binding']))
        require(call['operation']=='challenge.submit' and call['idempotency_key']==member['idempotency_key']
                and call['expected_source_cut']==self.proposal['base_cut'],'reference producer call or cut differs')
        builder=ChallengeSubmission(self.host,self.control['routing_binding'])
        # Original native eligibility, raw evidence, schema/core and connection
        # preparation still execute. This check supplies no authority of its own.
        plan=builder._plan(call['message'],call['expected_source_cut'],call['idempotency_key'])
        originals=[item for item in plan['targets'] if item['version']==target['version_ref']]
        require(len(originals)==1 and originals[0]['body']==target['record']
                and P.source.sha(originals[0]['raw'])==member['byte_sha256'],'carrier differs from exact current producer reconstruction')
        return builder,call['message'],plan,record['domain_binding']
    def registry(self,builder,routing):
        rows=routing['accepted_evidence'];refs=[r['binding']['ref'] for r in rows]
        require(len(refs)==len(set(refs)),'typed original evidence reference is ambiguous')
        verified={}
        for row in rows:
            posture=row['source_posture'];artifact=row['artifact']
            if posture=='completed-validation':
                require(row['kind']=='validation-receipt' and artifact is None,'receipt cannot be an artifact revision')
                raw=builder.receipt(row);reference_class='operational-validation-receipt'
            elif posture=='bound-original':
                raw=builder.original_evidence(row);reference_class='bound-original-document'
            elif posture=='candidate-original':
                raw=builder.candidate_evidence(row);reference_class='candidate-artifact-revision'
            else:
                require(posture=='signed-source' and artifact is not None,'original source posture is unsupported')
                _,_,raw,_=builder.source_record(artifact,None if row['kind']=='source' else row['kind'],
                                              historical=row['kind']=='source')
                reference_class='signed-artifact-revision'
            require(self.vault.material(row['binding'])==raw,'typed original evidence bytes differ')
            verified[row['binding']['ref']]={'reference_class':reference_class,'evidence_kind':row['kind'],
                'source_posture':posture,'original_binding':copy.deepcopy(row['binding']),
                'artifact':copy.deepcopy(artifact)}
        return verified
    def resolve(self,target,message,post):
        carrier=target['carrier_ref']
        if carrier not in CARRIERS:return None
        require(message==self.proposal and post is not self.host.handlers.view.data['projection'],
                'reference check requires the exact independent prospective proposal')
        details={'resolver_binding':copy.deepcopy(self.control['resolver_binding']),
            'source_cut':copy.deepcopy(message['base_cut']),'reference_closure_only':True,
            'ground_factual_validity_verified':False,'current_owner_authority_verified':False,
            'canonical_admission_granted':False,'typed_references':[]}
        if carrier==CARRIERS[2]:
            selected=self.vault.inputs.get('candidate:review-routing')
            require(selected is not None,'preference reference closure requires independent review routing')
            raw=self.vault.material({'ref':selected['ref'],'sha256':selected['sha256']})
            review=ReviewPreparation(self.host,self.vault.root/selected['path'],P.source.sha(raw),
                P.source.sha((HERE/'source-manifest.json').read_bytes()))
            profile,preference=review.resolve_routing(message)
            require(review.routing['preference_basis']=='proposed-target' and preference==target['record'],
                    'preference resolver cannot promote proposed bytes to current admission')
            # Only this declared workflow-type scope is supported. Other scopes
            # retain their generic not-evaluable check until explicitly selected.
            if preference['payload']['scope_kind']!='workflow-type':return None
            details.update(proposed_preference_is_currently_admitted=False,
                preference_scope_kind=preference['payload']['scope_kind'],
                preference_scope_ref=preference['payload']['scope_ref'],
                invalidation_conditions=copy.deepcopy(preference['payload']['invalidation_conditions']))
            details['typed_references']=[
                {'reference_class':'principal-artifact-revision','selector':'/payload/user_ref',
                 'requested_ref':preference['payload']['user_ref'],'artifact':review.routing['accountable_owner']},
                {'reference_class':'workflow-profile-artifact-revision','selector':'/payload/profile_ref',
                 'requested_ref':preference['payload']['profile_ref'],'artifact':review.routing['workflow_decision_profile']},
                {'reference_class':'declared-workflow-type-reference','selector':'/payload/scope_ref',
                 'requested_ref':preference['payload']['scope_ref'],'declared_by':review.routing['workflow_decision_profile'],
                 'declared_value':profile['payload']['workflow_type_ref']}]
            details['input_bindings']=[{'ref':selected['ref'],'sha256':selected['sha256']},
                                      target['decision_core_binding'] if 'decision_core_binding' in target else
                                      next(t['decision_core_binding'] for t in message['targets'] if t['artifact']['version_ref']==target['version_ref'])]
            return details
        builder,original,plan,producer= self.producer(target)
        registry=self.registry(builder,plan['routing']);body=target['record'];payload=body['payload']
        def resolve_list(selector,values,kind=None):
            require(len(values)==len(set(values)),'duplicate typed payload reference')
            for ref in values:
                require(ref in registry and (kind is None or registry[ref]['evidence_kind']==kind),
                        'typed payload reference is absent or has another evidence kind')
                details['typed_references'].append({'selector':selector,'requested_ref':ref,**copy.deepcopy(registry[ref])})
        if carrier==CARRIERS[0]:
            resolve_list('/payload/source_refs',payload['source_refs'],'source')
            resolve_list('/payload/item_refs',payload['item_refs'])
            resolve_list('/evidence_refs',body['evidence_refs'])
            project=plan['routing']['evidence_project'];builder.source_record(project)
            relation='relation.member-of';target_ref=project['version_ref']
            details.update(coverage_statement=payload['coverage_statement'],limitations=copy.deepcopy(payload['limitations']),
                           membership_project=copy.deepcopy(project))
        else:
            if payload['response_state']!='open' or payload['resolution_decision_ref']!='none' or payload['residue_refs']!=[]:return None
            require(payload['challenge_contract_ref']==original['challenge_contract']['version_ref']
                and payload['subject_ref']==original['subject']['identity_ref']
                and payload['subject_version_ref']==original['subject']['version_ref']
                and payload['challenger_ref']==original['actor']['principal_ref'],
                'challenge contract/subject/challenger reference differs')
            _,contract,_,_=builder.source_record(original['challenge_contract'],'challenge-contract')
            builder.source_record(plan['routing']['challenger'],'principal')
            builder.source_record(original['subject'],historical=True)
            require(payload['ground'] in contract['payload']['grounds']
                and set(contract['payload']['required_evidence_kinds'])<=set(r['evidence_kind'] for r in registry.values()),
                'challenge ground or required evidence kinds differ')
            resolve_list('/payload/evidence_refs',payload['evidence_refs'])
            resolve_list('/evidence_refs',body['evidence_refs'])
            relation='relation.challenges';target_ref=original['subject']['version_ref']
            details.update(challenge_contract=original['challenge_contract'],challenger=plan['routing']['challenger'],
                           subject=original['subject'],ground=payload['ground'],resolution_state='open-unresolved')
        connections=[c for c in message['connection_proposals'] if c['relation_kind_ref']==relation
                     and c['source']['artifact']['version_ref']==target['version_ref']
                     and c['target']['artifact']['version_ref']==target_ref]
        require(len(connections)==1,'carrier lacks its separate exact declared connection')
        c=connections[0]
        relations=[t for t in message['targets'] if t['artifact']['carrier_ref'].startswith('cal.artifact-type.typed-relation/')]
        matched=[]
        from . import artifact_model as M
        signature,binding=M.signature(self.host.handlers.view,relation)
        require(c['signature_sha256']==binding['sha256'] and c['axis_ref']==signature['payload']['axis_id'],
                'carrier connection signature or axis differs')
        for t in relations:
            r=P.frame_parse(self.vault.object_read({'ref':t['content']['content_ref'],'sha256':t['content']['byte_sha256']}))['payload']
            if r['relation_kind_ref']==relation and r['source']['version_ref']==target['version_ref'] and r['target']['version_ref']==target_ref:
                require(r['qualifiers']==c['qualifiers'],'carrier relation qualifiers differ');matched.append(header(t['artifact']))
        require(len(matched)==1,'carrier reference has no unique independently materialized Typed Relation')
        details.update(producer_binding=producer,typed_relation=matched[0],connection=copy.deepcopy(c),
            input_bindings=[producer,self.control['routing_binding'],* [r['original_binding'] for r in registry.values()]])
        return details
