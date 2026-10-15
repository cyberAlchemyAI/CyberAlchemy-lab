"""Independent extracted code on owned inert fixtures; no original producer calls."""
import ast,copy,fcntl,hashlib,json,os,re,stat,sys,tempfile,types
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab');B=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31';P=B/'output-integration-preparation-0005';OLD=B/'output-integration-preparation-0004';POST=P/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17';OUT=B/'output-integration-independent-review-0005';checks=[]
def need(v,why):
 if not v:raise ValueError(why)
def check(v,why):need(v,why);checks.append(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def closed(v,fields):need(type(v)is dict and set(v)==set(fields),'closed fixture')
def fds():
 d={}
 for n in os.listdir('/proc/self/fd'):
  try:s=os.fstat(int(n));d[n]=(s.st_dev,s.st_ino,s.st_mode,fcntl.fcntl(int(n),fcntl.F_GETFL),fcntl.fcntl(int(n),fcntl.F_GETFD))
  except OSError:pass
 return d
def klass(p,n):return next(x for x in ast.parse(p.read_bytes()).body if isinstance(x,ast.ClassDef)and x.name==n)
def extracted(path,names,env):
 nodes=[n for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names];unit=ast.Module(body=nodes,type_ignores=[]);ast.fix_missing_locations(unit);exec(compile(unit,str(path),'exec'),env);return env
before=fds();check(sys.gettrace()is None,'isolated observer control no initial trace')
mat=POST/'workflow_output_material.py';env={'ROOT':R,'Path':Path,'copy':copy,'os':os,'stat':stat,'re':re,'sha':sha,'need':need,'closed':closed};extracted(mat,{'relative','PrivateOutputMaterial'},env);M=env['PrivateOutputMaterial']
for which,input_mode,ordinary in [('none',448,False),('intermediate',448,False),('root',448,False),('ordinary755',493,True)]:
 with tempfile.TemporaryDirectory(prefix='cal-T31-v5-independent-custody-')as tmp:
  root=Path(tmp);root.chmod(0o700);(root/'materials').mkdir(mode=input_mode);file=root/'materials/input.json';body=b'{"OWNED_INERT":true}';file.write_bytes(body);file.chmod(0o600);s=root.stat();leaf=file.stat();reader=object.__new__(M);reader.host_guard=lambda:None;reader.descriptor={'output_custody':{'root':str(root),'identity':[s.st_dev,s.st_ino,s.st_uid,448],'output_roots':['materials']}};reader.before={};fired=[]
  def trace(frame,event,arg):
   if event=='call'and frame.f_code.co_filename==str(mat)and frame.f_code.co_name=='attached'and not fired and which in ('intermediate','root'):
    fired.append(True);(root/'materials'if which=='intermediate'else root).chmod(0o755)
   return trace
  failed=False
  try:
   sys.settrace(trace)
   raw=reader.capture({'path':'materials/input.json','original_binding':{'ref':'OWNED-INERT','sha256':sha(body)}},input_identity=None if ordinary else [leaf.st_dev,leaf.st_ino,leaf.st_uid,384])
  except ValueError:failed=True
  finally:sys.settrace(None)
  if which in ('intermediate','root'):check(fired and failed,'actual final selected input '+which+' mode drift refuses')
  else:check(not failed and raw==body,'actual positive capture '+which)
  check(fds()==before,'custody case descriptors restored '+which)
# Pure selected result observation: actual method bodies, explicit inert objects.
lpath=POST/'workflow_lesson_consumer.py';scope={'ROOT':R,'Path':Path,'sha':sha,'need':need};extracted(lpath,{'W06Consumer'},scope);W=scope['W06Consumer'];host=object();ref='transition:operational-learning:application-recorded';lineage={'run_binding':{'ref':'OWNED-INERT:run','sha256':'1'*64},'work_ref':'OWNED-INERT:work','source_cut':{'OWNED-INERT:cut':True}}
selection=types.SimpleNamespace(original_ref='OWNED-INERT:selection',context=types.SimpleNamespace(session_ref='OWNED-INERT:session',source_head='OWNED-INERT:source'))
repaired=b'OWNED-INERT repaired';stdout=json.dumps({'controlled':True,'source_sha256':sha(repaired)}).encode();observed={'controlled':True,'returncode':0,'original_source_unchanged':True,'inline_only_change':True,'lesson_ref':'OWNED-INERT:lesson','selection_ref':selection.original_ref,'session_ref':selection.context.session_ref,'source_head':selection.context.source_head,'repaired_source_ref':'repaired','stdout_ref':'stdout','stderr_ref':'stderr','result':json.loads(stdout)};bodies={'repaired':repaired,'stdout':stdout,'stderr':b'OWNED-INERT stderr','manifest':json.dumps(observed).encode()};app=types.SimpleNamespace(application_ref='OWNED-INERT:application',observed=observed,manifest_ref='manifest',e=types.SimpleNamespace(original=lambda ref:bodies[ref]));cap=types.SimpleNamespace(ref=ref,packet=lineage,guard=lambda:None);factory=types.SimpleNamespace(host=host,inputs=types.SimpleNamespace(active=cap))
def verifier():
 v=object.__new__(W);v.pending=False;v.host=host;v.factory=factory;v.transition_ref=ref;v.application=app;v.module=types.SimpleNamespace(parse=json.loads);v.binding={'path':'OWNED-INERT-code','sha256':sha(b'OWNED-INERT-code')};v.read_public=lambda b:b'OWNED-INERT-code';v.host_guard=lambda:None;return v
def call(v=None,**changes):return (v or verifier()).verify_result(selection,'OWNED-INERT:lesson',app.application_ref,**dict(lineage,**changes))
x=call();check(x['producer_redispatched']is False and x['actual_child_consumption_verified']is True and x['stdout_sha256']==sha(stdout),'actual observer validates only already-returned inert result')
def refuse(label,fn):
 try:fn()
 except (ValueError,KeyError):checks.append(label)
 else:raise AssertionError(label)
v=verifier();call(v);refuse('one-shot verifier refuses second observation',lambda:call(v))
for field,value in [('work_ref','foreign'),('run_binding',{'ref':'foreign','sha256':'2'*64}),('source_cut',{'foreign':True})]:refuse('actual verifier refuses '+field+' mismatch',lambda field=field,value=value:call(**{field:value}))
for key in ('repaired','stdout','manifest'):
 old=bodies[key];bodies[key]=b'{"OWNED-INERT:foreign":true}';refuse('actual observer refuses selected '+key+' byte mismatch',call);bodies[key]=old
# Complete postimage comparison; all unmentioned files remain byte-identical.
changed={q.name for q in POST.iterdir()if q.is_file()and q.read_bytes()!=(OLD/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'/q.name).read_bytes()};check(changed=={'workflow_lesson_consumer.py','workflow_output_material.py','workflow_producer_outputs.py'},'exact three declared changed API postimages, remaining23 byte-identical')
producer=klass(POST/'workflow_producer_outputs.py','ProducerInvocationFactory');invoke=next(x for x in producer.body if isinstance(x,ast.FunctionDef)and x.name=='invoke');text=ast.unparse(invoke);check(text.count('value = fn(')==1 and text.index('value = fn(')<text.index('self.assembler.verify_result(')<text.index('capsule._seal = result_seal(')<text.index('material.close('),'actual original dispatch once, post-result verification before seal/material')
check(not any(isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=='invoke'for x in ast.walk(klass(lpath,'W06Consumer'))),'actual W06 verifier cannot recursively invoke producer')
aenv={'Path':Path,'hashlib':hashlib};extracted(P/'bootstrap.py',{'InvocationAssembler'},aenv);A=aenv['InvocationAssembler'];a=object.__new__(A);a.pending_consumer=(object(),object());a.host=host;a.read_public=None;a.consumers={};token=object();a.api_factory=types.SimpleNamespace(install_w06_consumer=lambda *a,**kw:token);check(a.install_consumer(ref)is token and a.consumers[ref]is token,'actual assembler retains selected verifier');refuse('actual assembler refuses verifier replacement',lambda:a.install_consumer(ref))
check(fds()==before and sys.gettrace()is None and 'ctypes'not in sys.modules,'whole own inert fixture exact FDmap and observer cleanup')
res={'schema_version':'lab-T31-v5-independent-fix-controls/v1','result':'PASS-owned-inert-only','check_count':len(checks),'checks':checks,'FD_delta':0,'original_child_API_Source_native_lease_or_producer_executed':False,'only_extracted_new_candidate_fixture_methods_executed':True,'authored_full_control_suite_executed':False,'genuine_W06_consumption_or_benefit_claimed':False,'authority_effect':'none'};(OUT/'fix-result.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in res.items()if k!='checks'},sort_keys=True))
