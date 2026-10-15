"""Authenticated original challenge response, private phase-specific candidate.

The old W05 response is fixture-only. This explicit successor has its own exact
private phase permission and signed actual response input. It never calls the
open-only challenge.submit or creates a human disposition/Decision/admission.
"""
import base64,copy
from .protocol import HERE,compact
from .handlers import cut
from .auth import now,instant
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_material import selected_resolver,private_material
from .workflow_producer_guard import guard_original_producer
from .workflow_stage_producers import StageWriter

class ChallengeResponseProducer:
    def __init__(self,host,service,obligations,*,control_binding,descriptor,read_public,source_rows,carriers,guard):
        self.host=host;self.service=service;self.obligations=obligations;self.control_binding=copy.deepcopy(control_binding);self.descriptor=copy.deepcopy(descriptor);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False;self.factory=None
        self.control=parse(private_material(host,control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','producer_policy_binding','producer_source_binding','phase_grant_binding','authority_contract_binding','obligations_method_binding','record_version','authority_effect'))
        need(p['schema_version']=='lab-private-authenticated-challenge-response-stage/v1-candidate' and p['authority_effect']=='none','explicit versioned response phase control required')
        need(len(descriptor['output_custody']['output_roots'])==1,'one selected response capture root required')
    def current(self,header,kind):
        from . import artifact_model as M
        row=self.service.handlers.resolve_exact(header);need(row['effective_state'] in ('admitted-current','local-admitted-current'),'response input is not exact/current')
        raw=M.record_bytes(self.service.handlers.view,row)[0];body=parse(raw)
        need(body['kind']==kind and sha(raw)==header['byte_sha256'],'actual original response input kind/bytes differ')
        self.service.handlers.view.handle.operations.validate_record(body,header['carrier_ref'],self.service.handlers.view.data['projection']);return body
    def grant(self,run_binding,work_ref,source_cut):
        p=self.control;context,policy=guard_original_producer(self.service,self.host,p['producer_policy_binding'],p['producer_source_binding'])
        need(sha(private_material(self.host,self.control_binding))==self.control_binding['sha256'],'private response control changed')
        raw=private_material(self.host,p['phase_grant_binding']);need(sha(raw)==p['phase_grant_binding']['sha256'],'independent phase permission changed');g=parse(raw)
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-response-permission.schema.json').read_bytes())).validate(g)
        need(g['principal_ref']==context['principal_ref'] and g['scope_ref']==self.descriptor['output_scope_ref'] and g['scope_ref'] in policy['scope_refs'] and g['run_binding']==run_binding and g['work_ref']==work_ref and g['source_cut']==source_cut==cut(self.host.handlers.view),'exact phase permission principal/Work/run/scope/cut differs')
        need(instant(g['not_before'])<=now()<min(instant(g['expires_at']),instant(policy['expires_at'])),'actual response phase permission expired/not started')
        role=self.current(g['role_assignment'],'role-assignment');owner=self.current(g['owner_principal'],'principal');contract=self.current(g['challenge_contract'],'challenge-contract');subject=self.current(g['subject'],g['subject_kind'])
        need(owner['node_id']==context['principal_ref'] and owner['payload']['status']=='active' and role['assignment_state']=='active' and role['role_ref']==g['role_ref'],'actual active response Principal/RoleAssignment differs')
        from .workflow_response_contract import recognize_signer,response_authority
        recognize_signer(policy['reader_public_key'],owner,context['principal_ref'],g['scope_ref'])
        need(g['authority_contract_binding']==p['authority_contract_binding'],'phase grant cannot substitute the independently selected authority contract')
        authority_raw=private_material(self.host,p['authority_contract_binding']);need(sha(authority_raw)==p['authority_contract_binding']['sha256'],'selected original response authority changed');authority=parse(authority_raw)
        permission_schema=parse((HERE/'workflow-response-permission.schema.json').read_bytes());Draft202012Validator(permission_schema['$defs']['response_authority']).validate(authority)
        role_body=self.current(authority['role'],'role');boundary=self.current(authority['authority_boundary'],'authority-boundary');assignee=self.current(authority['assignee'],authority['assignee_kind'])
        person=self.current(authority['person_reference'],'person-reference');membership=None if authority['team_membership']is None else self.current(authority['team_membership'],'team-membership')
        response_authority(authority,g,principal=owner,assignment=role,role=role_body,boundary=boundary,assignee=assignee,person=person,membership=membership,contract=contract,now=now(),instant=instant)
        need(instant(role['period']['start'])<=now() and (role['period']['end'] is None or now()<instant(role['period']['end'])),'original response role period expired')
        need(contract['payload']['owner_route']==g['owner_route'] and contract['scope_ref']==subject['scope_ref']==owner['scope_ref']==role['scope_ref']==g['scope_ref'],'exact original Contract/role/subject scope or selected response route differs')
        return g,context,policy,owner,contract,subject
    def respond(self,response_raw,signature_raw,*,run_binding,work_ref,source_cut):
        need(not self.pending,'response phase pending/completed; never redispatch');self.guard();p=self.control
        g,context,policy,owner,contract,subject=self.grant(run_binding,work_ref,source_cut)
        need(type(response_raw)is bytes and type(signature_raw)is bytes and len(response_raw)<=g['max_input_bytes'] and len(signature_raw)<=16384,'bounded actual authenticated response input required')
        need(self.factory is not None,'trusted actual predecessor output factory required')
        previous=self.factory.result('transition:challenge-handling:eligible')
        need(previous.work_ref==work_ref and previous.source_cut==source_cut and self.factory.plan['transitions']['transition:challenge-handling:eligible']['invocation_ref']==g['eligible_invocation_ref'],'actual eligible predecessor invocation lineage differs')
        from .workflow_producer_outputs import select_original_run
        select_original_run(self.host,previous,{'run_binding':run_binding,'source_cut':source_cut,'transition_ref':'transition:challenge-handling:responded'},{'next_run':{'work':{'version_ref':work_ref}}})
        rows,_=previous.material.selected(self.factory.plan['transitions']['transition:challenge-handling:eligible']['output_slot_ref']);need(len(rows)==1,'one exact eligible original Challenge required');old=rows[0]['artifact'];body=parse(rows[0]['raw'])
        need(body['kind']=='challenge-event' and body['payload']['response_state'] in ('open','submitted','eligible') and body['payload']['resolution_decision_ref'] in ('none','unresolved') and old['scope_ref']==g['scope_ref'],'actual eligible challenge posture/scope differs')
        need(body['payload']['challenge_contract_ref']==g['challenge_contract']['version_ref'] and body['payload']['subject_version_ref']==g['subject']['version_ref'] and body['payload']['subject_ref']==g['subject']['identity_ref'],'response original Contract/subject differs')
        from .workflow_response_contract import authenticate_response
        response,proof=authenticate_response(response_raw,signature_raw,public_key=policy['reader_public_key'],policy_binding=p['producer_policy_binding'],run_binding=run_binding,work_ref=work_ref,source_cut=source_cut,eligible_invocation_ref=g['eligible_invocation_ref'])
        selected_resolver(self.obligations.verify,{'resolver_binding':p['obligations_method_binding'],'resolver_entrypoint':'verify'},self.read_public,self.source_rows)
        obligations=copy.deepcopy(g['response_obligations']);obligations['response_binding']={'ref':'authenticated-challenge-response:'+sha(response_raw),'sha256':sha(response_raw)}
        challenger=self.current(obligations['challenger'],'principal')
        for accepted in obligations['accepted_evidence']:
            original=self.current(accepted['artifact'],accepted['kind']);from .artifact_model import record_bytes
            raw=record_bytes(self.service.handlers.view,self.service.handlers.resolve_exact(accepted['artifact']))[0]
            need(accepted['binding']['sha256']==sha(raw) and accepted['binding']['ref']==accepted['artifact']['version_ref'] and original['scope_ref']==g['scope_ref'],'actual selected original response evidence differs')
        bindings=[r['binding'] for r in obligations['accepted_evidence']]
        self.obligations.verify(obligations,rules=contract['payload'],challenge=body['payload'],challenge_header=old,contract_header=g['challenge_contract'],subject_header=g['subject'],owner_header=g['owner_principal'],challenger=challenger,response=response,evidence_bindings=bindings,now=now())
        # Only exact actual authenticated response permits this phase successor.
        successor=copy.deepcopy(body);successor['payload']['response_state']='responded';successor['payload']['evidence_refs']=list(dict.fromkeys(body['payload']['evidence_refs']+[b['ref'] for b in bindings]));successor['relation_refs']=list(body['relation_refs'])+[{'relation_kind_ref':'relation.successor-of','direction':'source','counterpart_kind':'challenge-event','counterpart_ref':old['identity_ref']}]
        raw=compact(successor);header={'scope_ref':old['scope_ref'],'identity_ref':old['identity_ref'],'version_ref':old['identity_ref']+'@'+p['record_version'],'carrier_ref':old['carrier_ref'],'byte_sha256':sha(raw)}
        need(header['version_ref']!=old['version_ref'],'genuine distinct response revision required');self.carriers.output(header,raw,scope_ref=g['scope_ref']);self.grant(run_binding,work_ref,source_cut)
        self.pending=True;writer=StageWriter(self.host,self.descriptor,self.guard);out=writer.write(raw);response_capture=writer.write(response_raw);signature_capture=writer.write(signature_raw)
        receipt={'schema_version':'lab-observed-authenticated-challenge-response-stage/v1-candidate','run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'phase_grant_binding':p['phase_grant_binding'],'authority_contract_binding':p['authority_contract_binding'],'producer_policy_binding':p['producer_policy_binding'],'original_role_assignment':g['role_assignment'],'original_contract':g['challenge_contract'],'original_subject':g['subject'],'predecessor':old,'response_binding':response_capture['original_binding'],'response_signature_binding':signature_capture['original_binding'],'actual_original_obligations_method':p['obligations_method_binding'],'artifact':header,'response_stage_observed':True,'resolution_Decision_created':False,'actual_owner_outcome':None,'canonical_admission_granted':False,'authority_effect':'none'}
        r=writer.write(compact(receipt));self.grant(run_binding,work_ref,source_cut);self.guard();selected_resolver(self.obligations.verify,{'resolver_binding':p['obligations_method_binding'],'resolver_entrypoint':'verify'},self.read_public,self.source_rows)
        return {'artifact':header,'receipt':receipt,'receipt_binding':r['original_binding'],'actual_authenticated_response':response,'actual_signature_input':proof,'original_output_material':{'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':{self.descriptor['output_slot_ref']:[{'artifact':header,**out}]},'action_receipts':[r,response_capture,signature_capture],'authority_effect':'none'}}
