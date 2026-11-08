"""Capture actual authorized Service.call replies and their original typed objects."""
import copy
from .protocol import HERE,compact
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_material import selected_resolver,private_material
from .workflow_stage_producers import StageWriter
from .workflow_output_registry import selected_transition

FIELDS={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'}
class AuthorizedAPIProducer:
    def __init__(self,host,service,*,control_binding,route_rows,read_public,source_rows,carriers,guard):
        self.host=host;self.service=service;self.control_binding=copy.deepcopy(control_binding);self.routes=copy.deepcopy(route_rows);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        self.control=parse(private_material(host,control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','original_method_binding','producer_policy_binding','producer_source_binding','operation','authority_effect'))
        need(p['schema_version']=='lab-private-authorized-API-output/v1-candidate' and p['authority_effect']=='none','closed original API invocation selection required')
        need(self.routes and len({compact(r['output_custody']) for r in self.routes.values()})==1,'same actual authorized API invocation must keep output custody')
        descriptor=next(iter(self.routes.values()));need(descriptor['output_custody']['root']==str(service.vault.root) and descriptor['output_custody']['output_roots']==['objects'],'actual original API vault custody must be selected before dispatch')
    def invoke(self,raw):
        need(not self.pending,'authorized API producer pending/completed; never redispatch');self.guard();p=self.control
        need(sha(private_material(self.host,self.control_binding))==self.control_binding['sha256'],'authorized API producer selection changed')
        call=parse(raw);need(call['operation']==p['operation'] and call['expected_source_cut']==cut(self.host.handlers.view)==cut(self.service.handlers.view),'exact original API operation/cut differs')
        from .service import Service
        from .workflow_producer_guard import guard_original_producer
        need(type(self.service)is Service and self.service.channel.guard()['principal_ref']==self.host.channel.guard()['principal_ref'] and next(iter(self.routes.values()))['output_scope_ref'] in self.service.channel.policy_guard()['scope_refs'],'original producer Service principal/scope permission differs')
        guard_original_producer(self.service,self.host,p['producer_policy_binding'],p['producer_source_binding'],operation=p['operation']);original=self.service.call;selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':'Service.call'},self.read_public,self.source_rows)
        # Preserve the actual Service nonce/deadline/request, grant/effect-budget,
        # idempotency, dispatch, full-source entry/exit and journal boundary.
        self.pending=True;reply=original(raw)
        need(type(reply)is dict and reply.get('kind')=='result' and reply.get('operation')==p['operation'],'original API did not return its actual successful result')
        domain=reply['message'];need(domain.get('posture') not in ('pending','indeterminate','recovery-required','failed') and domain.get('recovery_required') is not True,'partial API result requires reconciliation; never redispatch')
        required={c for ref in self.routes for c in selected_transition(ref)['output_carriers']};outputs={}
        def walk(node):
            if type(node)is dict:
                if set(node) in (FIELDS,FIELDS|{'candidate_contract_binding'}) and node['carrier_ref'] in required:
                    # Original candidate targets permit exactly this extra contract
                    # selector; it is not a sixth public ArtifactRef dimension.
                    h={k:copy.deepcopy(node[k]) for k in FIELDS};body=self.service.vault.object_read({'ref':'workspace-object:'+self.service.vault.manifest['workspace_ref']+':'+h['byte_sha256'],'sha256':h['byte_sha256']})
                    self.carriers.output(h,body,scope_ref=next(iter(self.routes.values()))['output_scope_ref'])
                    need(h['version_ref'] not in outputs or outputs[h['version_ref']]['artifact']==h,'conflicting actual API output headers')
                    outputs[h['version_ref']]={'artifact':h,'path':'objects/'+h['byte_sha256']+'.json','original_binding':{'ref':'workspace-object:'+self.service.vault.manifest['workspace_ref']+':'+h['byte_sha256'],'sha256':h['byte_sha256']}}
                for child in node.values():walk(child)
            elif type(node)in (tuple,list):
                for child in node:walk(child)
        walk(reply)
        descriptor=next(iter(self.routes.values()));need(descriptor['output_custody']['root']==str(self.service.vault.root) and descriptor['output_custody']['output_roots']==['objects'],'authorized API objects must use their actual original selected vault custody')
        receipt=StageWriter(self.host,descriptor,self.guard).write(compact(reply));slots={}
        for ref,row in self.routes.items():
            categories=set(selected_transition(ref)['output_carriers']);members=[v for v in outputs.values() if v['artifact']['carrier_ref'] in categories]
            need({v['artifact']['carrier_ref'] for v in members}==categories,'actual authorized API reply lacks full original typed carrier closure')
            slots[row['output_slot_ref']]=members
        guard_original_producer(self.service,self.host,p['producer_policy_binding'],p['producer_source_binding'],operation=p['operation']);self.guard();selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':'Service.call'},self.read_public,self.source_rows)
        return {'original_reply':reply,'receipt':reply,'receipt_binding':receipt['original_binding'],'original_output_material':{'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':slots,'action_receipts':[receipt],'authority_effect':'none'}}
