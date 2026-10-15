"""Exact current-source workflow coordination under a private selected grant.

An eligible Intent Resolution, Decision and typed edge are source evidence.
Only the separately provisioned policy permits this owned coordination effect.
No completed Work, human owner outcome or repository admission is inferred.
"""
import copy
import importlib
import importlib.util
from pathlib import Path
import sys

from .protocol import HERE,ROOT,source,compact,binding
from .auth import now,instant
from .handlers import ApplicationError,cut,gap
from . import artifact_model as model
from .workspace import privacy,safe

PACKAGE=HERE.parent/'workflow-transition-v1';NAME='_cal_selected_workflow_transition_v1'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PACKAGE/'__init__.py',submodule_search_locations=[str(PACKAGE)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
K=importlib.import_module(NAME+'.kernel');J=importlib.import_module(NAME+'.journal')
source.require(Path(K.__file__).resolve()==PACKAGE/'kernel.py' and Path(J.__file__).resolve()==PACKAGE/'journal.py',
    'unselected workflow kernel/journal')

def validate_control(policy,schemas):
    """Only actual private policy selection can bind a workflow route."""
    from .workspace import validate_scope,read_private
    source.require(policy['schema_version']=='lab-local-workflow-transition-policy/v1-candidate',
        'independent workflow policy required')
    control=policy['workflow_control']
    source.require(set(control)=={'routing_binding','kernel_binding','journal_binding'}
        and control['kernel_binding']==binding(str((PACKAGE/'kernel.py').relative_to(ROOT)),(PACKAGE/'kernel.py').read_bytes())
        and control['journal_binding']==binding(str((PACKAGE/'journal.py').relative_to(ROOT)),(PACKAGE/'journal.py').read_bytes()),
        'independent workflow method differs')
    root,manifest=validate_scope(policy);selected=control['routing_binding']
    matches=[r for r in manifest['materials'] if r['ref']==selected['ref'] and r['sha256']==selected['sha256']]
    source.require(len(matches)==1,'workflow routing lacks exact independent original material')
    raw=read_private(root/matches[0]['path']);source.require(source.sha(raw)==selected['sha256'],'workflow routing changed')
    row=source.parse(raw)
    source.require(set(row)=={'schema_version','grant_binding','journal_root','journal_config_sha256'}
        and row['schema_version']=='lab-owned-workflow-routing/v1-candidate', 'closed workflow routing required')
    relative=Path(row['journal_root'])
    source.require(not relative.is_absolute() and '..' not in relative.parts and relative.as_posix()==row['journal_root']
        and len(relative.parts)==2 and relative.parts[0]=='workflows','owned workflow journal path differs')
    safe(root/'workflows',0o700);safe(root/relative,0o700)
    store=J.Journal(root/relative,row['journal_config_sha256'])
    source.require(store.config['principal_ref']==policy['principal_ref'] and store.config['scope_ref']==policy['scope_refs'][0],
        'workflow journal principal/scope differs')
    grant_matches=[r for r in manifest['materials'] if r['ref']==row['grant_binding']['ref']
        and r['sha256']==row['grant_binding']['sha256']]
    source.require(len(grant_matches)==1,'independent workflow grant missing')
    grant_raw=read_private(root/grant_matches[0]['path'])
    source.require(source.sha(grant_raw)==row['grant_binding']['sha256'],'workflow grant changed')
    grant=source.parse(grant_raw)
    source.require(grant['principal_ref']==policy['principal_ref'] and grant['scope_ref']==policy['scope_refs'][0]
        and instant(grant['not_before'])<=now()<min(instant(grant['expires_at']),instant(policy['expires_at']))
        and grant['permitted_effects']==['candidate-workflow-transition'],'workflow grant principal/scope/period/effects differ')
    return row,grant

class WorkflowTransition:
    def __init__(self,host):
        service=importlib.import_module(__package__+'.service');auth=importlib.import_module(__package__+'.auth')
        source.require(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,
            'actual workflow Service/ReaderChannel required')
        self.host=host;self.initial_policy=copy.deepcopy(host.channel.policy_guard())
        self.route,self.grant=validate_control(self.initial_policy,host.schemas)
        self.store=J.Journal(host.vault.root/self.route['journal_root'],self.route['journal_config_sha256'])
    def original(self,b):
        raw=self.host.vault.material(b);privacy(source.parse(raw));return raw
    def selected(self,header):
        view=self.host.handlers.view;row=view.subjects.get(header['version_ref'])
        source.require(row is not None and row['effective_state'] in K.CURRENT and model.artifact_ref(view,row)==header,
            'workflow reference is not exact/current in the selected signed source')
        raw=model.record_bytes(view,row)[0]
        source.require(source.sha(raw)==header['byte_sha256'] and source.parse(raw)==row['record'],
            'workflow original record differs')
        return row
    def current_identity(self,ref,kind):
        rows=[r for r in self.host.handlers.view.subjects.values() if r['effective_state'] in K.CURRENT
            and r['kind']==kind and (r['version_ref']==ref or r['identity']==ref)]
        source.require(len(rows)==1,'workflow semantic endpoint missing, ambiguous or historical')
        return rows[0]
    def semantics(self,run,definition):
        # Binding a header is insufficient: the actual current source must
        # express this Intent interpretation and one Goal's coordinated Work.
        intent=self.selected(run['intent']);resolution=self.selected(run['intent_resolution'])
        work=self.selected(run['work']);coordination=self.selected(run['coordination_context'])
        self.selected(definition['decision_profile'])
        source.require(coordination['record']['project_ref']==self.grant['scope_ref']
            and coordination['record']['goal_ref'] in work['record']['payload']['goal_refs'],
            'workflow Work/Goal/Coordination scope does not close')
        goal=self.current_identity(coordination['record']['goal_ref'],'goal')
        source.require(goal['record']['project_ref']==self.grant['scope_ref'] if 'project_ref' in goal['record'] else
            any(r['record'].get('payload',{}).get('relation_kind_ref')=='relation.member-of'
                and r['record']['payload']['source']['version_ref']==goal['version_ref']
                and r['record']['payload']['target']['ref']==self.grant['scope_ref']
                and r['effective_state'] in K.CURRENT for r in self.host.handlers.view.subjects.values()),
            'workflow current Goal membership is unresolved')
        p=resolution['record']['payload']
        source.require(p['intent_ref'] in (intent['identity'],intent['version_ref'])
            and any(ref in p['selected_subject_refs'] for ref in (work['identity'],work['version_ref']))
            and not any(ref in p['excluded_subject_refs'] for ref in (work['identity'],work['version_ref'])),
            'workflow Intent Resolution does not select this exact Work')
        decision=self.current_identity(p['owner_decision_ref'],'decision');d=decision['record']['payload']
        source.require(resolution['version_ref'] in d['subject_refs'] and d['declared_effect_refs'],
            'workflow Resolution lacks its exact observed Decision declaration')
        for ref in d['declared_effect_refs']:
            effect=self.current_identity(ref,'effect')
            source.require(effect['record']['payload']['subject_ref']==resolution['version_ref'],
                'workflow declared Effect names another Resolution')
        edges=[r for r in self.host.handlers.view.subjects.values() if r['kind']=='typed-relation'
            and r['effective_state'] in K.CURRENT and r['record']['payload']['relation_kind_ref']=='relation.declares-effect-on'
            and r['record']['payload']['source']['version_ref']==decision['version_ref']
            and r['record']['payload']['target']['version_ref']==resolution['version_ref']]
        source.require(len(edges)==1 and edges[0]['record']['payload']['qualifiers']['exact_target_version_ref']==resolution['version_ref'],
            'workflow exact Decision/Resolution relation is unresolved')
        self.host.handlers.view.handle.operations.validate_relation(edges[0]['record'],self.host.handlers.view.data['projection'])
    def host_guard(self):
        from .integrated_guard import guard_host,require_outside
        require_outside();guard_host(self.host)
        policy=self.host.channel.policy_guard();route,grant=validate_control(policy,self.host.schemas)
        source.require(policy==self.initial_policy and route==self.route and grant==self.grant,
            'workflow actual independent permission/routing changed')
    def preflight(self,message,outer,key):
        source.require(message['idempotency_key']==key and message['source_cut']==outer==cut(self.host.handlers.view),
            'workflow request/key/current source cut differs')
        self.host_guard()
        from .guarded_candidate import selection
        with selection(self.host):
            facts={name:self.original(message[name]) for name in ('definition_binding','run_binding',
                'authority_evaluation_binding','satisfaction_report_binding')}
            run=source.parse(facts['run_binding']);definition=source.parse(facts['definition_binding'])
            self.semantics(run,definition)
            headers={}
            for header in [run[k] for k in ('intent','intent_resolution','work','coordination_context')]+message['input_artifacts']:
                row=self.selected(header);headers[header['version_ref']]={'artifact':header,'posture':row['effective_state'],'semantic_kind':row['kind']}
            obligations=copy.deepcopy(self.grant['obligation_bindings'])
            for bindings in obligations.values():
                for b in bindings:self.original(b)
            for b in message['action_receipt_bindings']:self.original(b)
            context=self.host.channel.context;actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
            actor['role_assignment_refs']=context['role_assignment_bindings']
            self.plan=K.plan(message,definition_raw=facts['definition_binding'],run_raw=facts['run_binding'],
                authority_raw=facts['authority_evaluation_binding'],satisfaction_raw=facts['satisfaction_report_binding'],
                host_grant=self.grant,authenticated_actor=actor,current_cut=cut(self.host.handlers.view),
                selected_headers=headers,selected_obligations=obligations,now=now())
            # Output producers must be separately implemented and verified. A
            # transition cannot silently drop its declared domain outputs.
            source.require(self.plan['allowed_output_carriers']==[],'workflow transition requires unavailable exact output producers')
        self.host_guard()
        return self.plan
    def apply(self,message,request,outer,key):
        self.host_guard()
        tx=self.store.apply(self.plan,request_binding=request,host_guard=self.host_guard)
        self.host_guard();head,raw=self.store.replay()
        source.require(source.parse(raw)==self.plan['next_run'] and tx['event']==self.plan['event']
            and head['run_sha256']==tx['next_run_sha256'],'workflow observed transaction/run differs')
        evidence=self.host.vault.object(compact(tx));event=self.host.vault.object(compact(tx['event']))
        result={'schema_version':'lab-workflow-transition-receipt/v1-candidate','request_binding':request,
            'run_ref':tx['event']['run_ref'],'from_state':tx['event']['from_state'],'to_state':tx['event']['to_state'],
            'posture':'applied','event_binding':event,'output_artifact_refs':[],
            'evidence_bindings':[evidence],'gaps':[],'recovery_required':False,'authority_effect':'none',
            'claim_ceiling':'Observed test-owned coordination transaction with exact current source and independent private grant. No Work satisfaction, human owner outcome, canonical admission or external effect.'}
        source.require(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:workflow-transition-receipt:v1-candidate',result),
            'workflow actual result violates its exact closed contract')
        self.host_guard();return result,[evidence,event]
