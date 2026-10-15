"""Read-only, predeclared original repository migration scope assessment.

Produces a new candidate-unapproved manifest revision and a real byte-comparison
receipt. It never copies a repository, infers execution authority or discovers
expected values from the same ambient files it checks.
"""
from .workflow_output_material import private_material
import copy
from pathlib import PurePosixPath
from .protocol import HERE,compact
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha,pointer
from .workflow_stage_producers import StageWriter

class MigrationScopeAssessment:
    def __init__(self,host,*,control_binding,descriptor,read_public,source_rows,carriers,guard):
        self.host=host;self.control_binding=copy.deepcopy(control_binding);self.descriptor=copy.deepcopy(descriptor);self.read_public=read_public;self.source_rows=frozenset(source_rows);self.carriers=carriers;self.guard=guard;self.pending=False
        need(len((self.descriptor if hasattr(self,'descriptor') else next(iter(self.routes.values())))['output_custody']['output_roots'])==1,'one explicitly selected capture root required before producer/capability')
        self.control=parse(private_material(host,control_binding));p=self.control
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-stage-controls.schema.json').read_bytes())).validate(p)
        closed(p,('schema_version','manifest_template_binding','scope_inputs_binding','manifest_id','record_version','authority_effect'))
        need(p['schema_version']=='lab-private-original-migration-assessment/v1-candidate' and p['authority_effect']=='none','closed original migration assessment control required')
    def public(self,b):
        closed(b,('path','sha256'));raw=self.read_public(b);need((b['path'],b['sha256']) in self.source_rows and sha(raw)==b['sha256'],'preselected original migration source changed/absent');return raw
    def assess(self,*,run_binding,work_ref,source_cut):
        need(not self.pending,'migration assessment pending/completed; never redispatch');self.guard();p=self.control
        need(sha(private_material(self.host,self.control_binding))==self.control_binding['sha256'] and source_cut==cut(self.host.handlers.view),'actual migration control/source cut differs')
        from .workflow_transition import validate_control
        _,grant=validate_control(self.host.channel.policy_guard(),self.host.schemas)
        need(grant['run_binding']==run_binding and grant['source_cut']==source_cut and self.descriptor['output_scope_ref']==grant['scope_ref'] and self.descriptor['transition_ref'] in grant['permitted_transitions'],'actual original migration assessment permission differs')
        original=parse(self.public(p['manifest_template_binding']));inputs=parse(self.public(p['scope_inputs_binding']))
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-migration-inputs.schema.json').read_bytes())).validate(inputs)
        need(original['authority_effect']=='none' and original['execution_authority'] is False and original['status']=='candidate-unapproved','original migration template grants no execution/adoption authority')
        refs={'source_inventory':original['source_repository']['inventory'],'target_baseline':original['target_repository']['baseline'],'architecture':original['architecture'],'mapping_rules':original['mapping_rules'],'exclusions':original['exclusion_inventory'],'allowlist':original['copy_allowlist'],'expected_postimage':original['expected_postimage']}
        documents={key:parse(self.public(b)) for key,b in refs.items()}
        def rows(key):
            selector=inputs['row_selectors'][key];value=pointer(documents[key],selector['rows_pointer']);need(type(value)is list,'actual original migration declaration rows required');out={}
            for row in value:
                name=pointer(row,selector['path_pointer']);pin=pointer(row,selector['sha256_pointer']);path=PurePosixPath(name)
                need(type(name)is str and str(path)==name and not path.is_absolute() and all(v not in ('..','.') for v in path.parts) and '\\' not in name and path.parts and name not in out,'canonical unique original migration declaration path required')
                need(type(pin)is str and len(pin)==64 and all(c in '0123456789abcdef' for c in pin),'exact original migration declaration digest required');out[name]=pin
            return out
        source=rows('source_inventory');baseline=rows('target_baseline');expected=rows('expected_postimage');allow=inputs['copies'];observed=[];post=dict(baseline)
        # Inputs are independently selected complete declaration projections.
        need(len(inputs['source_files'])==len(source) and len(inputs['target_baseline_files'])==len(baseline) and source=={r['declared_path']:r['binding']['sha256'] for r in inputs['source_files']} and baseline=={r['declared_path']:r['binding']['sha256'] for r in inputs['target_baseline_files']},'full original selected scope declaration conservation differs')
        for group in ('source_files','target_baseline_files'):
            for row in inputs[group]:self.public(row['binding']);observed.append(copy.deepcopy(row))
        allowlist=pointer(documents['allowlist'],inputs['allowlist_pointer']);need(allowlist==allow,'original complete copy allowlist differs')
        excluded=pointer(documents['exclusions'],inputs['exclusions_pointer']);need(type(excluded)is list and all(type(x)is str for x in excluded),'original explicit migration exclusions required')
        for row in allow:
            need(row['source_path'] in source and row['target_path'] not in post and row['source_path'] not in excluded and row['target_path'] not in excluded,'original additive migration copy/exclusion/preimage constraint differs')
            need(row['expected_sha256']==source[row['source_path']],'independently declared copy byte identity differs');post[row['target_path']]=row['expected_sha256']
        need(post==expected and len({r['target_path'] for r in allow})==len(allow),'entire original baseline plus additive expected postimage differs')
        body=copy.deepcopy(original);need(p['manifest_id']!=original['migration_manifest_id'],'new actual assessment manifest identity required');body.update(migration_manifest_id=p['manifest_id'],version=p['record_version'])
        raw=compact(body);header={'scope_ref':self.descriptor['output_scope_ref'],'identity_ref':body['migration_manifest_id'],'version_ref':body['migration_manifest_id']+'@'+body['version'],'carrier_ref':'cal.artifact-type.repository-migration-manifest/v1','byte_sha256':sha(raw)};self.carriers.output(header,raw,scope_ref=self.descriptor['output_scope_ref'])
        self.pending=True;writer=StageWriter(self.host,self.descriptor,self.guard);out=writer.write(raw)
        receipt={'schema_version':'lab-observed-original-migration-assessment/v1-candidate','run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'original_manifest_binding':p['manifest_template_binding'],'scope_inputs_binding':p['scope_inputs_binding'],'actual_compared_originals':observed,'source_count':len(source),'baseline_count':len(baseline),'additive_copy_count':len(allow),'expected_postimage_count':len(expected),'artifact':header,'repository_copies_performed':0,'source_mutated':False,'execution_authority':False,'authority_effect':'none'}
        r=writer.write(compact(receipt));self.guard()
        for b in refs.values():self.public(b)
        return {'artifact':header,'receipt':receipt,'receipt_binding':r['original_binding'],'original_output_material':{'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':{self.descriptor['output_slot_ref']:[{'artifact':header,**out}]},'action_receipts':[r],'authority_effect':'none'}}
