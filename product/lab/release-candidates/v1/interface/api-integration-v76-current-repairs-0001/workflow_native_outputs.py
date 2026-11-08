"""Typed originals from an actual committed and cold-observed native outcome.

This adapter never opens a native writer, grants authority or constructs native
Core/State/history/Decision contents. The selected publisher capability supplies
original transaction/replay bytes and explicit causal selectors into them.
"""
import base64,copy
from .protocol import compact,HERE
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha,pointer
from .workflow_output_material import selected_resolver,private_material
from .workflow_stage_producers import StageWriter
from .workflow_output_registry import selected_transition

class NativeTypedResultAdapter:
    def __init__(self,host,capability,*,control_binding,route_rows,read_public,source_rows,carriers,guard):
        self.host=host;self.capability=capability;self.control_binding=copy.deepcopy(control_binding);self.routes=copy.deepcopy(route_rows);self.descriptor=copy.deepcopy(next(iter(route_rows.values())));self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        need(self.routes and len({compact(r['output_custody']) for r in self.routes.values()})==1 and len({r['output_scope_ref'] for r in self.routes.values()})==1,'one exact native capture output custody/scope required')
        need(len((self.descriptor if hasattr(self,'descriptor') else next(iter(self.routes.values())))['output_custody']['output_roots'])==1,'one explicitly selected capture root required before producer/capability')
        self.control=parse(private_material(host,control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','capability_binding','capability_entrypoint','operation','native_store_ref','native_branch_ref','native_domain','head_value_pointer','record_roles','authority_effect'))
        need(p['schema_version']=='lab-private-native-typed-output/v1-candidate' and p['authority_effect']=='none' and p['native_domain'] in ('sealed-admission-transaction','ontology-generation-head','repository-bundle-manifest'),'selected private native output domain contract required')
    def capture(self,*,run_binding,work_ref,source_cut):
        need(not self.pending,'native typed capture pending/completed; never redispatch');self.guard();p=self.control
        need(source_cut==cut(self.host.handlers.view) and sha(private_material(self.host,self.control_binding))==self.control_binding['sha256'],'native output control/Lab source changed')
        selected_resolver(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']},self.read_public,self.source_rows)
        self.pending=True
        # Root's selected capability performs/observes its original guarded
        # operation. It must return only after actual commit and cold replay;
        # unknown outcomes cannot be turned into typed results by this adapter.
        outcome=self.capability()
        closed(outcome,('schema_version','operation','principal_ref','work_ref','source_cut','native_store_ref','native_branch_ref','native_domain','transaction_binding','transaction_original','replay_binding','replay_original','records','authority_effect'))
        need(outcome['schema_version']=='lab-original-native-typed-outcome/v2-candidate' and outcome['authority_effect']=='none' and outcome['operation']==p['operation'],'closed actual native outcome required')
        need(outcome['principal_ref']==self.host.channel.guard()['principal_ref'] and outcome['work_ref']==work_ref and outcome['source_cut']==source_cut and outcome['native_store_ref']==p['native_store_ref'] and outcome['native_branch_ref']==p['native_branch_ref'] and outcome['native_domain']==p['native_domain'],'actual native principal/Work/cut/store/branch differs')
        for key in ('transaction','replay'):
            closed(outcome[key+'_binding'],('ref','sha256'));need(type(outcome[key+'_original'])is bytes and sha(outcome[key+'_original'])==outcome[key+'_binding']['sha256'],'native original causal bytes differ')
        native={'transaction':parse(outcome['transaction_original']),'replay':parse(outcome['replay_original'])}
        # The read-only capability must expose these actual cold-observation
        # correspondences, with original digests. A success flag is insufficient.
        replay=native['replay'];closed(replay,('schema_version','store_ref','branch_ref','native_domain','head_value','original_transaction_sha256','committed','cold_replayed','record_set','authority_effect'))
        need(replay['schema_version']=='lab-native-cold-typed-observation/v2-candidate' and replay['authority_effect']=='none' and replay['committed'] is True and replay['cold_replayed'] is True and replay['store_ref']==p['native_store_ref'] and replay['branch_ref']==p['native_branch_ref'] and replay['native_domain']==p['native_domain'] and replay['head_value']==pointer(native['transaction'],p['head_value_pointer']) and replay['original_transaction_sha256']==outcome['transaction_binding']['sha256'],'actual native cold commit/original transaction correspondence missing')
        writer=StageWriter(self.host,self.descriptor,self.guard);outputs=[];roles=[]
        for row in outcome['records']:
            closed(row,('role','causal_source','header_pointer','scope_pointer','original_pointer','original_encoding','original_bytes'))
            need(row['role'] in p['record_roles'] and row['causal_source'] in native,'unselected native result role/origin')
            observed=native[row['causal_source']];header=pointer(observed,row['header_pointer']);raw=row['original_bytes'];closed(header,('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'))
            need(type(raw)is bytes and sha(raw)==header['byte_sha256'],'exact native result body/header differs')
            original=pointer(observed,row['original_pointer'])
            if row['original_encoding']=='base64-original':need(type(original)is str and base64.b64decode(original,validate=True)==raw,'native original bytes do not match actual causal record')
            else:need(row['original_encoding']=='original-json-value' and original==parse(raw),'native original JSON differs from observed projection record')
            proof=copy.deepcopy(pointer(observed,row['scope_pointer']));need(proof['work_ref']==work_ref and proof['source_cut']==source_cut and proof['principal_ref']==outcome['principal_ref'],'actual native scope proof invocation differs');route=next(ref for ref in self.routes if header['carrier_ref'] in selected_transition(ref)['output_carriers'])
            self.carriers.output(header,raw,scope_ref=self.descriptor['output_scope_ref'],transition_ref=route,scope_proof=proof,invocation_lineage={'run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'principal_ref':outcome['principal_ref']});material=writer.write(raw)
            outputs.append({'artifact':copy.deepcopy(header),'scope_proof':proof,**material});roles.append(row['role'])
        need(set(roles)==set(p['record_roles']),'complete independently selected native result-role closure required')
        categories={c for ref in self.routes for c in selected_transition(ref)['output_carriers']}
        need({row['artifact']['carrier_ref'] for row in outputs}==categories,'all original transition typed native outputs required')
        receipt={'schema_version':'lab-observed-native-workflow-output/v1-candidate','operation':p['operation'],'run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'transaction_binding':outcome['transaction_binding'],'replay_binding':outcome['replay_binding'],'artifacts':[row['artifact'] for row in outputs],'scope_contract_binding':self.descriptor['scope_contract_binding'],'scope_correspondences':[row['scope_proof'] for row in outputs],'authority_effect':'none','work_satisfaction_asserted':False}
        r=writer.write(compact(receipt));self.guard();selected_resolver(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']},self.read_public,self.source_rows)
        slots={row['output_slot_ref']:[v for v in outputs if v['artifact']['carrier_ref'] in selected_transition(ref)['output_carriers']] for ref,row in self.routes.items()}
        material={'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':slots,'action_receipts':[r],'authority_effect':'none'}
        return {'artifacts':receipt['artifacts'],'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':material}
