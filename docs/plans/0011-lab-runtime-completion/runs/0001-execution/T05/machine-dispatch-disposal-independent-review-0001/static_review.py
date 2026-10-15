"""Pure exact-source/AST/diagnostic review; no Machine or API imports."""
import ast,hashlib,json,os,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T05/machine-dispatch-disposal-preparation-0001'
OWN=Path(__file__).parent
HH='b618e23b9f35074a44fa4253bff514a6890a163d16b1d7f03a15106e139f1f3e'
MF='1029aad621c03914e7e4f45466e7006184f89eca20ffd39b3d2fdfa10352c6c1'
def need(v,m):
    if not v:raise ValueError(m)
def main():
    fd0=len(os.listdir('/proc/self/fd'))
    cp=RUN/'T32/native-lifecycle-recovery-adoption-0003/capture.py';raw=cp.read_bytes()
    need(hashlib.sha256(raw).hexdigest()=='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa','review capture helper differs')
    m=types.ModuleType('_T05_disposal_review_capture');m.__file__=str(cp);exec(compile(raw,str(cp),'exec'),m.__dict__);capture=m.capture_path
    handoff=capture(P/'HANDOFF.json',HH);manifest=capture(P/'source-manifest.json',MF)
    rows=json.loads(manifest)['files'];need(len(rows)==8,'all8 selected rows required');cache={}
    for row in rows:
        raw=capture(ROOT/row['path'],row['sha256']);need(len(raw)==row['size_bytes'],'selected size differs');cache[row['path']]=raw
    old=cache[str((P/'original-machine_transport.py').relative_to(ROOT))]
    new=cache[str((P/'postimages/machine_transport.py').relative_to(ROOT))]
    def methods(raw):
        return {n.name:ast.dump(n,include_attributes=False)for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)and c.name=='MachinePeer'for n in c.body if isinstance(n,ast.FunctionDef)}
    a=methods(old);b=methods(new)
    need(len(a)==len(b)==12 and set(a)==set(b)and {k for k in a if a[k]!=b[k]}=={'call'},'unexpected original Machine method change')
    old_top=[n for n in ast.parse(old).body if not isinstance(n,ast.ClassDef)]
    new_top=[n for n in ast.parse(new).body if not isinstance(n,ast.ClassDef)]
    need([ast.dump(n,include_attributes=False)for n in old_top]==[ast.dump(n,include_attributes=False)for n in new_top],'top-level code changed')
    klass=next(n for n in ast.parse(new).body if isinstance(n,ast.ClassDef)and n.name=='MachinePeer')
    call=next(n for n in klass.body if isinstance(n,ast.FunctionDef)and n.name=='call')
    attempt=call.body[0];need(isinstance(attempt,ast.Try),'original guard/capture try absent')
    need(isinstance(attempt.body[0],ast.Expr)and ast.unparse(attempt.body[0])=='self.guard()','original guard is not outside state lock')
    lock=attempt.body[1];need(isinstance(lock,ast.With)and ast.unparse(lock.items[0].context_expr)=='self._state_lock','existing exact state lock required')
    calls=[ast.unparse(n.func)for n in ast.walk(lock)if isinstance(n,ast.Call)]
    need(sorted(calls)==['min','require','self.A.now'],'new state lock invokes a resource/Service/policy callback')
    need(isinstance(call.body[-1],ast.Return)and ast.unparse(call.body[-1].value)=='service.call(raw)','original dispatcher must run outside lock and catch')
    terminal_path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T05/machine-read-diagnostic-terminal-0005.json'
    terminal=json.loads(cache[terminal_path]);rb=terminal['result_binding'];original_result=capture(Path(rb['owned_external_path']),rb['sha256'])
    need(json.loads(original_result)==terminal['original_result'],'terminal differs from actual owned result bytes')
    frames=terminal['original_result']['cases'][0]['diagnostic']['frames']
    need(any(v['function']=='call'and v['line']==214 and v['path'].endswith('/machine_transport.py')for v in frames),'actual observed dispatcher failure frame absent')
    for row in rows:need(capture(ROOT/row['path'],row['sha256'])==cache[row['path']],'selected input changed')
    need(capture(P/'HANDOFF.json',HH)==handoff and capture(P/'source-manifest.json',MF)==manifest,'frozen metadata changed')
    need(capture(Path(rb['owned_external_path']),rb['sha256'])==original_result,'actual owned diagnostic changed')
    need(len(os.listdir('/proc/self/fd'))==fd0,'review descriptor imbalance')
    value={'result':'PASS-independent-static-disposal-review','authority_effect':'none','handoff_sha256':HH,'manifest_sha256':MF,'selected_rows_entry_exit':8,'all12_original_method_names_retained':True,'unchanged_method_AST_count':11,'only_changed_method':'MachinePeer.call','all_top_level_AST_identical':True,'guard_outside_lock':True,'only_calls_under_lock':calls,'dispatcher_outside_lock_and_catch':True,'actual_diagnostic_result_sha256':rb['sha256'],'actual_case_frame_verified':'MachinePeer.call:214','FD_delta':0,'inert_controls_rerun':False,'Machine_Service_API_native_Source_guard_or_lease_called':False,'actual_timer_or_full14_qualified':False}
    with(OWN/'static-result-0001.json').open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(value,sort_keys=True))
if __name__=='__main__':main()
