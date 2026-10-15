"""Two narrow own inert probes; no API/native/Source/producer construction."""
import ast,copy,hashlib,inspect,json,os,re,stat,sys,tempfile
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0004';POST=P/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,why):
 if not ok:raise ValueError(why)
def closed(value,fields):need(type(value)is dict and set(value)==set(fields),'closed fixture')
def klass(path,name):return next(n for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.ClassDef)and n.name==name)
def fds():
 rows={}
 for n in os.listdir('/proc/self/fd'):
  try:s=os.fstat(int(n));rows[n]=(s.st_dev,s.st_ino,s.st_mode)
  except OSError:continue
 return rows

def main():
 before=fds();factory=klass(POST/'workflow_producer_outputs.py','ProducerInvocationFactory');invoke=next(n for n in factory.body if isinstance(n,ast.FunctionDef)and n.name=='invoke')
 # Compile the actual declaration, but bind signature only. No function body or
 # producer is executed. No original callback or module is modified.
 signature_env={};unit=ast.Module(body=[invoke],type_ignores=[]);ast.fix_missing_locations(unit);exec(compile(unit,str(POST/'workflow_producer_outputs.py'),'exec'),signature_env)
 error=None
 try:inspect.signature(signature_env['invoke']).bind(object(),'transition:operational-learning:application-recorded',run_binding={},work_ref='OWNED-WORK',source_cut={},args=('OWNED-SELECTION','OWNED-LESSON'),kwargs={'current_context_reader':None})
 except TypeError as e:error=str(e)
 need(error is not None and 'late_selection'in error,'expected exact caller-signature mismatch absent')
 bootstrap=klass(P/'bootstrap.py','InvocationAssembler');install=next(n for n in bootstrap.body if isinstance(n,ast.FunctionDef)and n.name=='install_consumer')
 need(any(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=='install_w06_consumer'for n in ast.walk(install)),'consumer not discarded as reviewed')
 tree=ast.parse((POST/'workflow_output_material.py').read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='relative']+[klass(POST/'workflow_output_material.py','PrivateOutputMaterial')]
 env={'ROOT':ROOT,'Path':Path,'copy':copy,'os':os,'stat':stat,'re':re,'sha':sha,'need':need,'closed':closed}
 unit=ast.Module(body=nodes,type_ignores=[]);ast.fix_missing_locations(unit);sourcefile=str(POST/'workflow_output_material.py');exec(compile(unit,sourcefile,'exec'),env)
 M=env['PrivateOutputMaterial'];observed={};oldtrace=sys.gettrace();need(oldtrace is None,'isolated probe trace required')
 with tempfile.TemporaryDirectory(prefix='cal-T31-v4-inert-input-mode-')as tmp:
  root=Path(tmp);root.chmod(0o700);(root/'materials').mkdir(mode=0o700);file=root/'materials/input.json';body=b'{"OWNED_INERT_INPUT":true}';file.write_bytes(body);file.chmod(0o600);s=root.stat();leaf=file.stat()
  reader=object.__new__(M);reader.host_guard=lambda:None;reader.descriptor={'output_custody':{'root':str(root),'identity':[s.st_dev,s.st_ino,s.st_uid,0o700],'output_roots':['materials']}};reader.before={}
  fired=[]
  def trace(frame,event,arg):
   if event=='call'and frame.f_code.co_filename==sourcefile and frame.f_code.co_name=='attached'and not fired:
    fired.append(True);(root/'materials').chmod(0o755)
   return trace
  try:
   sys.settrace(trace)
   result=reader.capture({'path':'materials/input.json','original_binding':{'ref':'OWNED-INERT','sha256':sha(body)}},input_identity=[leaf.st_dev,leaf.st_ino,leaf.st_uid,0o600])
  finally:sys.settrace(oldtrace)
  need(fired and result==body,'actual selected custody mode counterexample did not occur')
  observed={'raw_returned_after_required_intermediate_700_became':stat.S_IMODE((root/'materials').stat().st_mode),'leaf_mode_stayed':stat.S_IMODE(file.stat().st_mode),'source_expected_intermediate_mode':0o700,'actual_function_returned_exact_bytes':True,'root_mode_stayed':stat.S_IMODE(root.stat().st_mode),'host_guard_is_explicit_inert_fixture':True,'actual_private_body_access_or_effect_claimed':False}
 need(fds()==before,'probe descriptor leak')
 return {'result':'COUNTEREXAMPLES-CONFIRMED-owned-inert-only','authority_effect':'none','W06_interface':{'actual_factory_signature':str(inspect.signature(signature_env['invoke'])),'old_call_missing_required_arguments_error':error,'assembler_discards_actual_returned_consumer':True,'function_body_or_original_producer_called':False},'late_input_intermediate_mode':observed,'FD_delta':0,'original_callbacks_or_os_methods_mutated':False,'full_authored_control_suite_executed':False,'actual_API_Source_native_lease_or_original_producer_executed':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
