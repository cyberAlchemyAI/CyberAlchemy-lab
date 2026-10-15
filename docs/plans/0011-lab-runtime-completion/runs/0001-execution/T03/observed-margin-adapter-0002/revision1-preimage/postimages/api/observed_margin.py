"""Selected private fresh-claim margin; no deadline or permission renewal.

This is a separately selected production candidate, not current runtime code.
Its private binding comes only from the captured startup composition. Historical
prior/result paths never call it. Assessment custody is held separately from the
original Service fields so old recorded outcomes do not need an old live Session.
"""
import hashlib,sys,types
from dataclasses import dataclass
from pathlib import Path
from . import margin_capture as C
from . import margin_kernel as K

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
MODULES=('service','workspace','auth','protocol','guard','session_attachment','current_context_sessions','handlers')
CONFIG_FIELDS=set('schema_version authority_effect mode api_directory api_source_binding profile_binding software_binding period_binding dependency_selection_binding dependency_installation instrumentation_binding policy_binding load_binding'.split())
MODES=('diagnostic-measurement','enforce-observed-margin')
class MarginBeforeClaim(ValueError):
    def __init__(self,code):
        self.code=code;super().__init__('Selected observed margin refused before claim')
def need(value,code='integrity-failed'):
    if not value:raise MarginBeforeClaim(code)
def closed(value,fields,code='integrity-failed'):need(type(value) is dict and set(value)==set(fields),code)
def codes(code):
    yield code
    for item in code.co_consts:
        if isinstance(item,types.CodeType):yield from codes(item)
def code_signature(code):
    # Compare immutable compiled values rather than marshal serialization flags.
    # This reads code constants only, never function globals, args or frames.
    def constant(value):
        if isinstance(value,types.CodeType):return ('code',code_signature(value))
        if type(value) in (str,bytes,int,float,complex,bool,type(None)):return (type(value).__name__,value)
        if value is Ellipsis:return ('ellipsis',)
        if type(value) is tuple:return ('tuple',tuple(constant(v) for v in value))
        if type(value) is frozenset:return ('frozenset',tuple(sorted((constant(v) for v in value),key=repr)))
        raise MarginBeforeClaim('integrity-failed')
    return tuple(getattr(code,name) for name in ('co_argcount','co_posonlyargcount','co_kwonlyargcount','co_nlocals','co_stacksize','co_flags','co_code','co_names','co_varnames','co_freevars','co_cellvars','co_filename','co_name','co_qualname','co_firstlineno','co_linetable','co_exceptiontable'))+(tuple(constant(v) for v in code.co_consts),)
def code_check(function,raw,path):
    expected=[code for code in codes(compile(raw,str(path),'exec')) if code.co_qualname==function.__qualname__]
    need(len(expected)==1 and Path(function.__code__.co_filename)==path
         and code_signature(function.__code__)==code_signature(expected[0]))
def private(root,identity,binding):
    closed(binding,('path','sha256'));name=C.relative(binding['path']);need('/' not in name)
    return C.capture(Path(root)/name,binding['sha256'],control_root=root,root_identity=identity,max_bytes=1024*1024)
def config_check(value):
    closed(value,CONFIG_FIELDS,'closure-missing')
    need(value['schema_version']=='lab-protected-observed-margin-runtime/v1-candidate'
         and value['authority_effect']=='none' and value['mode'] in MODES,'closure-missing')
    C.relative(value['api_directory']);C.relative(value['dependency_installation'])
    for key in ('api_source_binding','profile_binding','software_binding','period_binding','dependency_selection_binding','instrumentation_binding'):
        closed(value[key],('path','sha256'));C.relative(value[key]['path'])
    if value['mode']=='enforce-observed-margin':
        for key in ('policy_binding','load_binding'):closed(value[key],('path','sha256'),'closure-missing')
    else:need(value['policy_binding'] is None and value['load_binding'] is None,'closure-missing')
    return value

def software(config,module_rows):
    api=ROOT/C.relative(config['api_directory']);selection=C.parse(C.capture_binding(ROOT,config['software_binding']))
    need(type(selection) is dict and selection.get('authority_effect')=='none' and type(selection.get('files')) is list)
    selected={};captured={}
    for row in selection['files']:
        need(type(row) is dict and {'path','sha256'}<=set(row));path=C.relative(row['path']);need(path not in selected)
        need(path!=config['software_binding']['path']) # no manifest self-digest cycle
        selected[path]=row['sha256'];captured[path]=C.capture(ROOT/path,row['sha256'])
    need(set(module_rows)==set(MODULES))
    package=module_rows['service'].__package__
    for name,module in module_rows.items():
        path=api/(name+'.py');need(module.__file__==str(path) and sys.modules.get(package+'.'+name) is module)
        relative=str(path.relative_to(ROOT));need(relative in captured)
    # Physical source bytes AND current callable code, including same-object
    # __code__ changes. No existing callback is replaced by this adapter.
    callbacks={'service':(module_rows['service'].Service.__init__,module_rows['service'].Service._call,module_rows['service'].Service.close),
               'workspace':(module_rows['workspace'].Vault.claim,module_rows['workspace'].Vault.guard,module_rows['workspace'].Vault.lock.__wrapped__),
               'auth':(module_rows['auth'].now,module_rows['auth'].ReaderChannel.guard,module_rows['auth'].ReaderChannel.policy_guard,module_rows['auth'].ReaderChannel.termination_guard),
               'protocol':(module_rows['protocol'].compact,module_rows['protocol'].frame_parse,module_rows['protocol'].Schemas.guard,module_rows['protocol'].Schemas.valid),
               'guard':(module_rows['guard'].verify,module_rows['guard']._capture_exact,module_rows['guard']._verify_files),
               'session_attachment':(module_rows['session_attachment'].SessionAttachment.__init__,module_rows['session_attachment'].SessionAttachment.guard),
               'current_context_sessions':(module_rows['current_context_sessions'].LiveReader.guard,module_rows['current_context_sessions'].PermissionBridge.guard,module_rows['current_context_sessions'].ContextSessions.delivery)}
    for name,functions in callbacks.items():
        path=api/(name+'.py');raw=captured[str(path.relative_to(ROOT))]
        for function in functions:code_check(function,raw,path)
    for leaf in ('observed_margin.py','margin_capture.py','margin_kernel.py','observed-margin-policy.schema.json'):
        need(str((api/leaf).relative_to(ROOT)) in captured)
    need(config['api_source_binding']['path']==str((api/'source-manifest.json').relative_to(ROOT)))
    # Preserve the full selected original source/environment verifier.
    manifest=module_rows['guard'].verify(config['api_source_binding']['sha256'])
    source_rows={(r['path'],r['sha256']) for r in manifest['files']}
    for path,pin in selected.items():need((path,pin) in source_rows)
    C.capture_binding(ROOT,config['api_source_binding']);profile=C.parse(C.capture_binding(ROOT,config['profile_binding']))
    return captured

def dependency(config):
    value=C.parse(C.capture_binding(ROOT,config['dependency_selection_binding']))
    need(value.get('schema_version')=='lab-runtime-dependency-closure/v2-candidate')
    rows={r['destination']:{**r,'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
    rows.update(value['wheel_members']);rows['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    installation=ROOT/C.relative(config['dependency_installation']);need(Path(sys.executable)==installation/'bin/python')
    for name,row in rows.items():
        path=installation/C.relative(name);raw=C.capture(path,row['sha256']);st=path.lstat()
        need(len(raw)==row['size_bytes'] and st.st_mode&0o777==row['mode'])
    C.membership(installation,rows)
    return config['dependency_selection_binding']['sha256']

def instrumentation(binding):
    specification=C.parse(C.capture_binding(ROOT,binding));closed(specification,('schema_version','profile_hook','trace_hook','monitoring_tools','authority_effect'))
    need(specification['schema_version']=='lab-margin-instrumentation-observation/v1-candidate' and specification['authority_effect']=='none')
    def hook(value):return None if value is None else {'module':type(value).__module__,'qualname':type(value).__qualname__}
    actual={'profile_hook':hook(sys.getprofile()),'trace_hook':hook(sys.gettrace()),
            'monitoring_tools':{str(n):sys.monitoring.get_tool(n) for n in range(6)}}
    need(all(actual[k]==specification[k] for k in actual))
    return binding['sha256']

@dataclass(frozen=True,slots=True)
class RuntimeBinding:
    host:object
    parent:object
    attachment:object
    modules:object
    root:Path
    root_identity:tuple
    selection_binding:object
    selection_raw:bytes
    before_claim_code:tuple
    def check_entry(self,function):
        need(function is before_claim and code_signature(function.__code__)==self.before_claim_code
             and Path(function.__code__.co_filename)==Path(__file__))
    def selection(self):
        raw=private(self.root,self.root_identity,dict(self.selection_binding));need(raw==self.selection_raw)
        return config_check(C.parse(raw))
    def close(self):
        # Original attachment close releases its references, never the parent
        # RAM/Session/reader permission. Original Service fields stay untouched.
        if self.host.session_attachment is not self.attachment:self.attachment.close()


def bind_runtime(host,parent,modules,control_root,root_identity,selection_binding,expected_attachment):
    """Private captured startup only. Not reachable from an API message/Actor.

    modules must be actual objects returned by Root's independently closed full
    API capture, with its future shared source/profile. No existing module is
    monkeypatched or aliased to this new software origin.
    """
    raw=private(control_root,root_identity,selection_binding);config=config_check(C.parse(raw));captured=software(config,modules)
    S=modules['service'];W=modules['workspace'];A=modules['auth'];SA=modules['session_attachment']
    need(type(host) is type(parent) is S.Service and host is not parent and type(host.vault) is W.Vault
         and host.vault.observed_margin_host is host and host.vault.observed_margin_runtime is None)
    need(type(host.channel) is type(parent.channel) is A.ReaderChannel and host.channel is not parent.channel)
    need(host.channel.policy['schema_version'] in ('lab-local-lesson-application-policy/v2-candidate','lab-local-lesson-assessment-policy/v1-candidate'))
    if host.channel.policy['schema_version']=='lab-local-lesson-application-policy/v2-candidate':
        attachment=host.session_attachment;need(type(attachment) is SA.SessionAttachment and attachment.parent is parent and attachment.expected==expected_attachment)
    else:
        # This is the existing verifier's actual constructor, not a counterfeit
        # parent field. Deliberately do not assign Service.session_attachment or
        # Service.sessions: recorded assessment recovery remains independent.
        need(host.session_attachment is None and host.sessions is None)
        attachment=SA.SessionAttachment(host,parent,expected_attachment)
    attachment.guard()
    path=ROOT/config['api_directory']/'observed_margin.py'
    module_raw=captured[str(path.relative_to(ROOT))]
    independent_code=next(code for code in codes(compile(module_raw,str(path),'exec')) if code.co_qualname=='before_claim')
    need(Path(__file__)==path and code_signature(before_claim.__code__)==code_signature(independent_code))
    binding=RuntimeBinding(host,parent,attachment,types.MappingProxyType(dict(modules)),Path(control_root),root_identity,types.MappingProxyType(dict(selection_binding)),raw,code_signature(independent_code))
    host.vault.observed_margin_runtime=binding
    return binding

def observed(binding,call,context,deadline,config):
    modules=binding.modules;host=binding.host;parent=binding.parent;attachment=binding.attachment
    need(type(host) is type(parent) is modules['service'].Service and type(host.vault) is modules['workspace'].Vault
         and host.vault.observed_margin_host is host and host.vault.observed_margin_runtime is binding)
    need(type(attachment) is modules['session_attachment'].SessionAttachment and attachment.host is host and attachment.parent is parent)
    host.schemas.guard();parent.schemas.guard();host.vault.guard();parent.vault.guard()
    current=host.channel.guard();parent_context=parent.channel.guard();need(current==context)
    need(host.schemas is parent.schemas and host.schemas.profile_binding==config['profile_binding'])
    row=attachment.guard();resource=attachment.resource;sessions=parent.sessions
    need(sessions is attachment.sessions and sessions.live.get(row['session_ref']) is resource
         and type(sessions) is modules['current_context_sessions'].ContextSessions and type(resource) is modules['current_context_sessions'].LiveReader)
    resource.guard();selected=sessions.source;selected.guard()
    need(selected is resource.source and call['expected_source_cut']==row['source_cut']==selected.source_cut)
    if call['operation']=='lesson.apply':need(call['message']['session_ref']==row['session_ref'])
    else:
        # Original assessment preflight proves this exact application's completed
        # journal witness. Independently reread it here and bind its Session to
        # the actual protected parent, without changing native preparation.
        from .lesson_assessment import LessonAssessment
        control=host.channel.policy_guard()['assessment_control'];builder=LessonAssessment(host,control['routing_binding'],config['api_source_binding'])
        builder.preflight(call['message'],call['expected_source_cut'],call['idempotency_key'])
        application=builder.completed_candidate_application(call['message']['application'])
        need(application['payload']['session_ref']==row['session_ref'])
    period=C.parse(C.capture_binding(ROOT,config['period_binding']))
    need(parent.channel.policy['session_control']['period_binding']==config['period_binding'])
    proof=sessions.delivery(resource.delivery['verified_original_binding'])
    need(proof['verified_original_binding']==resource.delivery['verified_original_binding'] and proof['source_cut']==selected.source_cut)
    need(deadline is not None and deadline.tzinfo is not None)
    bounds={'effective_call':deadline.isoformat(),'Session':resource.expires.isoformat(),'Context_delivery':proof['expires_at'],
            'Source_period':period['expires_at'],'parent_reader':parent.channel.policy['expires_at'],'operator_reader':host.channel.policy['expires_at']}
    # Retain final original channel/resource guards. No lock is reacquired and
    # no derived material/journal is written by these observations.
    attachment.guard();resource.guard();parent.channel.guard();host.channel.guard()
    return bounds,selected.source_cut

def load_check(load,identity,at=None):
    closed(load,('schema_version','authority_effect','status','observed_at','valid_until','load_specification_binding','instrumentation_identity_sha256'),'closure-missing')
    need(load['schema_version']=='lab-margin-current-load/v1-candidate' and load['authority_effect']=='none'
         and load['status']=='qualified-current-load','closure-missing')
    closed(load['load_specification_binding'],('path','sha256'))
    C.capture_binding(ROOT,load['load_specification_binding'])
    need(load['load_specification_binding']['sha256']==identity['load_identity_sha256']
         and load['instrumentation_identity_sha256']==identity['instrumentation_identity_sha256'])
    if at is not None:need(K.instant(load['observed_at'])<=K.instant(at)<K.instant(load['valid_until']),'closure-missing')
    return True

def before_claim(vault,call,context,deadline):
    """Called only under the original exclusive claim lock after prior lookup."""
    if call['operation'] not in K.CHECKPOINTS:return None
    binding=getattr(vault,'observed_margin_runtime',None)
    need(type(binding) is RuntimeBinding and binding.host.vault is vault,'closure-missing')
    try:
        config=binding.selection();captured=software(config,binding.modules)
        dep=dependency(config);instrument=instrumentation(config['instrumentation_binding'])
        bounds,cut=observed(binding,call,context,deadline,config)
        if config['mode']=='diagnostic-measurement':
            need(binding.selection()==config)
            bounds,cut=observed(binding,call,context,deadline,config)
            at=binding.modules['auth'].now().isoformat();need(K.instant(at)<min(K.instant(v) for v in bounds.values()),'deadline-exceeded')
            return {'mode':'diagnostic-measurement','margin_enforced':False,'empirical_margin_qualified':False,
                    'direct_deadlines':bounds,'observed_at':at,'authority_effect':'none'}
        policy_raw=private(binding.root,binding.root_identity,config['policy_binding']);policy=C.parse(policy_raw)
        load_raw=private(binding.root,binding.root_identity,config['load_binding']);load=C.parse(load_raw)
        from jsonschema import Draft202012Validator
        schema=C.parse(captured[str((ROOT/config['api_directory']/'observed-margin-policy.schema.json').relative_to(ROOT))])
        need(Draft202012Validator(schema).is_valid(policy),'closure-missing')
        identity={'source_sha256':config['api_source_binding']['sha256'],'profile_sha256':config['profile_binding']['sha256'],
                  'code_closure_sha256':config['software_binding']['sha256'],'dependency_selection_sha256':dep,
                  'load_identity_sha256':load['load_specification_binding']['sha256'],'instrumentation_identity_sha256':instrument,
                  'source_cut_sha256':C.sha(binding.modules['protocol'].compact(cut))}
        for row in policy['evidence_bindings']:
            need(C.relative(row['path']).startswith('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/'),'closure-missing')
            C.capture_binding(ROOT,row)
        # Check code/source again after external empirical evidence. Its cost is
        # part of gate overhead and must be calibrated for this exact revision.
        load_check(load,identity) # selected load material is read before final UTC
        software(config,binding.modules);need(instrumentation(config['instrumentation_binding'])==instrument)
        need(binding.selection()==config)
        need(private(binding.root,binding.root_identity,config['policy_binding'])==policy_raw
             and private(binding.root,binding.root_identity,config['load_binding'])==load_raw)
        bounds,cut=observed(binding,call,context,deadline,config)
        need(identity['source_cut_sha256']==C.sha(binding.modules['protocol'].compact(cut)))
        # No filesystem reads or guards follow this real UTC observation.
        at=binding.modules['auth'].now().isoformat()
        need(K.instant(load['observed_at'])<=K.instant(at)<K.instant(load['valid_until']),'closure-missing');current=True
        result=K.decide(policy,identity,bounds,at,K.CHECKPOINTS[call['operation']],load_current=current)
        return {**result,'mode':'enforce-observed-margin','margin_enforced':True,'empirical_margin_qualified':True}
    except MarginBeforeClaim:raise
    except K.MarginRefusal as error:
        if error.reason=='real-lease-cannot-fit-observed-tail':raise MarginBeforeClaim('budget-exceeded') from None
        if error.reason=='empirical-execution-identity-differs':raise MarginBeforeClaim('integrity-failed') from None
        raise MarginBeforeClaim('closure-missing') from None
    except Exception:raise MarginBeforeClaim('integrity-failed') from None
