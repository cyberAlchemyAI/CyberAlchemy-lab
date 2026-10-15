"""Authored owned metadata/signature/custody controls; unrun until Root review."""
import ast,copy,hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    pkg='_T31_v5_OWNED_INERT_invocation';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        spec=importlib.util.spec_from_file_location(pkg+'.'+leaf,path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
    load('protocol',HERE/'pure/protocol.py');C=load('workflow_output_contracts',POST/'workflow_output_contracts.py');load('workflow_output_registry',POST/'workflow_output_registry.py');load('workflow_output_validation',POST/'workflow_output_validation.py');M=load('workflow_output_material',POST/'workflow_output_material.py');F=load('workflow_producer_outputs',POST/'workflow_producer_outputs.py');fixture=load('invocation_fixture',HERE/'pure/invocation_fixture.py');checks=[]
    expected={'run_binding':{'ref':'OWNED-INERT:run-A','sha256':'1'*64},'work_ref':'OWNED-INERT:Work-A@1','source_cut':{'OWNED-INERT:cut':'A'}}
    F.invocation_arguments(fixture.exact,(),expected,expected);checks.append('actual selected signature binds exact outer run Work cut without dispatch')
    for key,value in [('work_ref','OWNED-INERT:Work-B@1'),('run_binding',{'ref':'OWNED-INERT:run-A-same-prefix','sha256':'2'*64}),('source_cut',{'OWNED-INERT:cut':'stale'})]:
        kwargs=copy.deepcopy(expected);kwargs[key]=value
        try:F.invocation_arguments(fixture.exact,(),kwargs,expected)
        except ValueError:checks.append('signature refuses different '+key+' before effect')
        else:raise AssertionError(key)
    a=F.invocation_arguments(fixture.raw_input,(b'OWNED-INERT:A',),{},expected)[1];b=F.invocation_arguments(fixture.raw_input,(b'OWNED-INERT:B',),{},expected)[1];assert a!=b;checks.append('exact original raw input bytes have distinct sealed argument selection')
    from datetime import datetime,timedelta,timezone
    actual_now=datetime.now(timezone.utc);start=(actual_now-timedelta(minutes=1)).isoformat();end=(actual_now+timedelta(minutes=1)).isoformat();instant=lambda s:datetime.fromisoformat(s)
    run={'run_ref':'OWNED-INERT:run-A','work':{'version_ref':expected['work_ref']},'source_cut':expected['source_cut'],'actor':{'principal_ref':'OWNED-INERT:principal'},'definition_binding':{'ref':'OWNED-INERT:definition','sha256':'4'*64},'state':'OWNED-INERT:ready'}
    raw=C.json.dumps(run,sort_keys=True,separators=(',',':')).encode();selected=dict(expected,run_binding={'ref':'OWNED-INERT:run-A','sha256':C.sha(raw)},scope_ref='OWNED-INERT:scope',principal_ref='OWNED-INERT:principal')
    ref='OWNED-INERT:phase';grant=dict(selected,definition_binding=run['definition_binding'],permitted_transitions=[ref],permitted_effects=['candidate-workflow-transition'],actor_role_refs=['OWNED-INERT:role'],not_before=start,expires_at=end)
    definition={'transitions':[{'transition_ref':ref,'from_state':run['state'],'actor_role_refs':['OWNED-INERT:role']}]}
    F.verify_invocation_preimage(ref,selected,raw,raw,grant,definition,actual_now,instant);checks.append('selected original run and independently current grant correspondence metadata passes')
    for key,value in [('run_binding',{'ref':'OWNED-INERT:run-A-same-prefix','sha256':'5'*64}),('principal_ref','OWNED-INERT:foreign'),('scope_ref','OWNED-INERT:foreign'),('source_cut',{'OWNED-INERT:stale':True}),('expires_at',start),('permitted_effects',['OWNED-INERT:unrelated-effect'])]:
        altered=dict(grant);altered[key]=value
        try:F.verify_invocation_preimage(ref,selected,raw,raw,altered,definition,actual_now,instant)
        except ValueError:checks.append('fresh original grant refuses different/stale '+key)
        else:raise AssertionError(key)
    try:F.verify_invocation_preimage(ref,selected,raw,raw+b' ',grant,definition,actual_now,instant)
    except ValueError:checks.append('changed actual journal predecessor refuses before invocation')
    else:raise AssertionError('changed journal preimage')
    with tempfile.TemporaryDirectory(prefix='cal-T31-v4-own-input-')as folder:
        root=Path(folder);root.chmod(0o700);(root/'invocations').mkdir(mode=0o700);(root/'materials').mkdir(mode=0o700);(root/'materials-other').mkdir(mode=0o700);(root/'claims').mkdir(mode=0o700);st=root.stat()
        descriptor={'schema_version':'lab-private-late-workflow-inputs/v1-candidate','resolver_binding':{},'resolver_entrypoint':'LateInvocationInputs.resolve','assembler_binding':{},'assembler_entrypoint':'InvocationAssembler.bind','custody':{'root':str(root),'identity':[st.st_dev,st.st_ino,os.getuid(),0o700],'output_roots':['invocations','materials']},'phase_contracts':{}}
        host=types.SimpleNamespace();reader=M.LateInvocationInputs(host,{'invocation_inputs':descriptor,'transitions':{}},guard=lambda:None,read_public=None,source_rows=set())
        def selected_file(path,raw):
            with path.open('xb')as f:f.write(raw)
            path.chmod(0o600);s=path.stat();return {'path':path.relative_to(root).as_posix(),'identity':[s.st_dev,s.st_ino,os.getuid(),0o600],'sha256':hashlib.sha256(raw).hexdigest()}
        good=selected_file(root/'materials/input.json',b'{"OWNED-INERT":true}\n');assert reader.read(good)==b'{"OWNED-INERT":true}\n';checks.append('held private input owner mode identity byte hash and prefix selection passes')
        foreign=selected_file(root/'materials-other/input.json',b'{}\n')
        try:reader.read(foreign)
        except ValueError:checks.append('same-prefix sibling custody refuses')
        else:raise AssertionError('same prefix custody')
        for altered in [dict(good,sha256='3'*64),dict(good,identity=[0,1,os.getuid(),0o600])]:
            try:reader.read(altered)
            except ValueError:checks.append('foreign private input digest/identity refuses')
            else:raise AssertionError('wrong input accepted')
        (root/'materials/input.json').write_bytes(b'{"OWNED-INERT":false}\n')
        try:reader.read(good)
        except ValueError:checks.append('changed selected predecessor/input bytes refuse')
        else:raise AssertionError('changed input accepted')
        # Bounded durable technical leaves, no original authority/producer calls.
        packet={'invocation_ref':'OWNED-INERT:durable','run_binding':selected['run_binding'],'work_ref':selected['work_ref'],'source_cut':selected['source_cut'],'principal_ref':selected['principal_ref'],'input_seal':'6'*64,'producer_binding':{'path':'OWNED-INERT.py','sha256':'7'*64},'producer_entrypoint':'exact'}
        chosen=selected_file(root/'invocations/intent-input.json',json.dumps(packet,sort_keys=True).encode())
        cap=M.LateInvocation(reader,'OWNED-INERT:phase',chosen,packet);reader.originals[cap.seal]=reader.read(chosen)
        M.consume_inputs(reader,cap);assert cap.used;checks.append('exclusive durable intent seals exact actual input before any dispatch')
        try:M.consume_inputs(reader,cap)
        except ValueError:checks.append('duplicate durable invocation consumption refuses')
        else:raise AssertionError('duplicate durable consumption')
        material=types.SimpleNamespace(materials={'OWNED-INERT':True},seal='8'*64,digest=lambda:'8'*64)
        result=types.SimpleNamespace(pending=False,material=material,seal='9'*64)
        try:M.verify_completed_inputs(reader,cap,result)
        except ValueError:checks.append('read-only selection refuses missing completion without writing')
        else:raise AssertionError('uncompleted selected')
        completed=M.complete_inputs(reader,cap,result);assert M.verify_completed_inputs(reader,cap,result)==completed
        assert M.complete_inputs(reader,cap,result)==completed;checks.append('exact known completion reconciles once and read-only verification matches')
        restarted=M.LateInvocationInputs(host,{'invocation_inputs':dict(descriptor,phase_contracts={'OWNED-INERT:phase':{}}),'transitions':{'OWNED-INERT:phase':{'invocation_ref':'OWNED-INERT:durable'}}},guard=lambda:None,read_public=None,source_rows=set())
        try:restarted.resolve('OWNED-INERT:phase',chosen)
        except ValueError:checks.append('fresh reader restart refuses existing durable intent before input resolution or redispatch')
        else:raise AssertionError('restart redispatch allowed')
        result.seal='a'*64
        try:M.verify_completed_inputs(reader,cap,result)
        except ValueError:checks.append('foreign result seal refuses exact durable completion')
        else:raise AssertionError('foreign completion')
        reader.plan={'transitions':{'OWNED-INERT:phase':{'invocation_ref':'OWNED-INERT:group'}}};reader.claims['OWNED-INERT:group']=object()
        try:reader.resolve('OWNED-INERT:phase',good)
        except ValueError:checks.append('duplicate one-shot resolver consumption refuses before reading/dispatch')
        else:raise AssertionError('duplicate resolution')
    initial=dict(run,intent='OWNED-INERT:intent',intent_resolution='OWNED-INERT:resolution',coordination_context='OWNED-INERT:coordination',event_bindings=[])
    event={'ref':'OWNED-INERT:event','sha256':'b'*64};later=dict(initial,state='OWNED-INERT:successor',event_bindings=[event])
    F.verify_original_successor(initial,later,selected,before=initial,event_binding=event);checks.append('later slot joins protected original initial run and exact one-event successor metadata')
    for key,value in [('run_ref','OWNED-INERT:run-A-same-prefix'),('work',{'version_ref':'OWNED-INERT:Work-B@1'}),('source_cut',{'OWNED-INERT:cut':'stale'}),('actor',{'principal_ref':'OWNED-INERT:foreign'}),('definition_binding',{'ref':'OWNED-INERT:foreign','sha256':'c'*64}),('event_bindings',[{'ref':'OWNED-INERT:other-event','sha256':'d'*64}])]:
        altered=copy.deepcopy(later);altered[key]=value
        try:F.verify_original_successor(initial,altered,selected,before=initial,event_binding=event)
        except ValueError:checks.append('later slot refuses foreign/stale successor '+key)
        else:raise AssertionError(key)
    changed=copy.deepcopy(initial);changed['work']={'version_ref':'OWNED-INERT:foreign'}
    try:F.verify_original_successor(initial,later,selected,before=changed,event_binding=event)
    except ValueError:checks.append('changed original predecessor refuses later-slot metadata join')
    else:raise AssertionError('changed predecessor accepted')
    tree=ast.parse((POST/'workflow_producer_outputs.py').read_bytes());klass=next(c for c in tree.body if isinstance(c,ast.ClassDef)and c.name=='ProducerInvocationFactory');invoke=next(f for f in klass.body if isinstance(f,ast.FunctionDef)and f.name=='invoke');text=ast.unparse(invoke)
    assert text.index('invocation_arguments(')<text.index('capsule = InvocationResult(')<text.index('value = fn(')
    assert text.index('current_invocation(')<text.index('capsule = InvocationResult(')
    assert 'initial' in ast.unparse(next(f for f in tree.body if isinstance(f,ast.FunctionDef)and f.name=='select_original_run'))
    checks.append('full actual current run and signature checks precede domain capsule reservation and dispatch')
    return checks
