"""Versioned genuine design stages and guarded formal Session capture.

No constructor starts a producer, creates a Session, grants permission or writes
an output. Actual methods run only through the selected invocation factory.
"""
import copy,os,re,sys,stat
from pathlib import Path
from .protocol import compact,ROOT,HERE
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_material import PrivateOutputMaterial,selected_resolver

class StageWriter:
    def __init__(self,host,descriptor,guard):
        self.host=host;self.descriptor=descriptor;self.guard=guard
    def write(self,raw):
        self.guard();need(type(raw)is bytes and len(raw)<=16*1024*1024,'bounded original stage bytes required')
        # Reuse the exact held root/ancestor custody implementation. This object
        # does not install a resolver or call any producer.
        holder=object.__new__(PrivateOutputMaterial);holder.host=self.host;holder.descriptor=self.descriptor;holder.host_guard=self.guard
        root,handles,links,roots=holder.root_fd()
        try:
            need(len(roots)==1,'one explicitly selected stage output directory required');fd=root
            for part in roots[0].parts:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);handles.append(child);s=os.fstat(child);links.append((fd,part,child,(s.st_dev,s.st_ino)));fd=child
            holder.attached(links);name=sha(raw)+'.json';leaf=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=fd)
            try:
                data=memoryview(raw)
                while data:
                    written=os.write(leaf,data);need(written>0,'original stage write made no progress');data=data[written:]
                os.fsync(leaf);held=os.fstat(leaf);named=os.stat(name,dir_fd=fd,follow_symlinks=False)
                need(stat.S_ISREG(held.st_mode) and stat.S_IMODE(held.st_mode)==0o600 and (held.st_dev,held.st_ino,held.st_size)==(named.st_dev,named.st_ino,named.st_size) and held.st_size==len(raw),'new stage original changed/detached')
            finally:os.close(leaf)
            os.fsync(fd);holder.attached(links);self.guard()
            return {'path':(roots[0]/name).as_posix(),'original_binding':{'ref':'workflow-stage-original:'+sha(raw),'sha256':sha(raw)}}
        finally:
            for held in reversed(handles):os.close(held)

class DesignStageProducer:
    def __init__(self,host,workflow,*,control_binding,read_public,source_rows,carriers,guard):
        self.host=host;self.workflow=workflow;self.control_binding=copy.deepcopy(control_binding);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        raw=host.vault.material(control_binding);self.control=parse(raw);p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','transition_ref','original_method_binding','original_entrypoint','selection_sha256','record_template','version_ref','input_bindings','output_slot_ref','output_custody','authority_effect'))
        need(p['schema_version']=='lab-private-original-design-stage/v1-candidate' and p['authority_effect']=='none' and p['transition_ref'] in ('transition:engineering:designed','transition:research:designed'),'exact private original design-stage control required')
        self.manifest=getattr(workflow,'manifest',{});self.selection=getattr(workflow,'selection',{})
    def produce(self,*,run_binding,work_ref,source_cut):
        need(not self.pending,'design stage pending/completed; never redispatch');self.guard();p=self.control
        need(sha(self.host.vault.material(self.control_binding))==self.control_binding['sha256'],'private design-stage control changed')
        need(source_cut==cut(self.host.handlers.view),'actual design source cut differs')
        from .workflow_transition import validate_control
        _,grant=validate_control(self.host.channel.policy_guard(),self.host.schemas)
        need(grant['run_binding']==run_binding and grant['source_cut']==source_cut and p['transition_ref'] in grant['permitted_transitions'],'actual original design coordination permission differs')
        original=self.workflow.design
        selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':p['original_entrypoint']},self.read_public,self.source_rows)
        module=sys.modules[type(self.workflow).__module__];research=p['transition_ref']=='transition:research:designed'
        if research:
            selection,records,procedure=module.resolve(self.workflow.inputs,p['selection_sha256'])
            need(selection==self.workflow.selection and records==self.workflow.records and procedure==self.workflow.procedure and selection['work_ref']==work_ref,'actual original research design inputs differ')
        else:
            manifest,records=module.resolve_inputs(self.workflow.inputs,p['selection_sha256'])
            need(manifest==self.workflow.manifest and records==self.workflow.records and manifest['work_ref']==work_ref,'actual original engineering design inputs differ')
        body_template=copy.deepcopy(p['record_template']);context=self.host.channel.guard()
        need(body_template['owner_ref']==context['principal_ref'] and body_template['scope_ref']==grant['scope_ref'],'actual original design owner/scope differs')
        need(body_template['node_id'] not in {r['identity'] for r in self.host.handlers.view.subjects.values()},'new design output reuses an existing source identity')
        if research:
            original_design=records[selection['design_ref']];allowed={'node_id','created_at','last_updated_at','design_state','evidence_refs','run_refs'}
            need(all(body_template[k]==original_design[k] for k in original_design if k not in allowed),'new experiment design changes actual selected research semantics')
        else:need(body_template['kind']=='generated-output' and body_template['payload']=={},'actual design output template kind/payload differs')
        need(len(p['output_custody']['output_roots'])==1,'selected design capture root must be unique before effect')
        input_rows=[]
        for b in p['input_bindings']:
            raw=self.read_public(b);need(sha(raw)==b['sha256'] and (b['path'],b['sha256']) in self.source_rows,'selected public design input changed/absent')
            input_rows.append(copy.deepcopy(b))
        need(input_rows and self.workflow.state=='prepared','real selected design input closure/state required');before=len(self.workflow.events);self.pending=True
        original()
        need(self.workflow.state=='designed' and len(self.workflow.events)==before+1 and self.workflow.events[-1]['from']=='prepared' and self.workflow.events[-1]['to']=='designed','original design method did not observe its actual stage transition')
        selected_resolver(original,{'resolver_binding':p['original_method_binding'],'resolver_entrypoint':p['original_entrypoint']},self.read_public,self.source_rows);self.guard()
        for b in p['input_bindings']:need(sha(self.read_public(b))==b['sha256'],'original design input changed after design')
        context=self.host.channel.guard();body=copy.deepcopy(p['record_template']);need(body['owner_ref']==context['principal_ref'] and body['scope_ref'] in self.host.channel.policy_guard()['scope_refs'],'actual design output owner/scope permission differs')
        manifest={'schema_version':'lab-observed-original-design/v1-candidate','transition_ref':p['transition_ref'],'run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'input_bindings':input_rows,'original_design_event':copy.deepcopy(self.workflow.events[-1]),'original_method_binding':p['original_method_binding'],'authority_effect':'none','actual_owner_outcome':None,'execution_completed':False}
        writer=StageWriter(self.host,{'output_custody':p['output_custody']},self.guard);m=writer.write(compact(manifest))
        # The receipt authenticates original inputs/state/manifest, never this
        # eventual record digest, so GeneratedOutput's receipt link is acyclic.
        receipt={'schema_version':'lab-design-stage-receipt/v1-candidate','design_manifest_binding':m['original_binding'],'control_binding':self.control_binding,'work_ref':work_ref,'source_cut':source_cut,'actual_state':'designed','authority_effect':'none','completed_work_asserted':False}
        r=writer.write(compact(receipt))
        if research:
            old=records[selection['design_ref']]
            allowed={'node_id','created_at','last_updated_at','design_state','evidence_refs','run_refs'}
            need(all(body[k]==old[k] for k in old if k not in allowed),'new experiment design changes actual selected research semantics')
            need(body['node_id']!=old['node_id'] and body['design_state']=='ready' and body['run_refs']==[],'genuine new design-stage identity/state required')
            from .auth import now
            body['created_at']=body['last_updated_at']=now().strftime('%Y-%m-%dT%H:%M:%SZ')
            body['evidence_refs']=list(dict.fromkeys(body['evidence_refs']+[r['original_binding']['ref']]))
            carrier='cal.artifact-type.experiment-design/v1'
        else:
            need(body['payload']=={},'engineering design derived payload must be empty before actual observation')
            body['payload']={'generator_ref':p['original_method_binding']['path'],'input_refs':[b['path'] for b in input_rows],'output_digest':m['original_binding']['sha256'],'reproducibility_receipt_ref':r['original_binding']['ref']}
            carrier='cal.artifact-type.generated-output/v2'
        raw=compact(body);header={'scope_ref':body['scope_ref'],'identity_ref':body['node_id'],'version_ref':p['version_ref'],'carrier_ref':carrier,'byte_sha256':sha(raw)}
        self.carriers.output(header,raw,scope_ref=body['scope_ref']);out=writer.write(raw);self.guard()
        row={'artifact':header,**out};material={'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':{p['output_slot_ref']:[row]},'action_receipts':[r],'authority_effect':'none'}
        return {'original_design_observation':manifest,'artifact':header,'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':material}

class FormalSessionCapture:
    def __init__(self,host,service,custodian,*,descriptor,control_binding,read_public,source_rows,carriers,guard):
        need(service.sessions is custodian,'actual selected producer Session custodian required');self.host=host;self.service=service;self.custodian=custodian;self.descriptor=copy.deepcopy(descriptor);self.control_binding=copy.deepcopy(control_binding);control=parse(host.vault.material(control_binding));
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(control)
        closed(control,('schema_version','original_method_binding','custodian_method_binding','producer_policy_binding','producer_source_binding','authority_effect'));self.custodian_binding=copy.deepcopy(control['custodian_method_binding']);self.producer_policy_binding=copy.deepcopy(control['producer_policy_binding']);self.producer_source_binding=copy.deepcopy(control['producer_source_binding']);need(control['schema_version']=='lab-private-formal-Session-capture/v1-candidate' and control['authority_effect']=='none','closed formal Session capture selection required');self.original_binding=copy.deepcopy(control['original_method_binding']);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
    def open(self,raw):
        need(not self.pending,'formal Session capture pending/completed; never redispatch');self.guard();original=self.service.call;custodian_method=self.custodian.open
        from .service import Service
        from .workflow_producer_guard import guard_original_producer
        need(type(self.service)is Service and cut(self.service.handlers.view)==cut(self.host.handlers.view),'actual selected Session producer Service/source required');guard_original_producer(self.service,self.host,self.producer_policy_binding,self.producer_source_binding,operation='session.open')
        call=parse(raw);need(call['operation']=='session.open' and call['expected_source_cut']==cut(self.host.handlers.view),'exact original Session API operation/cut required')
        need(sha(self.host.vault.material(self.control_binding))==self.control_binding['sha256'],'formal Session control changed')
        need(len(self.descriptor['output_custody']['output_roots'])==1,'selected formal capture root must be unique before Session effect')
        need(self.custodian.channel.guard()['principal_ref']==self.host.channel.guard()['principal_ref'],'formal Session capture cannot transfer another principal permission')
        selected_resolver(original,{'resolver_binding':self.original_binding,'resolver_entrypoint':'Service.call'},self.read_public,self.source_rows)
        selected_resolver(custodian_method,{'resolver_binding':self.custodian_binding,'resolver_entrypoint':'ContextSessions.open'},self.read_public,self.source_rows);self.pending=True
        reply=original(raw);need(reply.get('kind')=='result' and reply.get('operation')=='session.open','actual original Session API call refused/unknown');result=reply['message'];resource=self.custodian.live[result['session_ref']];resource.guard()
        # Only the selected formal record and already validated connection
        # headers are accessed. resource.memory/signing keys are never read.
        formal=copy.deepcopy(resource.session);event=self.custodian.selected(result['session_ref']);headers=[]
        for row in event['connection_records']:
            for name in ('source_artifact','target_artifact'):
                h=row[name]
                if h['identity_ref']==result['session_ref'] and h['carrier_ref']=='cal.artifact-type.agent-session/v1' and h not in headers:headers.append(copy.deepcopy(h))
        need(len(headers)==1,'actual original Session ArtifactRef missing/ambiguous');header=headers[0]
        module=sys.modules[type(self.custodian).__module__];raw=module.source.encoded(formal)
        need(sha(raw)==header['byte_sha256'] and formal['node_id']==result['session_ref'] and event['source_cut']==result['source_cut'],'exact original live formal Session bytes/cut differ')
        need(result['source_cut']==cut(self.host.handlers.view),'formal Session belongs to another actual source cut')
        self.carriers.output(header,raw,scope_ref=self.descriptor['output_scope_ref']);writer=StageWriter(self.host,self.descriptor,self.guard);out=writer.write(raw)
        receipt={'schema_version':'lab-original-formal-Session-capture/v1-candidate','original_opening_result':result,'original_API_reply':reply,'formal_artifact':header,'source_cut':result['source_cut'],'Session_RAM_accessed':False,'signers_accessed':False,'authority_effect':'none'}
        r=writer.write(compact(receipt));resource.guard();guard_original_producer(self.service,self.host,self.producer_policy_binding,self.producer_source_binding,operation='session.open');self.guard();selected_resolver(original,{'resolver_binding':self.original_binding,'resolver_entrypoint':'Service.call'},self.read_public,self.source_rows)
        selected_resolver(custodian_method,{'resolver_binding':self.custodian_binding,'resolver_entrypoint':'ContextSessions.open'},self.read_public,self.source_rows)
        material={'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':{self.descriptor['output_slot_ref']:[{'artifact':header,**out}]},'action_receipts':[r],'authority_effect':'none'}
        return {'original_result':result,'artifact':header,'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':material}

class LearningOutcomeProducer:
    """Keep the original assessment and unapplied improvement proposal together."""
    def __init__(self,host,application,*,control_binding,read_public,source_rows,guard):
        self.host=host;self.application=application;self.e=application.e;self.control_binding=copy.deepcopy(control_binding);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.guard=guard;self.pending=False
        self.control=parse(host.vault.material(control_binding));closed(self.control,('schema_version','original_method_binding','authority_effect'))
        need(self.control['schema_version']=='lab-private-original-learning-outcome/v1-candidate' and self.control['authority_effect']=='none','closed original learning outcome control required')
    def produce(self,*,requested_disposition=None,claimed_benefit=None):
        need(not self.pending,'learning assessment/proposal pending or completed; never redispatch');self.guard()
        need(sha(self.host.vault.material(self.control_binding))==self.control_binding['sha256'],'private learning outcome control changed')
        for name in ('assess','propose_improvement'):
            selected_resolver(getattr(self.application,name),{'resolver_binding':self.control['original_method_binding'],'resolver_entrypoint':'LessonApplicationService.'+name},self.read_public,self.source_rows)
        self.pending=True
        outcome=self.application.assess(requested_disposition=requested_disposition,claimed_benefit=claimed_benefit)
        signal,target,effect=self.application.propose_improvement()
        self.guard()
        for name in ('assess','propose_improvement'):
            selected_resolver(getattr(self.application,name),{'resolver_binding':self.control['original_method_binding'],'resolver_entrypoint':'LessonApplicationService.'+name},self.read_public,self.source_rows)
        return {'original_outcome_ref':outcome,'original_improvement_signal_ref':signal,'original_unapplied_target_ref':target,'original_unapplied_effect_ref':effect,'authority_effect':'none'}
