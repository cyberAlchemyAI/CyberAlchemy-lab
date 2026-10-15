"""Prepare exact challenge consequences under independent signed authority."""
import copy
import importlib
from pathlib import Path
import sys
from . import gate, obligations

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
KIND='lab-local-integrated-challenge-resolution-policy/v2-candidate'
URI='urn:cyberalchemy-lab:protocol:'
require=gate.require
CURRENT=('admitted-current','local-admitted-current')


class RuleFailure(Exception):
    def __init__(self,evidence):
        self.code='conflict'
        self.message='Exact challenge consequence declaration or prospective validation failed; inspect retained evidence.'
        self.evidence=copy.deepcopy(evidence)
        super().__init__(self.message)


class ChallengeResolution:
    def __init__(self,host,routing_binding,host_source_binding):
        module=sys.modules.get(type(host).__module__)
        require(module is not None and getattr(module,'Service',None) is type(host),'actual selected Service required')
        path=Path(module.__file__).resolve()
        require(path.name=='service.py' and path.parent.parent==HERE.parent,'foreign host source')
        package=type(host).__module__.rsplit('.',1)[0]
        self.P=importlib.import_module(package+'.protocol')
        self.M=importlib.import_module(package+'.artifact_model')
        self.H=importlib.import_module(package+'.handlers')
        self.G=importlib.import_module(package+'.guard')
        self.A=importlib.import_module(package+'.auth')
        require(type(host.channel) is self.A.ReaderChannel,'actual parent operator required')
        manifest_path=path.parent/'source-manifest.json'
        require(host_source_binding=={'path':str(manifest_path.relative_to(ROOT)),
                                     'sha256':self.P.source.sha(manifest_path.read_bytes())},'independent host selection differs')
        manifest=self.G.verify(host_source_binding['sha256'])
        for name in ('preparation.py','gate.py','obligations.py'):
            selected=HERE/name
            require({'path':str(selected.relative_to(ROOT)),'sha256':self.P.source.sha(selected.read_bytes())} in manifest['files'],
                    'resolution method outside selected host closure')
        self.host=host;self.vault=host.vault;self.schemas=host.schemas
        self.host_source_binding=copy.deepcopy(host_source_binding)
        self.routing_binding=copy.deepcopy(routing_binding)
        self.method_binding=self.P.binding(str(Path(__file__).resolve().relative_to(ROOT)),Path(__file__).read_bytes())
        policy=host.channel.policy_guard()
        require(policy['schema_version']==KIND and policy['resolution_control']['routing_binding']==routing_binding
                and policy['resolution_control']['method_binding']==self.method_binding,'independent resolution policy absent')
        self.raw=self.vault.object_read(routing_binding);self.routing=self.P.frame_parse(self.raw)
        require(set(self.routing)=={'schema_version','source_cut','scope_ref','challenge_contract','subject','owner_principal',
                                   'owner_public_key_hex','owner_gate_binding','semantic_proposal_binding','governance_proposal_binding',
                                   'result_proposal_binding','consequence_routes','response_obligations',
                                   'authorization_basis_binding','authority_effect','actual_owner_outcome'},
                'closed resolution routing required')
        require(self.routing['schema_version']=='lab-challenge-resolution-routing/v1-candidate'
                and self.routing['authority_effect']=='none' and self.routing['actual_owner_outcome'] is None,
                'candidate routing supplies no canonical owner outcome')
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        require(self.routing['authorization_basis_binding']==self.P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
                'development authorization differs')

    def record(self,header,kind=None):
        row=self.host.handlers.resolve_exact(header)
        semantic=self.host.handlers.view.data['projection']['contracts'][self.M.carrier(self.host.handlers.view,row)]['semantic_kind']
        require(row['effective_state'] in CURRENT and (kind is None or semantic==kind),'exact current source kind/posture required')
        raw=self.M.record_bytes(self.host.handlers.view,row)[0]
        require(self.P.source.sha(raw)==header['byte_sha256'],'source original differs')
        body=self.P.frame_parse(raw)
        self.host.handlers.view.handle.operations.validate_record(body,header['carrier_ref'],self.host.handlers.view.data['projection'])
        return body

    def proposal(self,binding,actor,outer,key):
        raw=self.vault.object_read(binding);body=self.P.frame_parse(raw)
        require(self.schemas.protocol_valid(URI+'change-proposal:v1-candidate',body),'original ChangeProposal required')
        require(body['actor']==actor and body['base_cut']==outer and body['scope_ref']==self.routing['scope_ref']
                and body['idempotency_key']==key,'proposal Actor/cut/scope/key differs')
        self.host.candidates.preflight(body,outer)
        return raw,body

    def preflight(self,message,outer,key):
        self.G.verify(self.host_source_binding['sha256']);self.schemas.guard()
        context=self.host.channel.guard();policy=self.host.channel.policy_guard()
        require(policy['schema_version']==KIND and 'challenge.resolve' in policy['allowed_operations'],'resolution preparation permission absent')
        require(policy['resolution_control']['routing_binding']==self.routing_binding
                and policy['resolution_control']['method_binding']==self.method_binding
                and self.vault.object_read(self.routing_binding)==self.raw,'resolution policy/routing changed')
        require(message['source_cut']==outer==self.routing['source_cut']==self.H.cut(self.host.handlers.view),'resolution cut differs')
        challenge=self.record(message['challenge'],'challenge-event')
        decision=self.record(message['resolution_decision'],'decision')
        contract=self.record(self.routing['challenge_contract'],'challenge-contract')
        subject=self.record(self.routing['subject'])
        principal=self.record(self.routing['owner_principal'],'principal')
        owner=principal['node_id'];cp=challenge['payload'];dp=decision['payload'];rules=contract['payload']
        require(context['principal_ref']==owner and dp['decision_maker_ref'] in (owner,self.routing['owner_principal']['version_ref']),
                'actual authenticated accountable owner differs')
        require(challenge['scope_ref']==decision['scope_ref']==contract['scope_ref']==subject['scope_ref']==principal['scope_ref']==self.routing['scope_ref'],
                'resolution source scopes differ')
        require(cp['challenge_contract_ref']==self.routing['challenge_contract']['version_ref']
                and cp['subject_version_ref']==self.routing['subject']['version_ref']
                and cp['subject_ref']==self.routing['subject']['identity_ref'], 'challenge exact contract/subject differs')
        require(cp['response_state']=='responded' and cp['resolution_decision_ref'] in ('none','unresolved'),
                'current responded unresolved challenge required')
        require(subject['kind'] in rules['challengeable_subject_kinds'] and cp['ground'] in rules['grounds'],
                'undeclared challenge subject/ground')
        require(message['challenge']['version_ref'] in dp['subject_refs'] and bool(dp['declared_effect_refs']),
                'Decision does not declare consequences for this exact challenge')
        require(message['semantic_change_proposal_binding']==self.routing['semantic_proposal_binding']
                and message['governance_change_proposal_binding']==self.routing['governance_proposal_binding'],
                'semantic/governance proposals not independently selected')
        require(message['unresolved_gaps']==[],'unresolved resolution obligations cannot prepare effects')
        response_control=self.routing['response_obligations']
        challenger=self.record(response_control['challenger'],'principal')
        require(challenger['scope_ref']==self.routing['scope_ref'],'challenger outside selected scope')
        for row in response_control['accepted_evidence']:
            evidence=self.record(row['artifact'],row['kind'])
            require(evidence['scope_ref']==self.routing['scope_ref'],'response evidence outside selected scope')
            raw=self.M.record_bytes(self.host.handlers.view,self.host.handlers.resolve_exact(row['artifact']))[0]
            require(row['binding']==self.P.binding(row['artifact']['version_ref'],raw)
                    and self.vault.material(row['binding'])==raw,'response evidence original differs')
        response=self.P.frame_parse(self.vault.material(response_control['response_binding']))
        obligations.verify(response_control,rules=rules,challenge=cp,challenge_header=message['challenge'],
            contract_header=self.routing['challenge_contract'],subject_header=self.routing['subject'],
            owner_header=self.routing['owner_principal'],challenger=challenger,response=response,
            evidence_bindings=message['evidence_bindings'],now=self.A.now())
        require(response_control['response_binding']['ref'] in dp['evidence_basis_refs']
                and set(dp['evidence_basis_refs'])<=set(item['ref'] for item in message['evidence_bindings'])|{response_control['response_binding']['ref']},
                'exact Decision evidence basis missing')
        signed=self.P.frame_parse(self.vault.object_read(self.routing['owner_gate_binding']))
        gate.verify(signed,selected_public_key_hex=self.routing['owner_public_key_hex'],recognized_principal=owner,
            selected_gate_ref=rules['resolution_gate_ref'],owner_route=rules['owner_route'],scope_ref=self.routing['scope_ref'],
            source_cut=outer,challenge=message['challenge'],resolution_decision=message['resolution_decision'],
            challenge_contract=self.routing['challenge_contract'],subject=self.routing['subject'],selected_outcome=dp['selected_outcome'],
            semantic_proposal_binding=message['semantic_change_proposal_binding'],governance_proposal_binding=message['governance_change_proposal_binding'],
            evidence_bindings=message['evidence_bindings'],consequence_routes=self.routing['consequence_routes'],
            response_obligations=response_control,
            principal_record=principal,policy_expires_at=policy['expires_at'],now=self.A.now())
        actor={name:context[name] for name in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=context['role_assignment_bindings']
        branches={};originals={}
        for axis,selected in [('semantic',message['semantic_change_proposal_binding']),('governance',message['governance_change_proposal_binding'])]:
            if selected is not None:originals[axis],branches[axis]=self.proposal(selected,actor,outer,key)
        require(branches,'one exact semantic or governance consequence proposal required')
        if len(branches)==2:
            require(self.routing['semantic_proposal_binding']!=self.routing['governance_proposal_binding'],
                    'semantic and governance consequences collapsed')
        raw,result=self.proposal(self.routing['result_proposal_binding'],actor,outer,key)
        branch_targets=[target for body in branches.values() for target in body['targets']]
        obligations.composition(result,branches,subject_header=self.routing['subject'])
        # Decision Effect references and consequence target references are
        # different types. The signed owner gate must bind their exact mapping.
        routes=self.routing['consequence_routes']
        require(type(routes) is list and len(routes)==len(branch_targets),'complete exact consequence routes required')
        declared=[];selected_targets=[]
        for route in routes:
            require(set(route)=={'axis','effect','target_version_ref','decision_scope'},'closed consequence route required')
            require(route['axis'] in branches,'undeclared semantic/governance consequence axis')
            matches=[target for target in branches[route['axis']]['targets']
                     if target['artifact']['version_ref']==route['target_version_ref']]
            require(len(matches)==1,'exact consequence target missing or ambiguous')
            target=matches[0]
            effect=self.record(route['effect'],'effect')
            scope_body=self.record(route['decision_scope'],'decision-scope');decision_scope=scope_body['payload']
            require(effect['scope_ref']==scope_body['scope_ref']==self.routing['scope_ref'],'Effect/Decision Scope differs')
            ep=effect['payload']
            require(route['effect']['version_ref'] in dp['declared_effect_refs'],'Effect not declared by actual Decision')
            require(ep['subject_ref'] in (target['artifact']['identity_ref'],target['artifact']['version_ref'])
                    and ep['effect_kind']==target['requested_effect'] and ep['effect_kind'] in decision_scope['permitted_effects']
                    and ep['effect_kind'] not in decision_scope['excluded_effects'], 'Effect target or Decision Scope differs')
            require(target['artifact']['identity_ref'] in decision_scope['subject_refs']
                    or target['artifact']['version_ref'] in decision_scope['subject_refs'], 'consequence outside exact Decision Scope')
            carrier=target['artifact']['carrier_ref']
            require(self.host.handlers.view.data['projection']['contracts'][carrier]['semantic_kind'] in decision_scope['subject_kind_refs'],
                    'target semantic kind outside exact Decision Scope')
            declared.append(route['effect']['version_ref']);selected_targets.append(route['target_version_ref'])
        require(set(declared)==set(dp['declared_effect_refs']) and len(set(selected_targets))==len(branch_targets),
                'Decision Effect or consequence closure incomplete')
        return raw,result,branches,originals

    def prepare(self,message,request,outer,key):
        guarded=importlib.import_module(type(self.host).__module__.rsplit('.',1)[0]+'.guarded_candidate')
        failed=None
        with guarded.calculation(self.host) as writer:
            raw,result,branches,originals=self.preflight(message,outer,key)
            evidence=[];passed=True
            for axis,body in branches.items():
                report,details=self.host.candidates.validate(body,request,outer,originals[axis],evidence_writer=writer)
                passed=passed and report['result']=='pass';evidence.extend(details['evidence'])
            report,details=self.host.candidates.validate(result,request,outer,raw,evidence_writer=writer)
            passed=passed and report['result']=='pass';evidence.extend(details['evidence'])
            evidence.append(writer.object(self.P.source.encoded({'schema_version':'lab-exact-challenge-consequence-check/v1-candidate',
                'result':'pass' if passed else 'fail','challenge':message['challenge'],'resolution_decision':message['resolution_decision'],
                'source_cut':outer,'semantic_proposal_binding':message['semantic_change_proposal_binding'],
                'governance_proposal_binding':message['governance_change_proposal_binding'],
                'owner_gate_binding':self.routing['owner_gate_binding'],'canonical_admissions':0,'authority_effect':'none'})))
            self.preflight(message,outer,key)
            require(self.host.handlers.current(),'resolution source changed during preparation')
            if passed:answer=copy.deepcopy(result),evidence
            else:failed=RuleFailure(evidence)
        if failed is not None:raise failed
        return answer
