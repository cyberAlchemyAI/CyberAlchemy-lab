"""Exact eligible challenge proposals; subject/history and resolution stay intact."""
import copy
from datetime import datetime,timezone
from pathlib import Path
from . import protocol as P, artifact_model as M, workspace as W
from .handlers import ApplicationError,cut
from .guarded_candidate import selection,calculation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
require=P.source.require;sha=P.source.sha
URI='urn:cyberalchemy-lab:protocol:'
CLAIM='Exact eligible candidate Challenge Event construction only; no factual ground adjudication, actual owner resolution, canonical admission, subject mutation or history rewrite.'

def validate_control(policy,schemas):
    root,manifest=W.validate_scope(policy);selected=policy['challenge_control']['routing_binding']
    require(selected['ref']=='workspace-object:'+manifest['workspace_ref']+':'+selected['sha256'],'challenge routing object namespace differs')
    raw=W.read_private(root/'objects'/(selected['sha256']+'.json'))
    require(sha(raw)==selected['sha256'],'independent challenge routing original changed')
    value=P.frame_parse(raw);W.privacy(value)
    schema=P.frame_parse((HERE/'challenge-routing.schema.json').read_bytes())
    P.Draft202012Validator(schema,registry=schemas.registry,format_checker=schemas.checker).validate(value)
    authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
    require(value['principal_ref']==policy['principal_ref'] and value['storage_scope_ref']==policy['scope_refs'][0]
        and value['development_authorization_binding']==P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
        'challenge routing lacks independent Principal/scope/development authorization')
    from .auth import instant,now
    require(not value['revoked'] and instant(value['not_before'])<=now()<instant(value['expires_at'])<=instant(policy['expires_at']),
        'challenge routing expired, revoked or outside reader interval')
    return value

def eligibility_bytes(*,actor,subject,contract,challenger,ground,evidence,source_cut,routes,validator_binding):
    """Deterministic encoding. It supplies no proof that validation actually ran."""
    return P.compact({'schema_version':'lab-challenger-eligibility-calculation/v1-candidate',
        'actor':actor,'subject':subject,'challenge_contract':contract,'challenger':challenger,
        'ground':ground,'evidence':evidence,'source_cut':source_cut,'contract_routes':routes,
        'validator_binding':validator_binding,'eligible_for_candidate_submission':True,
        'ground_factual_validity_verified':False,'owner_resolution_recorded':False,
        'canonical_admission_granted':False,'authority_effect':'none','claim_ceiling':CLAIM})

class ChallengeSubmission:
    def __init__(self,service,routing_binding):
        from .service import Service
        require(type(service) is Service,'actual selected Service required')
        self.service=service;self.view=service.handlers.view;self.vault=service.vault;self.schemas=service.schemas
        self.routing_binding=copy.deepcopy(routing_binding)
    def routing(self):
        policy=self.service.channel.policy_guard()
        require(policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'
            and policy['challenge_control']['routing_binding']==self.routing_binding,'independent challenger policy changed')
        return validate_control(policy,self.schemas)
    def source_record(self,header,kind=None,*,historical=False):
        readers=self.service.handlers;readers.selected_view=self.view
        row=readers.resolve_exact(header)
        allowed=('admitted-current','local-admitted-current','admitted-historical','local-admitted-historical') if historical else ('admitted-current','local-admitted-current')
        require(row['effective_state'] in allowed,'selected challenge source eligibility differs')
        semantic=self.view.data['projection']['contracts'][M.carrier(self.view,row)]['semantic_kind']
        require(kind is None or semantic==kind,'selected challenge source kind differs')
        raw=M.record_bytes(self.view,row)[0];require(sha(raw)==header['byte_sha256'],'selected challenge source original differs')
        body=P.frame_parse(raw);self.view.handle.operations.validate_record(body,header['carrier_ref'],self.view.data['projection']);W.privacy(body)
        return row,body,raw,semantic
    def receipt(self,row):
        selected=row['receipt_binding'];path=ROOT/selected['path']
        require(path.is_relative_to(ROOT) and path.resolve()==path and '..' not in Path(selected['path']).parts,
            'unsafe independent receipt source')
        source_path=HERE/'source-manifest.json';manifest=P.source.parse(source_path.read_bytes())
        require(any(b['path']==selected['path'] and b['sha256']==selected['sha256'] for b in manifest['files']),
            'receipt is not bound to actual selected host source')
        raw=P.source.original(selected);proof=P.frame_parse(raw);W.privacy(proof)
        require(proof.get('result')=='PASS' and proof.get('source_guarded_exit_completed') is True
            and type(proof.get('actual_cases')) is int and proof['actual_cases']>0,
            'selected receipt is not an actual completed source-guarded validation')
        require(row['binding']==P.binding(selected['path'],raw),'receipt evidence must preserve original source identity')
        return raw
    def _plan(self,message,outer,key):
        routing=self.routing();context=self.service.channel.guard()
        require(self.service.handlers.current() and routing['source_cut']==cut(self.view)==message['source_cut']==outer,
            'challenge requires exact current source cut')
        actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=copy.deepcopy(context['role_assignment_bindings'])
        require(message['actor']==actor and actor['agent_instance_ref'] is None and actor['session_ref'] is None
            and actor['assignment_ref'] is None,'actual selected operator challenger required')
        require(message['challenge_contract']==routing['challenge_contract'] and message['subject'] in routing['subjects'],
            'contract or exact challenged revision outside independently selected scope')
        _,contract,contract_raw,_=self.source_record(routing['challenge_contract'],'challenge-contract')
        _,challenger,challenger_raw,challenger_kind=self.source_record(routing['challenger'],'principal')
        subject,subject_body,subject_raw,subject_kind=self.source_record(message['subject'],historical=True)
        require(challenger['node_id']==context['principal_ref'] and challenger['payload']['status']=='active'
            and challenger_kind in contract['payload']['eligible_challenger_kinds'],'challenger not active or eligible under exact contract')
        require(subject_kind in contract['payload']['challengeable_subject_kinds']
            or subject['category'] in contract['payload']['challengeable_subject_kinds'],'subject kind not challengeable under exact contract')
        payload=contract['payload'];ground=message['ground']
        require(ground in payload['grounds'] and ground in routing['grounds'],'ground outside exact contract/host selection')
        routes={'policy_ref':payload['policy_ref'],'owner_route':payload['owner_route'],
            'resolution_gate_ref':payload['resolution_gate_ref'],'residue_route_ref':payload['unresolved_residue_route'],
            'response_mode':routing['response_mode'],'response_period':payload['response_period']}
        require(all(routes[k]==routing[k] for k in ('policy_ref','owner_route','resolution_gate_ref','residue_route_ref'))
            and routing['response_mode'] in payload['response_modes'],'contract owner/policy/resolution/residue/response routes differ')
        require(message['evidence_bindings'] and len({(b['ref'],b['sha256']) for b in message['evidence_bindings']})==len(message['evidence_bindings']),
            'unique complete challenge evidence required')
        selected=[];originals=[]
        for binding in message['evidence_bindings']:
            matches=[r for r in routing['accepted_evidence'] if r['binding']==binding]
            require(len(matches)==1,'evidence absent or ambiguous in independent challenger scope');row=matches[0]
            if row['kind']=='validation-receipt':
                require(row['artifact'] is None and row['receipt_binding'] is not None,'receipt evidence must use its actual source adapter')
                raw=self.receipt(row)
            else:
                require(row['artifact'] is not None and row['receipt_binding'] is None,'artifact evidence must use its actual source adapter')
                _,body,raw,_=self.source_record(row['artifact'],None if row['kind']=='source' else row['kind'],historical=row['kind']=='source')
                require(binding==P.binding(row['artifact']['version_ref'],raw),'artifact evidence original identity differs')
            require(self.vault.material(binding)==raw,'challenge evidence bytes differ from independently verified originals')
            selected.append({'kind':row['kind'],'binding':copy.deepcopy(binding)});originals.append(raw)
        require(set(payload['required_evidence_kinds'])<=set(r['kind'] for r in selected),'required evidence kinds not completely covered')
        validator=P.binding(str((HERE/'challenge_submission.py').relative_to(ROOT)),(HERE/'challenge_submission.py').read_bytes())
        eligibility=eligibility_bytes(actor=actor,subject=message['subject'],contract=message['challenge_contract'],
            challenger=routing['challenger'],ground=ground,evidence=selected,source_cut=outer,routes=routes,validator_binding=validator)
        require(self.vault.material(message['eligibility_evaluation_binding'])==eligibility,
            'caller eligibility evidence differs from independent executed evaluation')
        raw=self.vault.material(message['challenge_candidate_binding']);body=P.frame_parse(raw);W.privacy(body)
        carrier='cal.artifact-type.challenge-event/v1';contract_row=self.view.data['projection']['contracts'][carrier]
        schema_raw=P.source.original({'path':contract_row['schema_path'],'sha256':contract_row['schema_sha256']})
        P.Draft202012Validator(P.frame_parse(schema_raw),format_checker=self.schemas.checker).validate(body)
        self.view.handle.operations.validate_record(body,carrier,self.view.data['projection'])
        require(body['lifecycle_state']=='candidate' and body['scope_ref']==routing['candidate_scope_ref']==self.view.data['config']['scope_ref']
            and body['owner_ref']==contract['owner_ref'] and body['challenge_route']==routes['owner_route']
            and body['relation_refs']==[] and body['successor_refs']==[],'candidate ownership/scope/routes or undeclared graph effects differ')
        require(not any(s['identity']==body['node_id'] for s in self.view.subjects.values()),'new challenge identity already exists in preserved source history')
        expected={'challenge_contract_ref':routing['challenge_contract']['version_ref'],'subject_ref':message['subject']['identity_ref'],
            'subject_version_ref':message['subject']['version_ref'],'challenger_ref':context['principal_ref'],'ground':ground,
            'evidence_refs':[b['ref'] for b in message['evidence_bindings']],'response_state':'open','resolution_decision_ref':'none','residue_refs':[]}
        require(all(body['payload'][k]==v for k,v in expected.items()) and body['evidence_refs']==expected['evidence_refs'],
            'challenge candidate substitutes subject, history, challenger, evidence, ground or resolution')
        from .auth import instant,now
        require(instant(routing['not_before'])<=instant(body['payload']['submitted_at'])<=now()<instant(routing['expires_at']),
            'submission timestamp or current challenge window differs')
        version=body['node_id']+'@challenge.candidate.1';decision='decision:R03-challenge-submit:'+sha(raw)
        native={'category':'artifact-instance','operation':'admit','version_ref':version,'carrier_ref':carrier,
            'record':body,'predecessor_ref':None,'decision_ref':decision,'contract':None,
            'content':self.view.handle.custody.content_entry(raw)}
        core={'decision_ref':decision,'category':'artifact-instance','operation':'admit','version_ref':version,
            'target_digest':self.view.handle.common.digest(native)}
        runtime={'schema_version':'lab-runtime-proposal/v1','proposal_id':message['request_ref']+':challenge-candidate',
            'expected_head':self.view.data['head']['transaction_digest'],'source_snapshot_digest':self.view.data['config']['source_snapshot_digest'],
            'scope_ref':routing['candidate_scope_ref'],'policy_ref':self.view.data['config']['policy_ref'],
            'challenge_route':self.view.data['config']['challenge_route'],'schemas':{},'targets':[native]}
        runtime=self.view.handle.custody.with_originals(runtime,{version:raw},{},exact_schema_bytes=True)
        before=self.view.handle.common.digest(self.view.data['projection'])
        _,computed=self.view.handle.operations.prepare(self.view.data['projection'],runtime,self.view.data['head']['transaction_digest'],self.view.data['config'])
        require(computed==[core] and before==self.view.handle.common.digest(self.view.data['projection']),
            'native challenge core differs or pure preparation changed source')
        return {'raw':raw,'body':body,'carrier':carrier,'version':version,'core':core,'eligibility':eligibility,
            'schema_binding':{'ref':contract_row['schema_path'],'sha256':contract_row['schema_sha256']},
            'routes':routes,'routing':routing,'originals':[contract_raw,challenger_raw,subject_raw,*originals]}
    def preflight(self,message,outer,key):
        try:
            with selection(self.service):
                require(self.schemas.protocol_valid(URI+'challenge-request:v1-candidate',message),'original challenge request contract differs')
                self._plan(message,outer,key)
        except ApplicationError:raise
        except Exception as e:raise ApplicationError('invalid-contract','Exact challenger, revision, contract, evidence, routing or candidate could not be verified.') from e
    def prepare(self,message,request,outer,key,original):
        with calculation(self.service) as writer:
            require(P.frame_parse(original)==message and self.schemas.protocol_valid(URI+'challenge-request:v1-candidate',message),
                'original challenge bytes or public schema differ')
            plan=self._plan(message,outer,key);content=writer.object(plan['raw'])
            core=writer.object(self.view.handle.common.encoded(plan['core']))
            metadata=writer.object(P.source.encoded({'schema_version':'lab-candidate-target-metadata/v1-candidate',
                'category':'artifact-instance','decision_ref':plan['core']['decision_ref'],'contract':None}))
            eligibility=writer.object(plan['eligibility']);evidence=[eligibility,writer.object(original),writer.object(P.compact(plan['routing']))]
            evidence.extend(writer.object(raw) for raw in plan['originals'])
            body=plan['body'];domain={'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':message['request_ref']+':challenge-candidate',
                'actor':copy.deepcopy(message['actor']),'scope_ref':plan['routing']['candidate_scope_ref'],'base_cut':copy.deepcopy(outer),
                'source_profile_binding':{'ref':self.view.handle.manifest['profile_binding']['path'],'sha256':self.view.handle.manifest['profile_binding']['sha256']},
                'workspace_binding':self.vault.control_binding,'targets':[{'operation':'admit','artifact':{
                    'scope_ref':plan['routing']['candidate_scope_ref'],'identity_ref':body['node_id'],'version_ref':plan['version'],
                    'carrier_ref':plan['carrier'],'byte_sha256':sha(plan['raw']),'candidate_contract_binding':plan['schema_binding']},
                    'predecessor':None,'content':{'content_ref':content['ref'],'byte_sha256':content['sha256'],
                        'size_bytes':len(plan['raw']),'media_type':'application/json'},'candidate_binding':metadata,
                    'requested_effect':'Admit only this exact open Challenge Event after owner review; preserve its challenged revision and all original subject/history bytes.',
                    'decision_core_binding':core}], 'schema_bindings':[],'connection_proposals':[],'evidence_bindings':evidence,
                'idempotency_key':key,'challenge_route':self.view.data['config']['challenge_route'],'authority_effect':'none'}
            require(self.schemas.protocol_valid(URI+'change-proposal:v1-candidate',domain),'generated challenge proposal violates original public contract')
        return domain,evidence
