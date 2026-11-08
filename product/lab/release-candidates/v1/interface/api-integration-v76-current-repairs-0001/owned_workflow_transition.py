"""Trusted private owned-currentness profile through the original public operation.

No request or serialized policy installs Python objects. A separately selected
bootstrap registers actual host providers; their exact origins are bound by a
private control and checked on every boundary. The strict handler stays intact.
"""
import copy
import importlib
import inspect
from pathlib import Path
import sys
import weakref
from jsonschema import Draft202012Validator,FormatChecker
from .protocol import ROOT,HERE,source,binding,compact
from .handlers import cut
from .auth import now,instant
from .workspace import validate_scope,read_private,privacy
from . import artifact_model as model
from . import guard as G
from . import session_source_freshness as SS
from . import owned_workflow_semantics as SEM

REGISTRY=weakref.WeakKeyDictionary()
KERNELS={
 'implementation/lab-runtime/local-host/t31-owned-produced-0001/owned_kernel.py',
 'implementation/lab-runtime/local-host/t31-scoped-output-0001/scoped_kernel.py'}
STORES={
 'implementation/lab-runtime/local-host/t31-durable-output-0001/output_store.py',
 'implementation/lab-runtime/local-host/t31-scoped-output-0001/scoped_store.py'}

def need(ok,reason):
    if not ok:raise ValueError(reason)
def closed(value,fields,reason):need(type(value) is dict and set(value)==set(fields),reason)
def exact_code(b,allowed=None):
    closed(b,('path','sha256'),'closed owned code binding required');p=Path(b['path'])
    need(not p.is_absolute() and p.as_posix()==b['path'] and '..' not in p.parts and '\\' not in b['path'] and '\0' not in b['path'],'closed repository code locator required')
    need(allowed is None or b['path'] in allowed,'unselected owned kernel/store profile')
    full=ROOT/p;need(not full.is_symlink() and not any(a.is_symlink() for a in full.parents)
                    and source.sha(full.read_bytes())==b['sha256'],'selected owned code bytes changed')
    return full
def material(policy,b):
    root,manifest=validate_scope(policy)
    rows=[r for r in manifest['materials'] if r['ref']==b['ref'] and r['sha256']==b['sha256']]
    need(len(rows)==1,'exact independently selected owned material unavailable')
    raw=read_private(root/rows[0]['path']);need(source.sha(raw)==b['sha256'],'owned private material changed');return raw
def source_bindings():
    manifest=G.verify(source.sha((HERE/'source-manifest.json').read_bytes()))
    roles={'adapter_binding':'family_reader_manifest_binding','source_binding':'family_source_manifest_binding','package_binding':'family_source_package_binding'}
    return {key:{'ref':manifest[role]['path'],'sha256':manifest[role]['sha256']} for key,role in roles.items()}
def validate_control(policy,schemas):
    need(policy['schema_version']=='lab-local-workflow-transition-policy/v1-candidate' and policy['source_name']==source.CURRENT_LEGACY_NAME,'explicit current-family owned metadata policy required')
    control=policy['workflow_control'];closed(control,('routing_binding','kernel_binding','journal_binding'),'closed actual workflow control required')
    need(policy['workflow_source_control']==source_bindings(),'independently selected current workflow source bindings differ')
    journal=binding(str((HERE/'workflow_output_journal.py').relative_to(ROOT)),(HERE/'workflow_output_journal.py').read_bytes())
    need(control['journal_binding']==journal,'original journal method differs')
    route=source.parse(material(policy,control['routing_binding']))
    closed(route,('schema_version','grant_binding','journal_root','journal_config_sha256','owned_profile_binding'),'closed owned workflow routing required')
    need(route['schema_version']=='lab-owned-workflow-routing/v2-current-owned-fixture','explicit owned runtime routing required')
    rel=Path(route['journal_root']);need(not rel.is_absolute() and '..' not in rel.parts and len(rel.parts)==2 and rel.parts[0]=='workflows' and rel.as_posix()==route['journal_root'],'closed owned journal root required')
    grant=source.parse(material(policy,route['grant_binding']));profile=source.parse(material(policy,route['owned_profile_binding']))
    closed(profile,('schema_version','scope_ref','source_cut','actor','kernel_binding','store_binding','callback_origins','material_bindings','scope_selection_binding','authority_effect'),'closed private owned runtime profile required')
    need(profile['schema_version']=='lab-private-owned-workflow-runtime/v1' and profile['authority_effect']=='none','owned profile grants no admission')
    exact_code(profile['kernel_binding'],KERNELS);exact_code(profile['store_binding'],STORES)
    scoped=profile['store_binding']['path'].endswith('/scoped_store.py')
    need(scoped==(profile['scope_selection_binding'] is not None),'explicit native scope selection required only for scoped store')
    if scoped:material(policy,profile['scope_selection_binding'])
    need(control['kernel_binding']=={'ref':profile['kernel_binding']['path'],'sha256':profile['kernel_binding']['sha256']},'private owned kernel differs from authenticated policy')
    need(profile['scope_ref']==grant['scope_ref']==policy['scope_refs'][0] and profile['source_cut']==grant['source_cut']
         and profile['actor']['principal_ref']==grant['principal_ref']==policy['principal_ref'] and grant['authority_effect']=='none'
         and grant['permitted_effects']==['candidate-workflow-transition'] and instant(grant['not_before'])<=now()<min(instant(grant['expires_at']),instant(policy['expires_at'])),
         'owned current grant, principal, period or scope differs')
    closed(profile['callback_origins'],('headers','semantics','outputs','guard'),'closed private host adapter selection required')
    for origin in profile['callback_origins'].values():
        closed(origin,('path','sha256','entrypoint'),'closed callback origin required');exact_code({'path':origin['path'],'sha256':origin['sha256']})
        need(type(origin['entrypoint']) is str and origin['entrypoint'] and '<lambda>' not in origin['entrypoint'],'named exact trusted host callback required')
    need(type(profile['material_bindings']) is list,'independent private coordination original selection required')
    keys=[]
    for row in profile['material_bindings']:
        closed(row,('artifact','original_binding'),'closed selected private record binding required')
        closed(row['artifact'],('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'),'closed selected private header required')
        raw=material(policy,row['original_binding']);need(source.sha(raw)==row['artifact']['byte_sha256'],'selected private coordination original differs')
        keys.append(compact(row['artifact']))
    need(len(keys)==len(set(keys)),'duplicate selected private coordination original')
    return route,grant,profile
def callable_origin(fn,expected):
    target=fn.__func__ if inspect.ismethod(fn) else fn
    need(inspect.isfunction(target),'actual selected host function required')
    path=exact_code({'path':expected['path'],'sha256':expected['sha256']})
    need(Path(target.__code__.co_filename).resolve()==path and target.__qualname__==expected['entrypoint'],'private callback origin/entrypoint differs')
    return (target.__code__,getattr(fn,'__self__',None))
def actor(channel):
    c=channel.context;return {**{k:c[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')},'role_assignment_refs':c['role_assignment_bindings']}
def method_identity(fn):
    target=fn.__func__ if inspect.ismethod(fn) else fn
    need(inspect.isfunction(target),'actual selected Python method required')
    path=Path(target.__code__.co_filename).resolve();need(path.is_relative_to(ROOT),'selected method code outside repository')
    return (target,getattr(fn,'__self__',None),target.__code__,str(path),source.sha(path.read_bytes()))
def same_method(actual,expected):
    return all(actual[i] is expected[i] for i in (0,1,2)) and actual[3:]==expected[3:]

class Selection:
    """One private host-installed capability; no public installation path exists."""
    def __init__(self,host,*,store,kernel,headers,semantics,outputs,guard):
        service=importlib.import_module(__package__+'.service');auth=importlib.import_module(__package__+'.auth')
        need(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,'actual selected Service/ReaderChannel required')
        policy=host.channel.policy_guard();route,grant,profile=validate_control(policy,host.schemas)
        root,_=validate_scope(policy)
        need(Path(kernel.__file__).resolve()==exact_code(profile['kernel_binding'],KERNELS),'actual owned kernel module origin differs')
        need(Path(inspect.getfile(type(store))).resolve()==exact_code(profile['store_binding'],STORES)
             and store.root==root/route['journal_root'] and store.journal.config_sha256==route['journal_config_sha256']
             and store.journal.config['principal_ref']==policy['principal_ref'] and store.journal.config['scope_ref']==profile['scope_ref'],
             'actual owned physical journal scope/config/type differs')
        need(actor(host.channel)==profile['actor'],'actual authenticated owned Actor differs')
        self.closed=False;self.host=host;self.channel=host.channel;self.vault=host.vault;self.store=store;self.kernel=kernel
        self.api_source_sha=source.sha((HERE/'source-manifest.json').read_bytes());G.verify(self.api_source_sha)
        self.policy=copy.deepcopy(policy);self.route=copy.deepcopy(route);self.profile=copy.deepcopy(profile);self.policy_sha=host.channel.expected_sha
        self.bound_kernel=kernel;self.bound_store=store;self.bound_journal=store.journal
        self.bound_carriers=store.carriers
        self.bound_scope=getattr(store,'scope',None)
        self.scope_selection=None
        self.scope_index_path=None
        if self.bound_scope is not None:
            self.scope_selection=self.bound_scope.selection
            self.scope_index_path=self.scope_selection.index_path
            b=profile['scope_selection_binding'];_,manifest=validate_scope(policy)
            rows=[r for r in manifest['materials'] if r['ref']==b['ref'] and r['sha256']==b['sha256']]
            need(len(rows)==1 and Path(self.scope_selection.index_path)==root/rows[0]['path']
                 and self.scope_selection.index_sha256==b['sha256'],'actual native scope index selection differs')
            self.bound_scope.guard()
        self.journal_config_raw=read_private(store.root/'config.json')
        need(source.sha(self.journal_config_raw)==route['journal_config_sha256'] and source.parse(self.journal_config_raw)==store.journal.config,
             'actual delegated journal config/original differs')
        self.kernel_plan=method_identity(kernel.plan)
        self.store_methods={name:method_identity(getattr(store,name)) for name in ('apply','replay','consume','recover')}
        self.carriers_output=method_identity(store.carriers.output)
        self.journal_methods={name:method_identity(getattr(store.journal,name)) for name in ('apply','replay','recover')}
        journal_path=Path(inspect.getfile(type(store.journal))).resolve()
        self.journal_origin=(str(journal_path),source.sha(journal_path.read_bytes()))
        need(self.journal_origin[1]==policy['workflow_control']['journal_binding']['sha256'],
             'actual delegated journal bytes differ from selected immutable method')
        self.callbacks={'headers':headers,'semantics':semantics,'outputs':outputs,'guard':guard}
        self.callback_refs={key:callable_origin(fn,profile['callback_origins'][key]) for key,fn in self.callbacks.items()}
        self.source=host.handlers.view.custody_signed_sources;self.source.guard()
        need(self.source.view is host.handlers.view and self.source.source_cut==profile['source_cut']==cut(host.handlers.view),'actual selected owned Source/cut differs')
        self.source_basis=copy.deepcopy(SS.captured_source_basis(self.source));self.family=copy.deepcopy(SS.fresh_selected_source(self.source))
        self.selected_stamp=source.sha(compact({'policy':self.policy,'route':self.route,'profile':self.profile}))
        self.guard()
    def _bindings_guard(self,deadline=None):
        need(not self.closed,'owned workflow host selection is closed')
        from .integrated_guard import require_outside
        require_outside();source.current_legacy_delivery().FACT_SCOPE.require_outside_scope()
        need(self.host.channel is self.channel and self.host.vault is self.vault and self.host.handlers.view is self.source.view,'actual owned host/channel/Vault/source identity changed')
        G.verify(self.api_source_sha);self.host.schemas.guard();self.vault.guard()
        self.channel.termination_guard();policy=self.channel.policy
        route,grant,profile=validate_control(policy,self.host.schemas)
        need(self.channel.expected_sha==self.policy_sha and source.sha(compact({'policy':policy,'route':route,'profile':profile}))==self.selected_stamp
             and actor(self.channel)==self.profile['actor'],'owned independent selection/Actor changed')
        root,_=validate_scope(policy)
        self._runtime_guard(root,route,policy,profile)
        need(self.source.source_cut==self.profile['source_cut'] and SS.captured_source_basis(self.source)==self.source_basis,'owned captured Source facts changed')
        SS.fresh_selected_source(self.source,self.family)
        need(set(self.callbacks)==set(self.callback_refs)==set(self.profile['callback_origins']),'actual host callback closure changed')
        for key,fn in self.callbacks.items():
            actual=callable_origin(fn,self.profile['callback_origins'][key]);expected=self.callback_refs[key]
            need(actual[0] is expected[0] and actual[1] is expected[1],'actual host callback object changed')
        end=min(instant(policy['expires_at']),instant(grant['expires_at']))
        need(now()<end and (deadline is None or now()<deadline),'owned effective caller/grant deadline ended')
        return grant
    def _runtime_guard(self,root,route,policy,profile):
        need(self.kernel is self.bound_kernel and self.store is self.bound_store and self.store.journal is self.bound_journal
             and self.store.carriers is self.bound_carriers
             and self.store.root==self.store.journal.root==root/route['journal_root']
             and self.store.journal.config_sha256==route['journal_config_sha256']
             and self.store.journal.config['principal_ref']==policy['principal_ref']
             and self.store.journal.config['scope_ref']==profile['scope_ref'],
             'actual selected owned kernel/store/journal routing changed')
        need(read_private(self.store.root/'config.json')==self.journal_config_raw and self.store.journal.config==source.parse(self.journal_config_raw),
             'captured or physical owned journal config changed')
        need(same_method(method_identity(self.kernel.plan),self.kernel_plan)
             and all(same_method(method_identity(getattr(self.store,name)),identity) for name,identity in self.store_methods.items())
             and same_method(method_identity(self.store.carriers.output),self.carriers_output)
             and all(same_method(method_identity(getattr(self.store.journal,name)),identity) for name,identity in self.journal_methods.items())
             and source.sha(Path(self.journal_origin[0]).read_bytes())==self.journal_origin[1],
             'actual selected owned plan/journal method changed')
        need(getattr(self.store,'scope',None) is self.bound_scope,'actual native scope object changed')
        if self.bound_scope is not None:
            need(self.bound_scope.selection is self.scope_selection and self.store.carriers.scope is self.bound_scope
                 and self.bound_scope.journal is self.bound_journal
                 and self.scope_selection.index_path==self.scope_index_path
                 and self.scope_selection.index_sha256==profile['scope_selection_binding']['sha256']
                 and read_private(Path(self.scope_selection.index_path))==material(policy,profile['scope_selection_binding']),
                 'actual native scope selection changed')
            self.bound_scope.guard()
    def guard(self,deadline=None):
        self._bindings_guard(deadline)
        self.callbacks['guard']()
        # A live guard may discover or cause a change. Do not commit through
        # altered routing, callables, policy, Source facts or an elapsed deadline.
        return self._bindings_guard(deadline)
    def close(self):
        self.closed=True;self.callbacks.clear();self.callback_refs.clear()
        self.host=None;self.channel=None;self.vault=None;self.source=None;self.source_basis=None;self.family=None
        self.bound_kernel=None;self.bound_store=None;self.bound_journal=None;self.bound_scope=None;self.bound_carriers=None;self.scope_selection=None

def install(host,**private_inputs):
    need(host not in REGISTRY,'owned workflow capability cannot be rebound');selected=Selection(host,**private_inputs);REGISTRY[host]=selected;return selected
def selected(host):return REGISTRY.get(host)
def uninstall(host):
    capability=REGISTRY.pop(host,None)
    if capability is not None:capability.close()

class OwnedWorkflowTransition:
    def __init__(self,selection,deadline):
        need(type(selection) is Selection and REGISTRY.get(selection.host) is selection and deadline is not None,'exact private owned selection/caller deadline required')
        self.selection=selection;self.host=selection.host;self.deadline=deadline;self.plan=None;self.originals=None
    def host_guard(self):return self.selection.guard(self.deadline)
    def preflight(self,message,outer,key):
        grant=self.host_guard();need(message['idempotency_key']==key and message['source_cut']==outer==cut(self.host.handlers.view),'owned exact message/key/current cut differs')
        self.selection.source.guard();self.host_guard()
        raw={name:self.host.vault.material(message[name]) for name in ('definition_binding','run_binding','authority_evaluation_binding','satisfaction_report_binding')}
        run=source.parse(raw['run_binding']);definition=source.parse(raw['definition_binding'])
        headers=self.selection.callbacks['headers'](copy.deepcopy(message),copy.deepcopy(run),copy.deepcopy(grant))
        facts=self.selection.callbacks['semantics'](copy.deepcopy(run),copy.deepcopy(definition),copy.deepcopy(grant))
        def read(row):
            closed(row,('artifact','original'),'exact original semantic record required');h=row['artifact'];body_raw=row['original']
            need(type(body_raw) is bytes and source.sha(body_raw)==h['byte_sha256'],'semantic original byte binding differs');resolved=headers.resolve(h)
            if hasattr(headers,'scope_permitted'):need(headers.scope_permitted(h,grant['scope_ref']),'original authority/container scope is not independently permitted')
            else:need(h['scope_ref']==grant['scope_ref'],'original header authority scope differs')
            if resolved['posture'] in ('admitted-current','local-admitted-current'):
                subject=self.host.handlers.view.subjects.get(h['version_ref'])
                need(subject is not None and subject['effective_state'] in ('admitted-current','local-admitted-current')
                     and model.artifact_ref(self.host.handlers.view,subject)==h and model.record_bytes(self.host.handlers.view,subject)[0]==body_raw,
                     'declared signed-source header is not an actual exact original')
            elif resolved['posture']=='owned-coordination-current':
                chosen=[v for v in self.selection.profile['material_bindings'] if v['artifact']==h]
                need(len(chosen)==1 and material(self.selection.policy,chosen[0]['original_binding'])==body_raw,
                     'private coordination record lacks independently selected original')
            else:need(resolved['posture']=='owned-produced-current','unknown owned header posture')
            body=source.parse(body_raw);privacy(body)
            contract=self.host.handlers.view.data['projection']['contracts'].get(h['carrier_ref']);need(contract is not None,'actual carrier contract absent')
            document=source.parse(source.original({'path':contract['schema_path'],'sha256':contract['schema_sha256']}))
            selector=contract.get('schema_selector')
            if selector:
                for part in selector.removeprefix('#').strip('/').split('/'):document=document[part.replace('~1','/').replace('~0','~')]
            Draft202012Validator(document,registry=self.host.schemas.registry,format_checker=FormatChecker()).validate(body)
            SEM.original_identity(body,h)
            need(body.get('authority_effect')=='none','semantic exact authority differs')
            if body.get('kind')=='typed-relation':
                signature,_=model.signature(self.host.handlers.view,body['payload']['relation_kind_ref']);payload=signature['payload'];edge=body['payload']
                need({'source_kind':edge['source']['kind'],'target_kind':edge['target']['kind']} in payload['allowed_endpoint_pairs'],'exact current typed endpoint pair undeclared')
                q=payload['qualifier_contract'];Draft202012Validator({'type':'object','properties':q['properties'],'required':q['required_axes'],'additionalProperties':False}).validate(edge['qualifiers'])
            return body
        closed(facts,('intent','resolution','work','coordination','goal','decision','effects','decision_edges','goal_edges','decision_profile','inputs'),'closed semantic and input original closure required')
        need(facts['decision_profile']['artifact']==definition['decision_profile']
             and definition['decision_profile']['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1', 'exact original WorkflowDecisionProfile required')
        read(facts['decision_profile'])
        need(headers.resolve(definition['decision_profile'])['posture'] in ('admitted-current','local-admitted-current'),'WorkflowDecisionProfile must remain signed-source-current')
        SEM.validate(run,definition,grant,{k:v for k,v in facts.items() if k not in ('inputs','decision_profile')},read)
        need(type(facts['inputs']) is list and len(facts['inputs'])==len(message['input_artifacts']),'complete exact input original records required')
        for h,row in zip(message['input_artifacts'],facts['inputs'],strict=True):
            need(row['artifact']==h,'selected input original order/header differs');read(row)
        for refs in grant['obligation_bindings'].values():
            for b in refs:self.host.vault.material(b)
        for b in message['action_receipt_bindings']:self.host.vault.material(b)
        self.plan=self.selection.kernel.plan(message,definition_raw=raw['definition_binding'],run_raw=raw['run_binding'],authority_raw=raw['authority_evaluation_binding'],
            satisfaction_raw=raw['satisfaction_report_binding'],host_grant=grant,authenticated_actor=actor(self.host.channel),current_cut=cut(self.host.handlers.view),
            selected_headers=headers,selected_obligations=copy.deepcopy(grant['obligation_bindings']),now=now())
        produced=self.selection.callbacks['outputs'](copy.deepcopy(message),copy.deepcopy(self.plan),copy.deepcopy(run),copy.deepcopy(grant))
        closed(produced,('artifacts','originals','producer_receipt_bindings'),'closed independently selected producer result required')
        for b in produced['producer_receipt_bindings']:self.host.vault.material(b)
        # The original attachment contract delegates each body to the selected
        # store's exact ordinary/scoped carrier validator. Native scopes remain
        # visible in original headers and bodies; no scope is retagged here.
        from .workflow_output_contracts import attach_outputs
        self.plan=attach_outputs(self.selection.kernel,self.plan,outputs=produced['artifacts'],raw_by_ref=produced['originals'],carriers=self.selection.store.carriers,
            scope_ref=grant['scope_ref'],work_ref=run['work']['version_ref'],transition_ref=message['transition_ref'])
        self.plan['producer_receipt_bindings']=copy.deepcopy(produced['producer_receipt_bindings']);self.originals=copy.deepcopy(produced['originals'])
        need(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:workflow-run:v1-candidate',self.plan['next_run']),'owned output-bearing next Run violates original protocol')
        self.selection.source.guard();self.host_guard();return self.plan
    def apply(self,message,request,outer,key):
        self.host_guard();need(self.plan is not None and self.plan['event']['idempotency_key']==key,'actual owned preflight absent')
        tx=self.selection.store.apply(self.plan,originals=self.originals,request_binding=request,host_guard=self.host_guard)
        self.host_guard();head,raw=self.selection.store.replay()
        need(source.parse(raw)==self.plan['next_run'] and tx['event']==self.plan['event'] and head['run_sha256']==tx['next_run_sha256'],'actual owned commit/replay differs')
        evidence=self.host.vault.object(compact(tx));self.host_guard();event=self.host.vault.object(compact(tx['event']));self.host_guard()
        result={'schema_version':'lab-workflow-transition-receipt/v1-candidate','request_binding':request,'run_ref':tx['event']['run_ref'],
            'from_state':tx['event']['from_state'],'to_state':tx['event']['to_state'],'posture':'applied','event_binding':event,
            'output_artifact_refs':copy.deepcopy(tx['event']['output_artifact_refs']),'evidence_bindings':[evidence],'gaps':[],'recovery_required':False,
            'authority_effect':'none','claim_ceiling':'Owned candidate coordination over exact original producers and current private host grant. No Source admission, actual owner outcome, live Session recreation or Work satisfaction.'}
        need(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:workflow-transition-receipt:v1-candidate',result),'actual owned receipt violates original protocol')
        self.host_guard();return result,[evidence,event]
def select(host,message,outer,key,deadline):
    capability=selected(host)
    if capability is None:return None
    builder=OwnedWorkflowTransition(capability,deadline);builder.preflight(message,outer,key);return builder
