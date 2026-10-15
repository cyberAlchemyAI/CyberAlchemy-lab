"""Actual readiness evaluation with exact prior product/pilot typed originals.

No implementation or pilot evidence is synthesized. The original full34/AC01..13
validator must accept actual independently attested evidence before these exact
current originals become output-bearing coordination observations.
"""
import copy
from .protocol import HERE,compact
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_material import selected_resolver
from .workflow_stage_producers import StageWriter
from .workflow_output_registry import selected_transition

class ProductReadinessOutputs:
    def __init__(self,host,readiness,*,control_binding,route_rows,read_public,source_rows,carriers,guard):
        self.host=host;self.readiness=readiness;self.control_binding=copy.deepcopy(control_binding);self.routes=copy.deepcopy(route_rows);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        need(len((self.descriptor if hasattr(self,'descriptor') else next(iter(self.routes.values())))['output_custody']['output_roots'])==1,'one explicitly selected capture root required before producer/capability')
        self.control=parse(host.vault.material(control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','original_method_binding','manifest_binding','selected_artifacts','authority_effect'))
        need(p['schema_version']=='lab-private-original-product-readiness-outputs/v1-candidate' and p['authority_effect']=='none','closed actual product readiness output control required')
        need(set(self.routes)=={'transition:product-adoption-release:candidate-assessed','transition:product-adoption-release:pilot-assessed'},'both original product assessment stages required')
        need(readiness.host.channel.guard()['principal_ref']==host.channel.guard()['principal_ref'] and cut(readiness.host.handlers.view)==cut(host.handlers.view) and len({compact(r['output_custody']) for r in self.routes.values()})==1,'actual independently authorized producer principal/source and exact product output custody required')
    def assess(self,*,run_binding,work_ref,source_cut):
        need(not self.pending,'product assessment pending/completed; never redispatch');self.guard();p=self.control
        need(sha(self.host.vault.material(self.control_binding))==self.control_binding['sha256'] and source_cut==cut(self.host.handlers.view),'actual product output control/source cut changed')
        from .workflow_transition import validate_control
        _,grant=validate_control(self.host.channel.policy_guard(),self.host.schemas)
        need(grant['run_binding']==run_binding and grant['source_cut']==source_cut and set(self.routes)<=set(grant['permitted_transitions']),'actual product assessment coordination permission differs')
        original=self.readiness.validate;selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':'ReleaseReadiness.validate'},self.read_public,self.source_rows)
        manifest=parse(self.host.vault.material(p['manifest_binding']));outputs=[];required={c for ref in self.routes for c in selected_transition(ref)['output_carriers']}
        member_bindings=manifest['implementation_bindings']+manifest['package_bindings']+manifest['pilot_evidence_bindings']
        for header in p['selected_artifacts']:
            need(header['carrier_ref'] in required,'unselected actual product output carrier')
            row=self.host.handlers.resolve_exact(header);need(row['effective_state'] in ('admitted-current','local-admitted-current'),'actual product/pilot original must be current')
            from .artifact_model import record_bytes
            raw=record_bytes(self.host.handlers.view,row)[0];body=self.carriers.output(header,raw,scope_ref=next(iter(self.routes.values()))['output_scope_ref'])
            need(any(b['sha256']==header['byte_sha256'] and b['ref'] in (header['version_ref'],header['identity_ref']) for b in member_bindings),'actual readiness manifest does not bind exact product/pilot original')
            if header['carrier_ref']=='cal.artifact-type.work-outcome-assessment/v1':need(body['payload']['subject_ref']==work_ref,'actual original pilot outcome names another Work')
            outputs.append((copy.deepcopy(header),raw))
        need({h['carrier_ref'] for h,_ in outputs}==required and len(outputs)==len({h['version_ref'] for h,_ in outputs}),'all exact product/pilot output originals required')
        self.pending=True;result=original(manifest,p['manifest_binding'],source_cut)
        need(result['result']=='ready-for-final-review' and result['gaps']==[] and result['release_decision_created'] is False and result['whole_lab_release_approved'] is False,'actual full product readiness assessment is blocked')
        writer=StageWriter(self.host,next(iter(self.routes.values())),self.guard);members=[{'artifact':h,**writer.write(raw)} for h,raw in outputs]
        receipt={'schema_version':'lab-observed-original-product-readiness-outputs/v1-candidate','run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'manifest_binding':p['manifest_binding'],'actual_readiness_result':result,'artifacts':[h for h,_ in outputs],'actual_prior_outputs_reused_explicitly':True,'new_implementation_or_pilot_invented':False,'release_decision_created':False,'authority_effect':'none'}
        r=writer.write(compact(receipt));slots={}
        for ref,row in self.routes.items():slots[row['output_slot_ref']]=[v for v in members if v['artifact']['carrier_ref'] in selected_transition(ref)['output_carriers']]
        self.guard();selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':'ReleaseReadiness.validate'},self.read_public,self.source_rows)
        return {'artifacts':receipt['artifacts'],'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':{'schema_version':'lab-private-produced-workflow-material/v1-candidate','slots':slots,'action_receipts':[r],'authority_effect':'none'}}
