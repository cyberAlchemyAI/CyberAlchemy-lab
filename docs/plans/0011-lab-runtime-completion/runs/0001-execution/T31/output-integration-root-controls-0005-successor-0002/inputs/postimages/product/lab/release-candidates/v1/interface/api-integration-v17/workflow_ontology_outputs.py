"""Authoritative original rich ontology hydration after actual cold commit.

The original fifteen-node/ten-edge calculation and native exact joins remain
unchanged. The selected record revision is a new explicit capture contract;
no record revision or typed header is inferred from a bare native event.
"""
import copy
from .protocol import ROOT,HERE,compact
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_material import selected_resolver,private_material
from .workflow_stage_producers import StageWriter
from .workflow_output_registry import selected_transition

class OntologyTypedCapture:
    def __init__(self,host,capability,*,module,control_binding,route_rows,read_public,source_rows,carriers,guard):
        self.host=host;self.capability=capability;self.module=module;self.control_binding=copy.deepcopy(control_binding);self.routes=copy.deepcopy(route_rows);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        need(len((self.descriptor if hasattr(self,'descriptor') else next(iter(self.routes.values())))['output_custody']['output_roots'])==1,'one explicitly selected capture root required before producer/capability')
        self.control=parse(private_material(host,control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','capability_binding','capability_entrypoint','rich_method_binding','record_version','view_template_binding','authority_effect'))
        need(p['schema_version']=='lab-private-original-ontology-hydration/v1-candidate' and p['authority_effect']=='none' and type(p['record_version'])is str and p['record_version'],'explicit original ontology capture/version contract required')
        need(set(self.routes)=={'transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated'},'both original rich ontology output stages required')
        need(len({compact(row['output_custody']) for row in self.routes.values()})==1 and len({row['output_scope_ref'] for row in self.routes.values()})==1,'one exact selected ontology output custody/scope required')
    def produce(self,*,run_binding,work_ref,source_cut):
        need(not self.pending,'ontology capture pending/completed; never redispatch');self.guard();p=self.control
        need(source_cut==cut(self.host.handlers.view) and sha(private_material(self.host,self.control_binding))==self.control_binding['sha256'],'original ontology source/control changed')
        selected_resolver(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']},self.read_public,self.source_rows)
        selected_resolver(self.module.rich_carriers,{'resolver_binding':p['rich_method_binding'],'resolver_entrypoint':'rich_carriers'},self.read_public,self.source_rows)
        raw=self.read_public(p['view_template_binding']);need(sha(raw)==p['view_template_binding']['sha256'] and (p['view_template_binding']['path'],p['view_template_binding']['sha256']) in self.source_rows,'original public ontology view template changed/absent')
        view_template=parse(raw);self.pending=True;snapshot=self.capability()
        closed(snapshot,('schema_version','principal_ref','work_ref','source_cut','store_ref','mapping_binding','mapping_policy_original','mapping_original_binding','mapping_original','manifest_binding','manifest_original','head_binding','head_original','native_read_binding','native_read_original','native_files','cold_replay_binding','cold_replay_original','expires_at','authority_effect'))
        need(snapshot['schema_version']=='lab-original-cold-ontology-material/v1-candidate' and snapshot['authority_effect']=='none' and snapshot['principal_ref']==self.host.channel.guard()['principal_ref'] and snapshot['work_ref']==work_ref and snapshot['source_cut']==source_cut,'actual original ontology scope/Work/cut differs')
        closed(snapshot['mapping_binding'],('ref','sha256'));closed(snapshot['mapping_original_binding'],('ref','sha256'))
        need(type(snapshot['mapping_policy_original'])is bytes and sha(snapshot['mapping_policy_original'])==snapshot['mapping_binding']['sha256'],'original mapper policy binding differs')
        need(type(snapshot['mapping_original'])is bytes and sha(snapshot['mapping_original'])==snapshot['mapping_original_binding']['sha256'],'distinct original mapping.json binding differs')
        for key in ('manifest','head','native_read','cold_replay'):
            closed(snapshot[key+'_binding'],('ref','sha256'));need(type(snapshot[key+'_original'])is bytes and sha(snapshot[key+'_original'])==snapshot[key+'_binding']['sha256'],'actual original ontology causal bytes differ')
        head=parse(snapshot['head_original']);manifest=parse(snapshot['manifest_original']);mapping=parse(snapshot['mapping_original']);native=parse(snapshot['native_read_original']);replay=parse(snapshot['cold_replay_original'])
        need(mapping['source_cut']==source_cut and manifest['native_read_sha256']==snapshot['native_read_binding']['sha256'] and head['generation_sha256']==snapshot['manifest_binding']['sha256'] and manifest['mapping_binding']==snapshot['mapping_binding'] and manifest['lab_source_cut']==source_cut,'actual ontology head/manifest/mapping/source correspondence differs')
        closed(replay,('schema_version','head_binding','manifest_binding','native_read_binding','cold_replayed','authority_effect'))
        need(replay['schema_version']=='lab-original-ontology-cold-correspondence/v1-candidate' and replay['head_binding']==snapshot['head_binding'] and replay['manifest_binding']==snapshot['manifest_binding'] and replay['native_read_binding']==snapshot['native_read_binding'] and replay['cold_replayed'] is True and replay['authority_effect']=='none','actual complete ontology cold correspondence absent')
        native_files=snapshot['native_files'];need(type(native_files)is dict and native_files,'actual original ontology files required')
        expected={r['path']:r['sha256'] for r in manifest['files']}
        need(set(native_files)=={name for name in expected if name.startswith(('semantic/','governance/'))},'full original native semantic/governance files required')
        for name,raw in native_files.items():need(type(raw)is bytes and sha(raw)==expected[name],'committed native original file changed')
        scope=next(iter(self.routes.values()))['output_scope_ref'];need(snapshot['store_ref']==scope,'actual original ontology store/output scope differs')
        bodies,nodes,edges,correspondence=self.module.rich_carriers(mapping,native_files,scope,snapshot['manifest_binding']['ref'],snapshot['principal_ref'])
        D=self.module.SOURCE.custody_delivery();native_cut=native['cut'];cutraw=compact(native_cut)
        identity='ontology-cut:owned-projection:'+sha(cutraw);body=D.common('ontology-cut',identity,scope,snapshot['manifest_binding']['ref']);body.update(owner_ref=snapshot['principal_ref'],claim_ceiling=self.module.CLAIM)
        body['payload'].update(ontology_ref=D.MAPPED.ONTOLOGY,node_refs=list(nodes.values()),edge_refs=list(edges.values()),semantic_cursor=native_cut['semantic_cursor'],source_event_set_digest=native_cut['source_event_set_digest'],calculated_digest=sha(cutraw),integrity_result='pass',replay_source=False);bodies[identity]=body
        view=copy.deepcopy(view_template);vid='ontology-view:T31-original-cold:'+sha(snapshot['head_original']);view.update(node_id=vid,name='Observed original cold ontology projection',owner_ref=snapshot['principal_ref'],scope_ref=scope,claim_ceiling=self.module.CLAIM,evidence_refs=[snapshot['native_read_binding']['ref'],snapshot['cold_replay_binding']['ref']],successor_refs=[])
        from .auth import now,instant
        need(now()<instant(snapshot['expires_at']),'actual original ontology permission expired')
        view['payload'].update(consumer_ref=snapshot['principal_ref'],cut_ref=identity,cut_digest=sha(cutraw),source_event_set_digest=native_cut['source_event_set_digest'],semantic_cursor=native_cut['semantic_cursor'],ontology_ref=D.MAPPED.ONTOLOGY,selector_ref=native['context']['context_selector_ref'],intended_use='Represent exact actually committed and cold-replayed source originals',freshness_at=now().isoformat(),expires_at=snapshot['expires_at'],selected_node_refs=list(nodes.values()),selected_edge_refs=list(edges.values()),exclusions=['Lab admission','global relation mutation','active Session memory'],replay_source=False);bodies[vid]=view
        writer=StageWriter(self.host,next(iter(self.routes.values())),self.guard);outputs=[]
        for identity,body in bodies.items():
            carrier='cal.artifact-type.'+body['kind']+('/v2' if body['kind']=='ontology-node' else '/v1');raw=compact(body)
            header={'scope_ref':scope,'identity_ref':identity,'version_ref':identity+'@'+p['record_version'],'carrier_ref':carrier,'byte_sha256':sha(raw)}
            self.carriers.output(header,raw,scope_ref=scope);outputs.append({'artifact':header,**writer.write(raw)})
        receipt={'schema_version':'lab-original-ontology-typed-capture/v1-candidate','run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'original_head_binding':snapshot['head_binding'],'original_manifest_binding':snapshot['manifest_binding'],'original_cold_replay_binding':snapshot['cold_replay_binding'],'record_version_contract':p['record_version'],'native_to_carrier_correspondence':correspondence,'artifacts':[r['artifact'] for r in outputs],'authority_effect':'none','work_satisfaction_asserted':False}
        r=writer.write(compact(receipt));slots={}
        for ref,row in self.routes.items():
            categories=set(selected_transition(ref)['output_carriers']);members=[v for v in outputs if v['artifact']['carrier_ref'] in categories];need({v['artifact']['carrier_ref'] for v in members}==categories,'complete original ontology output categories required');slots[row['output_slot_ref']]=members
        self.guard();selected_resolver(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']},self.read_public,self.source_rows)
        return {'artifacts':receipt['artifacts'],'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':{'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':slots,'action_receipts':[r],'authority_effect':'none'}}
