"""Authored own inert W06 post-result observer and actual signature wiring controls.

These fixtures establish code correspondence only, never a genuine Lesson,
permission, application, child process, Source or benefit observation.
"""
import ast,copy,hashlib,importlib.util,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    pkg='_T31_v5_OWNED_INERT_lesson';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        spec=importlib.util.spec_from_file_location(pkg+'.'+leaf,path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
    load('protocol',HERE/'pure/protocol.py');C=load('workflow_output_contracts',POST/'workflow_output_contracts.py');W=load('workflow_lesson_consumer',POST/'workflow_lesson_consumer.py');A=load('owned_bootstrap',HERE/'bootstrap.py');checks=[]
    ref='transition:operational-learning:application-recorded';lineage={'run_binding':{'ref':'OWNED-INERT:run','sha256':'1'*64},'work_ref':'OWNED-INERT:Work@1','source_cut':{'OWNED-INERT:cut':True}}
    selection=types.SimpleNamespace(original_ref='OWNED-INERT:selection',context=types.SimpleNamespace(session_ref='OWNED-INERT:session',source_head='OWNED-INERT:head'))
    repaired=b'OWNED-INERT repaired input\n';stdout=json.dumps({'controlled':True,'source_sha256':C.sha(repaired)}).encode();stderr=b'OWNED-INERT stderr\n'
    observed={'controlled':True,'returncode':0,'original_source_unchanged':True,'inline_only_change':True,'lesson_ref':'OWNED-INERT:lesson','selection_ref':selection.original_ref,'session_ref':selection.context.session_ref,'source_head':selection.context.source_head,'repaired_source_ref':'OWNED-INERT:repaired','stdout_ref':'OWNED-INERT:stdout','stderr_ref':'OWNED-INERT:stderr','result':json.loads(stdout)}
    records={'OWNED-INERT:repaired':repaired,'OWNED-INERT:stdout':stdout,'OWNED-INERT:stderr':stderr,'OWNED-INERT:manifest':json.dumps(observed).encode()}
    class OwnCap:
        ref='transition:operational-learning:application-recorded';packet=lineage
        def guard(self):pass
    host=object();factory=types.SimpleNamespace(host=host,inputs=types.SimpleNamespace(active=OwnCap()));binding={'path':'OWNED-INERT-code','sha256':C.sha(b'OWNED-INERT selected original code')}
    application=types.SimpleNamespace(application_ref='OWNED-INERT:application',observed=observed,manifest_ref='OWNED-INERT:manifest',e=types.SimpleNamespace(original=lambda ref:records[ref]))
    def verifier():
        v=object.__new__(W.W06Consumer);v.host=host;v.factory=factory;v.transition_ref=ref;v.application=application;v.module=types.SimpleNamespace(parse=json.loads);v.binding=binding;v.read_public=lambda b:b'OWNED-INERT selected original code';v.host_guard=lambda:None;v.pending=False;return v
    value=verifier().verify_result(selection,'OWNED-INERT:lesson',application.application_ref,**lineage)
    assert value['actual_child_consumption_verified']is True and value['producer_redispatched']is False and value['stdout_sha256']==C.sha(stdout);checks.append('actual post-result verifier checks original selected child input output manifest and invocation metadata without dispatch')
    def refuses(label,fn):
        try:fn()
        except ValueError:checks.append(label)
        else:raise AssertionError(label)
    v=verifier();v.verify_result(selection,'OWNED-INERT:lesson',application.application_ref,**lineage);refuses('one original result verifier cannot verify/redispatch twice',lambda:v.verify_result(selection,'OWNED-INERT:lesson',application.application_ref,**lineage))
    refuses('foreign original application result refuses',lambda:verifier().verify_result(selection,'OWNED-INERT:lesson','OWNED-INERT:foreign',**lineage))
    for key,foreign in [('work_ref','OWNED-INERT:other-Work'),('run_binding',{'ref':'OWNED-INERT:run-same-prefix','sha256':'2'*64}),('source_cut',{'OWNED-INERT:stale':True})]:
        wrong=dict(lineage,**{key:foreign});refuses('W06 exact capsule refuses different '+key,lambda wrong=wrong:verifier().verify_result(selection,'OWNED-INERT:lesson',application.application_ref,**wrong))
    for changed in [('stdout',b'{"OWNED-INERT:foreign":true}'),('repaired',b'OWNED-INERT foreign input'),('manifest',b'{"OWNED-INERT:foreign":true}')]:
        key,raw=changed;old=records['OWNED-INERT:'+key];records['OWNED-INERT:'+key]=raw
        refuses('W06 original '+key+' bytes mismatch refuses',lambda:verifier().verify_result(selection,'OWNED-INERT:lesson',application.application_ref,**lineage));records['OWNED-INERT:'+key]=old
    # Actual assembler installer retains the return. No original API object exists.
    installed=object();assembler=object.__new__(A.InvocationAssembler);assembler.pending_consumer=(object(),object());assembler.api_factory=types.SimpleNamespace(install_w06_consumer=lambda *a,**k:installed);assembler.host=host;assembler.read_public=None;assembler.consumers={}
    assert assembler.install_consumer(ref)is installed and assembler.consumers[ref]is installed;checks.append('actual assembler retains and returns selected W06 verifier')
    tree=ast.parse((POST/'workflow_producer_outputs.py').read_bytes());klass=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='ProducerInvocationFactory');invoke=next(n for n in klass.body if isinstance(n,ast.FunctionDef)and n.name=='invoke');text=ast.unparse(invoke)
    assert text.count('value = fn(')==1 and text.index('value = fn(')<text.index('self.assembler.verify_result(')<text.index('capsule._seal = result_seal(')<text.index('material.close(')
    assert not any(isinstance(n,ast.Call)and ast.unparse(n.func).endswith('.invoke')for n in ast.walk(ast.parse((POST/'workflow_lesson_consumer.py').read_bytes())))
    checks.append('actual Factory calls one original producer then installed verifier before result sealing; verifier has no recursive invoke')
    return checks
