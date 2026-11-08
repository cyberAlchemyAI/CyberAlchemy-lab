"""Exact private member selection for an original candidate workflow proposal."""
import copy
from pathlib import Path
from . import protocol as P,workspace as W,handlers as H
from .generated_candidate import GeneratedCandidateHandlers,SelectedOutputs
from .handlers import ApplicationError
require=P.source.require
KIND='lab-local-challenge-review-policy/v1-candidate'
REFERENCE_KIND='lab-local-reference-closed-review-policy/v1-candidate'
KINDS=(KIND,REFERENCE_KIND)
URI='urn:cyberalchemy-lab:protocol:'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]

def validate_control(policy,schemas):
    root,manifest=W.validate_scope(policy);binding=policy['composition_control']['selection_binding']
    rows=[row for row in manifest['materials'] if row['ref']==binding['ref'] and row['sha256']==binding['sha256']]
    require(len(rows)==1 and binding['ref']=='candidate:workflow-composition','exact independent composition input required')
    raw=W.read_private(root/rows[0]['path']);require(P.source.sha(raw)==binding['sha256'],'private composition original changed')
    value=P.frame_parse(raw);W.privacy(value)
    schema=P.frame_parse((HERE/'workflow-composition.schema.json').read_bytes())
    P.Draft202012Validator(schema,registry=schemas.registry,format_checker=schemas.checker).validate(value)
    authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
    require(value['principal_ref']==policy['principal_ref'] and value['scope_ref']==policy['scope_refs'][0]
        and value['authorization_basis_binding']==P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),'composition Principal/scope/authorization differs')
    from .auth import instant,now
    require(instant(value['not_before'])<=now()<instant(value['expires_at'])<=instant(policy['expires_at']) and value['revoked'] is False,'composition grant expired or revoked')
    require(any(m['source']=='completed-producer' for m in value['members']),'at least one exact completed producer is required')
    return value,binding

class BoundObjects:
    def __init__(self):self.bindings={}

class WorkflowCandidateHandlers(GeneratedCandidateHandlers):
    def needed(self,message):
        if self.host.channel.policy['schema_version'] in KINDS:
            return True
        return super().needed(message)
    def selected(self,message,outer,writer=None):
        policy=self.host.channel.policy_guard()
        if policy['schema_version'] not in KINDS:return super().selected(message,outer,writer)
        selection,binding=validate_control(policy,self.schemas)
        if message['proposal_ref']!=selection['proposal_ref']:
            # The exact original producer proposal remains separately consumable.
            return super().selected(message,outer,writer)
        require(selection['base_cut_binding']==P.binding('selected-workflow-source-cut',P.compact(outer))
            and outer==H.cut(self.host.handlers.view),'composition selects another current source cut')
        objects=BoundObjects();targets=[];connections=[];evidence=[];actor=None;producers={}
        for member in selection['members']:
            if member['source']=='completed-producer':
                key=member['idempotency_key']
                if key not in producers:
                    claim,record=self.vault.lookup({'operation':'challenge.submit','idempotency_key':key},self.host.channel.guard())
                    require(claim is not None and record is not None and record['posture']=='completed','composition producer is absent or pending')
                    proposal=P.frame_parse(self.vault.object_read(record['domain_binding']))
                    selected=GeneratedCandidateHandlers.selected(self,proposal,outer,writer)
                    producers[key]=proposal;objects.bindings.update(selected.selected)
                    connections.extend(copy.deepcopy(proposal['connection_proposals']));evidence.extend(copy.deepcopy(proposal['evidence_bindings']))
                    require(actor is None or actor==proposal['actor'],'composed producer Actors differ')
                    actor=copy.deepcopy(proposal['actor'])
                matches=[t for t in producers[key]['targets'] if t['artifact']['version_ref']==member['target_version_ref']]
                require(len(matches)==1,'exact declared producer member absent or ambiguous');target=copy.deepcopy(matches[0])
                require(target['artifact']['byte_sha256']==member['byte_sha256'] and target['decision_core_binding']['sha256']==member['core_sha256'],'declared producer member bytes or core differ')
            else:
                raw=self.vault.material(member['target_binding']);target=P.frame_parse(raw);W.privacy(target)
                require(target['candidate_binding']==self.vault.manifest['target_metadata'].get(target['artifact']['version_ref']),'input member metadata not independently provisioned')
                for b in (target['candidate_binding'],target['decision_core_binding']):self.vault.material(b)
                if target['operation']!='withdraw':self.vault.material({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']})
                evidence.append(copy.deepcopy(member['target_binding']))
            targets.append(target)
        versions=[t['artifact']['version_ref'] for t in targets];require(len(versions)==len(set(versions)),'duplicate composed target')
        for proposal in producers.values():
            require(all(t['artifact']['version_ref'] in versions for t in proposal['targets']),'producer closure is incomplete; every independent member must be selected')
        view=self.host.handlers.view
        evidence.append(copy.deepcopy(binding));evidence=list({(b['ref'],b['sha256']):b for b in evidence}.values())
        expected={'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':selection['proposal_ref'],'actor':actor,
            'scope_ref':selection['scope_ref'],'base_cut':copy.deepcopy(outer),'source_profile_binding':{
                'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']},
            'workspace_binding':self.vault.control_binding,'targets':targets,'schema_bindings':[],
            'connection_proposals':connections,'evidence_bindings':evidence,'idempotency_key':selection['idempotency_key'],
            'challenge_route':view.data['config']['challenge_route'],'authority_effect':'none'}
        require(self.schemas.protocol_valid(URI+'change-proposal:v1-candidate',expected),'selected exact composition violates original proposal schema')
        require(P.compact(message)==P.compact(expected),'proposal differs from exact independent composition')
        result=SelectedOutputs(self.vault,expected,objects,writer)
        if policy['schema_version']==REFERENCE_KIND:
            from .carrier_references import CarrierReferences
            result.carrier_references=CarrierReferences(self.host,expected)
        return result
