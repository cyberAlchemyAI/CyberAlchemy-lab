"""Pure algorithm/postimage contract controls; no Lab runtime constructors."""
import ast,copy,hashlib,json,os,stat,sys,tempfile,types,uuid
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).resolve().parent;API=HERE/'postimages/api'
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004';sys.path.append(str(I/'deps'))
name='_margin_contract_'+uuid.uuid4().hex;package=types.ModuleType(name);package.__path__=[];sys.modules[name]=package;loaded={};cases=[]
selection=json.loads((HERE/'control-source-selection.json').read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify():
 for row in selection['files']:
  p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256'] and p.stat().st_size==row['size_bytes']
verify()
for leaf in ['margin_capture','margin_kernel','margin_seal','observed_margin']:
 path=API/(leaf+'.py');m=types.ModuleType(name+'.'+leaf);m.__file__=str(path);m.__package__=name;sys.modules[m.__name__]=m
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);loaded[leaf]=m
C=loaded['margin_capture'];K=loaded['margin_kernel'];M=loaded['observed_margin']
def yes(label):cases.append({'case':label,'result':'PASS-pure-contract-only'})
def refused(label,callback,kind=Exception,code=None):
 try:callback()
 except kind as error:
  if code is not None:assert getattr(error,'code',getattr(error,'reason',None))==code,(label,type(error).__name__)
 else:raise AssertionError(label+' accepted')
 yes(label)
# Exact staged claim body exercised inside an explicitly owned inert test class;
# original callbacks/modules are never instantiated, substituted, or modified.
oldroot=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
oldtree=ast.parse((oldroot/'workspace.py').read_bytes());newtree=ast.parse((API/'workspace.py').read_bytes())
oldclaim=next(n for n in ast.walk(oldtree) if isinstance(n,ast.FunctionDef) and n.name=='claim')
claim=next(n for n in ast.walk(newtree) if isinstance(n,ast.FunctionDef) and n.name=='claim')
assert ast.dump(oldclaim.args,include_attributes=False)==ast.dump(claim.args,include_attributes=False);yes('original claim signature unchanged')
reduced=copy.deepcopy(claim);block=next(n for n in reduced.body if isinstance(n,ast.With)).body;gate=[n for n in block if isinstance(n,ast.If) and ast.unparse(n.test)=="call['operation'] in ('lesson.apply', 'lesson.assess')"]
assert len(gate)==1;block.remove(gate[0]);assert ast.dump(reduced,include_attributes=False)==ast.dump(oldclaim,include_attributes=False);yes('only explicit pre-object gate changes original claim body')
ownedclass=ast.ClassDef(name='OwnedClaimContract',bases=[],keywords=[],body=[copy.deepcopy(claim)],decorator_list=[],type_params=[]);module=ast.fix_missing_locations(ast.Module(body=[ownedclass],type_ignores=[]))
atomicrows=[];source=types.SimpleNamespace(require=lambda v,r:None if v else (_ for _ in ()).throw(ValueError('inert requirement')),sha=sha,encoded=lambda v:(json.dumps(v,sort_keys=True)+'\n').encode())
ns={'__name__':name+'.claim_contract','__package__':name,'jcs':types.SimpleNamespace(namespace=lambda op,key,context:'inert-namespace',fingerprint=lambda call,context:'inert-fingerprint'),'source':source,'atomic':lambda path,raw:atomicrows.append((str(path),sha(raw)))}
exec(compile(module,str(API/'workspace.py'),'exec'),ns);Class=ns['OwnedClaimContract']
class Lock:
 def __enter__(self):self.active=True;return self
 def __exit__(self,*args):self.active=False
with tempfile.TemporaryDirectory(prefix='cal-T03-margin-contract-') as directory:
 root=Path(directory);root.chmod(0o700);(root/'journal').mkdir();effects=[];lock=Lock();obj=Class()
 obj.root=root;obj.channel=types.SimpleNamespace(policy={'workspace':{'max_actions':10}});obj.lock=lambda:lock
 obj.state=lambda namespace:(None,None);obj.object=lambda raw:effects.append(sha(raw)) or {'ref':'inert-body','sha256':sha(raw)}
 context={'principal_ref':'inert-principal','connection_ref':'inert-connection'};call={'operation':'lesson.apply','idempotency_key':'inert-key','call_id':'inert-call'}
 for operation in ['lesson.apply','lesson.assess']:
  refused('unknown private runtime before object/allocation: '+operation,lambda operation=operation:obj.claim({**call,'operation':operation},b'{}',context),M.MarginBeforeClaim,'closure-missing')
  assert not effects and not atomicrows and lock.active is False
 prior={'principal_ref':'inert-principal','namespace':'inert-namespace'};result={'posture':'completed'};obj.state=lambda namespace:(prior,result)
 out=obj.claim(call,b'{}',context);assert out==( 'inert-namespace','inert-fingerprint',prior,result,False) and not effects;yes('recorded exact retry returns before unavailable calibration and live parent')
 obj.state=lambda namespace:(prior,None);out=obj.claim(call,b'{}',context);assert out[3] is None and out[4] is False and not effects;yes('pending recovery remains prior without redispatch or timing gate')
 obj.state=lambda namespace:(None,None);out=obj.claim({**call,'operation':'change.prepare'},b'{}',context)
 assert out[4] is True and len(effects)==1 and len(atomicrows)==2;yes('unrelated original fresh operations retain original material/allocation sequence')
 # Real fresh FD captures of newly owned inert control bytes only.
 leaf=root/'policy.json';leaf.write_bytes(b'{"inert":true}\n');leaf.chmod(0o600);s=root.stat();ident=(s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode));pin=sha(leaf.read_bytes())
 assert C.capture(leaf,pin,control_root=root,root_identity=ident)==leaf.read_bytes();yes('actual anchored private root and exact inert leaf capture')
 refused('software capture never accepts null independent digest',lambda:C.capture(leaf,None),ValueError)
 refused('private root identity mismatch',lambda:C.capture(leaf,pin,control_root=root,root_identity=(ident[0],ident[1]+1,ident[2],ident[3])),ValueError)
 leaf.chmod(0o644);refused('private leaf custody mode mismatch',lambda:C.capture(leaf,pin,control_root=root,root_identity=ident),ValueError);leaf.chmod(0o600)
 other=root/'other.json';other.write_bytes(b'{"inert":false}\n');other.chmod(0o600);leaf.unlink();leaf.symlink_to(other)
 refused('private selected leaf symlink refused',lambda:C.capture(leaf,pin,control_root=root,root_identity=ident),OSError)
 for raw in [b'{"x":1,"x":2}',b'{"x":NaN}']:refused('strict control JSON duplicate/nonfinite',lambda raw=raw:C.parse(raw),ValueError)
# Late same-byte physical replacement after the actual owned capture read,
# before leaf/ancestor exit checks. Only new inert fixture bytes are involved.
with tempfile.TemporaryDirectory(prefix='cal-T03-margin-contract-') as directory:
 root=Path(directory);root.chmod(0o700);leaf=root/'late.json';raw=b'{"inert":true}\n';leaf.write_bytes(raw);leaf.chmod(0o600)
 st=root.stat();ident=(st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode));fdcount=len(os.listdir('/proc/self/fd'))
 line=next(n for n,text in enumerate((API/'margin_capture.py').read_text().splitlines(),1) if "raw=b''.join(pieces)" in text)
 fired=[];tool=4
 def observe(code,number):
  if code is C.capture.__code__ and number==line and not fired:
   fired.append(True);os.rename(leaf,root/'retained.json');leaf.write_bytes(raw);leaf.chmod(0o600)
 sys.monitoring.use_tool_id(tool,'margin-own-inert-capture-exit-probe')
 try:
  sys.monitoring.register_callback(tool,sys.monitoring.events.LINE,observe);sys.monitoring.set_local_events(tool,C.capture.__code__,sys.monitoring.events.LINE)
  refused('actual late same-byte leaf replacement caught at capture exit',lambda:C.capture(leaf,sha(raw),control_root=root,root_identity=ident),ValueError)
 finally:
  sys.monitoring.set_local_events(tool,C.capture.__code__,0);sys.monitoring.register_callback(tool,sys.monitoring.events.LINE,None);sys.monitoring.free_tool_id(tool)
 assert fired and len(os.listdir('/proc/self/fd'))==fdcount;yes('actual capture exception releases all owned descriptors')
with tempfile.TemporaryDirectory(prefix='cal-T03-margin-contract-') as directory:
 root=Path(directory);root.chmod(0o700);(root/'deps').mkdir();leaf=root/'deps/member.py';leaf.write_bytes(b'# inert owned fixture\n');leaf.chmod(0o600)
 assert C.membership(root,{'deps/member.py'})==1;yes('actual descriptor installed membership observation')
 (root/'foreign.py').write_bytes(b'# inert unselected fixture\n');refused('extra installed member refused before unknown body read',lambda:C.membership(root,{'deps/member.py'}),ValueError)
# Same-object __code__ substitution on a NEW inert fixture is detected from
# independently compiled source bytes, not original loader/callback mutation.
fixture=HERE/'owned-code-fixture.py';raw=fixture.read_bytes();local={};exec(compile(raw,str(fixture),'exec'),local);fn=local['calculate'];M.code_check(fn,raw,fixture);yes('current function code equals selected source compile')
fn.__code__=local['different'].__code__;refused('same-object function code substitution detected',lambda:M.code_check(fn,raw,fixture),M.MarginBeforeClaim,'integrity-failed')
# Kernel phases here are explicitly synthetic contract inputs, never timing evidence.
policy=json.loads((HERE/'UNQUALIFIED-POLICY-TEMPLATE.json').read_bytes());qualified={**policy,'status':'empirically-qualified','execution_identity':{k:'1'*64 for k in K.IDENTITY_FIELDS},'evidence_bindings':[{'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/inert-contract.json','sha256':'2'*64}],'sample_count':1,'phase_upper_bounds_us':{k:1 for k in K.REMAINING['application-preclaim']},'uncertainty_reserve_us':1,'gate_overhead_upper_bound_us':1,'valid_until':'2031-01-01T00:00:00Z'}
now=datetime(2030,1,1,tzinfo=timezone.utc);deadlines={k:(now+timedelta(microseconds=12)).isoformat() for k in K.DEADLINE_FIELDS}
def decide(p=qualified,identity=None,bounds=deadlines,load=True,checkpoint='application-preclaim'):
 return K.decide(p,p['execution_identity'] if identity is None else identity,bounds,now.isoformat(),checkpoint,load_current=load)
assert decide()['remaining_margin_us']==1;yes('synthetic full nine-phase tail plus overhead and uncertainty')
refused('unqualified empirical template always refuses',lambda:decide(p=policy),K.MarginRefusal,'empirical-policy-unqualified')
refused('synthetic exact remaining-tail equality refuses',lambda:decide(bounds={k:(now+timedelta(microseconds=11)).isoformat() for k in deadlines}),K.MarginRefusal,'real-lease-cannot-fit-observed-tail')
for key in K.DEADLINE_FIELDS:refused('each actual bound participates: '+key,lambda key=key:decide(bounds={**deadlines,key:now.isoformat()}),K.MarginRefusal,'real-lease-cannot-fit-observed-tail')
refused('code/profile/source/cut calibration identity mismatch refuses',lambda:decide(identity={**qualified['execution_identity'],'code_closure_sha256':'3'*64}),K.MarginRefusal,'empirical-execution-identity-differs')
refused('unknown actual load refuses',lambda:decide(load=False),K.MarginRefusal,'actual-load-unknown-or-outside-calibration')
refused('missing remaining phase refuses',lambda:decide(p={**qualified,'phase_upper_bounds_us':{}}),K.MarginRefusal,'empirical-phase-bound-unknown')
refused('impossible calendar despite absent optional format checker refuses',lambda:decide(p={**qualified,'valid_until':'2031-02-30T00:00:00Z'}),K.MarginRefusal,'invalid-real-deadline')
assert decide(checkpoint='assessment-preclaim')['required_observed_tail_us']==7;yes('assessment full remaining tail excludes completed application prefix')
# No actual host/class/profile/privacy access is needed to refuse no binding.
refused('adapter unknown binding before any domain payload access',lambda:M.before_claim(types.SimpleNamespace(),{'operation':'lesson.apply'},None,None),M.MarginBeforeClaim,'closure-missing')
for mode in ['diagnostic-measurement','enforce-observed-margin']:
 cfg={k:None for k in M.CONFIG_FIELDS};cfg.update(schema_version='lab-protected-observed-margin-runtime/v1-candidate',authority_effect='none',mode=mode,api_directory='inert/api',dependency_installation='inert/installation')
 for key in ('api_source_binding','profile_binding','software_binding','period_binding','dependency_selection_binding','instrumentation_binding'):cfg[key]={'path':'inert.json','sha256':'1'*64}
 if mode=='enforce-observed-margin':
  refused('enforce has no implicit diagnostic fallback',lambda:M.config_check(cfg),M.MarginBeforeClaim,'closure-missing');cfg.update(policy_binding={'path':'policy.json','sha256':'1'*64},load_binding={'path':'load.json','sha256':'2'*64})
 M.config_check(cfg);yes('explicit protected '+mode+' mode shape')
 refused('API-like extra runtime mode field refused',lambda:M.config_check({**cfg,'actor':{}}),M.MarginBeforeClaim,'closure-missing')
# Complete postimages have no syntax errors; constructor/claim signatures preserved.
for p in API.glob('*.py'):ast.parse(p.read_bytes())
old=ast.parse((oldroot/'service.py').read_bytes());new=ast.parse((API/'service.py').read_bytes())
for method in ['__init__','_call','close']:
 a=next(n for n in ast.walk(old) if isinstance(n,ast.FunctionDef) and n.name==method);b=next(n for n in ast.walk(new) if isinstance(n,ast.FunctionDef) and n.name==method)
 assert ast.dump(a.args,include_attributes=False)==ast.dump(b.args,include_attributes=False);yes('original Service '+method+' signature unchanged')
 if method=='close':assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False);yes('original Service close callback AST unchanged')
for lane in ['positive','security']:
 p=HERE/'postimages'/ (lane+'_lifecycle.py');text=p.read_text();assert "assessor=M['service'].Service(view,ac,parent.schemas)" in text and "assessment_margin=MARGIN_COMPOSITION" in text
 assert 'lesson.apply' in text and 'lesson.assess' in text and 'operation.inspect' in text and 'application.close()' in text;yes('complete '+lane+' lifecycle retained with explicit private margin composition')
from jsonschema import Draft202012Validator
schema=json.loads((HERE/'protected-runtime-selection.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema);assert not validator.is_valid(json.loads((HERE/'UNRESOLVED-RUNTIME-SELECTION.json').read_bytes()));yes('unresolved real runtime selection cannot claim runnable enforcement')
# Existing operation catalog actually declares every new preclaim code.
catalogpath=ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json';catalog=json.loads(catalogpath.read_bytes())
for operation in ['lesson.apply','lesson.assess']:
 rows=[r for r in catalog['operations'] if r.get('operation_id',r.get('operation',r.get('name')))==operation]
 assert len(rows)==1,(operation,'catalog identity');assert {'closure-missing','integrity-failed','budget-exceeded','deadline-exceeded'}<=set(rows[0]['allowed_error_codes']);yes('original '+operation+' catalog permits sanitized margin preclaim codes')
# Bound RuntimeBinding is a frozen selection rather than an API mode switch.
assert M.RuntimeBinding.__dataclass_params__.frozen;yes('private runtime composition selection frozen')
# MA01 exact original schema representation, with no source permission renewal.
selected_period={'path':'product/lab/release-candidates/v1/interface/owned-period.json','sha256':'4'*64}
original_period={'ref':selected_period['path'],'sha256':selected_period['sha256']}
assert M.period_correspondence(original_period,selected_period)==selected_period;yes('MA01 original ref+sha256 canonically corresponds to selected path+sha256')
for value in [{**original_period,'ref':'different-period.json'},{**original_period,'sha256':'5'*64},{**original_period,'path':selected_period['path']},selected_period]:
 refused('MA01 exact locator/digest/closed original shape mismatch',lambda value=value:M.period_correspondence(value,selected_period),M.MarginBeforeClaim,'integrity-failed')
# Real ordinary no-follow directory/lock custody, no Lab lock or readers.
with tempfile.TemporaryDirectory(prefix='cal-T03-margin-journal-scope-') as d:
 base=Path(d);host=base/'host';journal=base/'application';host.mkdir(mode=0o700);journal.mkdir(mode=0o700)
 for root in [host,journal]:(root/'.lock').write_bytes(b'');(root/'.lock').chmod(0o600)
 scope={'root':str(journal),'workspace_binding':{'ref':'workspace:inert','sha256':'6'*64},'manifest_sha256':'6'*64}
 policy={'source8_control':{'application_journal_scope':scope}}
 actual=types.SimpleNamespace(channel=types.SimpleNamespace(policy_guard=lambda:policy),vault=types.SimpleNamespace(root=host))
 chosen=M.assessment_scope(actual);assert chosen==scope and chosen is not scope and chosen['workspace_binding'] is not scope['workspace_binding'];yes('MA03 original selected scope captured without mutable alias')
 count=len(os.listdir('/proc/self/fd'))
 with C.JournalBoundary(journal,host):pass
 assert count==len(os.listdir('/proc/self/fd'));yes('MA03 real distinct owned directory and lock identities with no lock acquisition')
 for value in [None,{**scope,'root':str(host)}]:
  policy['source8_control']['application_journal_scope']=value
  refused('MA03 None or own selected journal refuses before delegated reader',lambda:M.assessment_scope(actual),M.MarginBeforeClaim,'closure-missing')
 policy['source8_control']['application_journal_scope']=scope
 refused('MA03 same physical directory refusal before delegation',lambda:C.JournalBoundary(host,host).__enter__(),ValueError)
 (journal/'.lock').unlink();os.link(host/'.lock',journal/'.lock')
 refused('MA03 hardlinked held-lock inode refuses without acquiring it',lambda:C.JournalBoundary(journal,host).__enter__(),ValueError)
 (journal/'.lock').unlink();(journal/'.lock').write_bytes(b'');(journal/'.lock').chmod(0o600)
 journal.rename(base/'retained-application');journal.symlink_to(base/'retained-application')
 refused('MA03 substituted journal directory symlink refuses before reader',lambda:C.JournalBoundary(journal,host).__enter__(),OSError)
 assert count==len(os.listdir('/proc/self/fd'));yes('MA03 every own scope refusal closes captured descriptors')
# Captured new helper graph, not original API/Source callback mutation. Every
# fault uses a new independent candidate module namespace and is discarded.
def helper_episode():
 prefix='_margin_integrity_'+uuid.uuid4().hex;pkg=types.ModuleType(prefix);pkg.__path__=[];sys.modules[prefix]=pkg;modules={};bodies={}
 for leaf in ['margin_capture','margin_kernel','margin_seal','observed_margin']:
  path=API/(leaf+'.py');raw=path.read_bytes();m=types.ModuleType(prefix+'.'+leaf);m.__file__=str(path);m.__package__=prefix;sys.modules[m.__name__]=m
  exec(compile(raw,str(path),'exec'),m.__dict__);modules[leaf]=m;bodies[leaf]=raw
 margin=modules['observed_margin'];seal=modules['margin_seal'];held=seal.make_guard(modules,bodies,margin.code_check);held[0]()
 return modules,held
mods,held=helper_episode();held[0]();yes('MA02 entire selected new helper graph accepts unchanged exact captured code/constants/context')
faults=[('kernel decide same-object code',lambda ms:setattr(ms['margin_kernel'].decide,'__code__',(lambda *args,**kw:None).__code__)),
 ('kernel instant same-object code',lambda ms:setattr(ms['margin_kernel'].instant,'__code__',(lambda value:None).__code__)),
 ('kernel require same-object code',lambda ms:setattr(ms['margin_kernel'].require,'__code__',(lambda *args:None).__code__)),
 ('capture same-object code',lambda ms:setattr(ms['margin_capture'].capture,'__code__',(lambda *args,**kw:b'').__code__)),
 ('checkpoint table in-place removal',lambda ms:ms['margin_kernel'].CHECKPOINTS.clear()),
 ('remaining phase table in-place change',lambda ms:ms['margin_kernel'].REMAINING.update({'application-preclaim':()})),
 ('adapter helper alias substitution',lambda ms:setattr(ms['observed_margin'],'C',types.SimpleNamespace())),
 ('adapter require code substitution',lambda ms:setattr(ms['observed_margin'].need,'__code__',(lambda *args:None).__code__)),
 ('helper defaults substitution',lambda ms:setattr(ms['margin_capture'].capture,'__kwdefaults__',{'control_root':None,'root_identity':None,'max_bytes':1})),
 ('source-owned period/mode constant drift',lambda ms:setattr(ms['observed_margin'],'MODES',('enforce-observed-margin',))),
 ('helper method substitution',lambda ms:setattr(ms['observed_margin'].RuntimeBinding,'check_entry',lambda *args:None)),
 ('guard snapshot same-object code',lambda ms:setattr(ms['margin_seal'].snapshot,'__code__',(lambda value:None).__code__)),
 ('new namespace injection',lambda ms:setattr(ms['margin_kernel'],'FOREIGN',True))]
for label,mutate in faults:
 ms,seal=helper_episode();mutate(ms);refused('MA02 '+label,seal[0],ValueError)
# Initial constant drift must refuse from original independently captured AST,
# rather than accepting the wrong mutable table as a new trusted baseline.
ms,seal=helper_episode();ms['margin_kernel'].CHECKPOINTS.clear()
refused('MA02 pre-bind checkpoint drift fails exact source-owned table',lambda:ms['margin_seal'].make_guard(ms,{k:(API/(k+'.py')).read_bytes() for k in ms},ms['observed_margin'].code_check),ValueError)
# Static data flow: every execution of the fresh new gate is bracketed by a
# caller-held guard, before original allocation; historical branches unchanged.
tree=ast.parse((API/'workspace.py').read_bytes());text=ast.unparse(next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='claim'))
assert text.index('guard()')<text.index('before_claim(self, call, context, deadline)')<text.index('original = self.object(raw)')
assert "guard.__code__ is not runtime.helper_guard_code" in text and "guard.__defaults__ is not runtime.helper_guard_defaults" in text and 'finally:' in text;yes('MA02 caller held guard checks bracket gate before object and allocation')
observed=ast.unparse(next(n for n in ast.walk(ast.parse((API/'observed_margin.py').read_bytes())) if isinstance(n,ast.FunctionDef) and n.name=='observed'))
assert observed.index('selected_scope = assessment_scope(host)')<observed.index('builder.preflight(')<observed.index('builder.completed_candidate_application(');yes('MA03 actual staged assessment scope gate precedes both original delegated readers')

verify();report={'schema_version':'lab-T03-margin-production-postimage-pure-controls/v1-candidate','result':'PASS-pure-contract-and-staging-only','case_count':len(cases),'cases':cases,'source_selection_sha256':sha((HERE/'control-source-selection.json').read_bytes()),'actual_original_Lab_constructor_lease_native_or_claim_effect':False,'synthetic_reserves_not_empirical_calibration':True,'current_runtime_or_full_learning_sequence_qualified':False,'authority_effect':'none','task_complete':False}
(HERE/'controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'cases':len(cases),'result_sha256':sha((HERE/'controls-result.json').read_bytes())}))
