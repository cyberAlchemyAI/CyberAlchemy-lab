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
for leaf in ['margin_capture','margin_kernel','observed_margin']:
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
verify();report={'schema_version':'lab-T03-margin-production-postimage-pure-controls/v1-candidate','result':'PASS-pure-contract-and-staging-only','case_count':len(cases),'cases':cases,'source_selection_sha256':sha((HERE/'control-source-selection.json').read_bytes()),'actual_original_Lab_constructor_lease_native_or_claim_effect':False,'synthetic_reserves_not_empirical_calibration':True,'current_runtime_or_full_learning_sequence_qualified':False,'authority_effect':'none','task_complete':False}
(HERE/'controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'cases':len(cases),'result_sha256':sha((HERE/'controls-result.json').read_bytes())}))
