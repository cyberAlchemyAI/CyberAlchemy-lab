"""Pure new-observer/AST controls. No API import, Source guard or Lab lease."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import threading
import types
import uuid
HERE=Path(__file__).resolve().parent


def need(value,message):
    if not value:raise AssertionError(message)


def check(captured):
    cases=[];entry_fds=len(os.listdir('/proc/self/fd'))
    tools_before=[sys.monitoring.get_tool(i) for i in range(6)];profile_before=sys.getprofile();trace_before=sys.gettrace()
    name='_cal_T35_phase_pure_'+uuid.uuid4().hex
    O=types.ModuleType(name);O.__file__=str(HERE/'observe.py');sys.modules[name]=O
    exec(compile(captured['observe.py'],O.__file__,'exec'),O.__dict__)
    selected={'schema_version':'lab-full-learning-measurement-selection/v1-candidate','collection_mode':'phase-only',
        'monitoring_reservation':{'tool_id':5,'tool_name':'cal-full-learning-measurement-v2'},'cProfile_enabled':False,'authority_effect':'none'}
    def refuse(label,callback):
        try:callback()
        except (ValueError,TypeError,KeyError):cases.append(label);return
        raise AssertionError(label)
    for label,edit in [
        ('unknown collection mode refuses',lambda v:v.update(collection_mode='deep')),
        ('unknown field refuses',lambda v:v.update(extra=True)),
        ('missing field refuses',lambda v:v.pop('authority_effect')),
        ('null independent reservation refuses',lambda v:v['monitoring_reservation'].update(tool_id=None)),
        ('boolean tool id refuses',lambda v:v['monitoring_reservation'].update(tool_id=True)),
        ('unselected name refuses',lambda v:v['monitoring_reservation'].update(tool_name='other')),
        ('enabled profile refuses',lambda v:v.update(cProfile_enabled=True))]:
        value=copy.deepcopy(selected);edit(value);refuse(label,lambda v=value:O.measurement_check(v))
    refuse('unselected measurement has no default permit',lambda:O.Observer(HERE,lambda _:None))
    refuse('CLI profiling cannot silently override mode',lambda:O.Observer(HERE,lambda _:None,True,measurement=selected))
    # No callback registration or event enabling appears anywhere in this
    # observer source. Reserve-only remains an explicit, separate operation.
    tree=ast.parse(captured['observe.py'])
    forbidden={'register_callback','set_local_events','set_events','setprofile','settrace'}
    need(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden for n in ast.walk(tree)),'observer enables event collection')
    cases.append('no monitoring/profile/trace callback registration or event enabling in observer AST')
    events=[];o=O.Observer(HERE,events.append,False,measurement=selected);o.start()
    try:
        need(o.tool==5 and sys.monitoring.get_tool(5)==O.TOOL_NAME and sys.monitoring.get_events(5)==0,'actual reserve-only state differs')
        cases.append('actual selected tool5 reservation with zero global event mask')
        second=O.Observer(HERE,lambda _:None,False,measurement=selected)
        refuse('occupied selected tool refuses without fallback',second.start)
        need(second.tool is None and sys.monitoring.get_tool(5)==O.TOOL_NAME and sys.monitoring.get_tool(4)==tools_before[4],'occupied reservation disturbed other owner')
        sentinel=object();need(o.measure('return-object',lambda:sentinel,lambda:{'cut':'fixture'}) is sentinel,'return replaced')
        cases.append('actual callback return identity and direct phase metadata preserved')
        def nested():return o.measure('inner',lambda:37,lambda:{})
        need(o.measure('outer',nested,lambda:{})==37,'nested result altered')
        ends=[r for r in events if r['event']=='phase-end'];by={r['phase']:r for r in ends}
        need(by['inner']['phase_token']!=by['outer']['phase_token'],'nested token reused')
        for row in ends:
            need(row['elapsed_seconds']>=0 and row['parent_CPU_seconds']>=0 and row['measuring_thread_CPU_seconds']>=0,'invalid real time sample')
            need(row['trusted_call_counts'] is None and row['nested_code_timings'] is None and row['lock_observations'] is None,'uncollected represented as complete counts')
            need(row['reaped_children_user_CPU_seconds']>=0 and row['reaped_children_system_CPU_seconds']>=0 and 'running/unreaped' in row['child_CPU_coverage'],'child CPU coverage incorrect')
            need(row['measurement_coverage']['sys_monitoring_event_collection_enabled'] is False,'collection coverage false claim')
        cases.extend(['nested phase tokens independent and timing overlap disclosed','real wall/process/thread/reaped-child CPU with precise coverage','uncollected function/exception/lock results null, not zero-complete'])
        error=RuntimeError('PRIVATE-PRIMARY-SENTINEL')
        def primary():raise error
        def missing_metadata():raise LookupError('PRIVATE-METADATA-SENTINEL')
        try:o.measure('primary-with-metadata-fault',primary,missing_metadata)
        except RuntimeError as actual:need(actual is error,'original primary replaced')
        else:raise AssertionError('original primary swallowed')
        need(o.metadata_errors==2,'both metadata failures not counted')
        cases.append('original exception identity retained across both metadata failures')
        def caught():
            try:raise ValueError('PRIVATE-CAUGHT-SENTINEL')
            except ValueError:return True
        need(o.measure('caught',caught,lambda:{}) is True,'swallowed callback result changed')
        need(not any(e.get('event')=='trusted-exception' for e in events),'phase-only unexpectedly collected inner fault')
        cases.append('swallowed inner exception intentionally unobserved, callback result preserved')
        o.add_inline_span(caught.__code__,1,2,'foreign-attachment-negative')
        need(any(e['event']=='inline-observation-uncollected' for e in events),'inline cost limitation omitted')
        cases.append('inline negative is explicitly uncollected without skipping actual caller logic')
        barrier=threading.Barrier(3);failures=[]
        def worker(label):
            try:
                barrier.wait();need(o.measure(label,lambda:sum(range(200)),lambda:{})==19900,'thread callback changed')
            except BaseException as fault:failures.append(type(fault).__name__)
        workers=[threading.Thread(target=worker,args=('thread-'+str(i),)) for i in range(2)]
        for worker_thread in workers:worker_thread.start()
        barrier.wait()
        for worker_thread in workers:worker_thread.join()
        need(not failures,'own thread control failed')
        ends=[e for e in events if e.get('event')=='phase-end' and e['phase'].startswith('thread-')]
        need(len(ends)==2 and len({e['phase_token'] for e in ends})==2,'thread phase tokens conflated')
        cases.append('concurrent inert wrapper phases keep distinct tokens without function hooks')
        need('PRIVATE-' not in json.dumps(events),'private inert sentinel emitted')
        need(o.callback_errors is None and o.dropped is None and o.dropped_lock_observations is None and o.bookkeeping_errors==0,'uncollected/drop semantics incorrect')
        cases.append('no private args/messages/return values recorded; observer errors counted separately')
    finally:o.close()
    need([sys.monitoring.get_tool(i) for i in range(6)]==tools_before,'tool reservation leaked or other tool changed')
    cases.append('all six actual tool reservations restored; only own reservation freed')
    def emit_fail(value):raise OSError('PRIVATE-EMIT-SENTINEL')
    broken=O.Observer(HERE,emit_fail,False,measurement=selected);broken.start()
    try:
        original=RuntimeError('PRIVATE-ORIGINAL-SENTINEL')
        def fail():raise original
        try:broken.measure('emit-fault',fail,lambda:{})
        except RuntimeError as actual:need(actual is original,'emitter replaced primary')
        else:raise AssertionError('primary lost')
        need(broken.bookkeeping_errors>=2,'emitter failure not separately counted')
    finally:broken.close()
    cases.append('emitter faults cannot replace original exception and make observation incomplete')
    # Static conservation of the complete accepted execution path.
    old=ast.parse(captured['preimage/driver.py']);new=ast.parse(captured['driver.py'])
    def methods(t):
        episode=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='Episode')
        return {n.name:n for n in episode.body if isinstance(n,ast.FunctionDef)}
    A=methods(old);B=methods(new)
    preserved=[name for name in A if name not in ['__init__','run']]
    need(all(ast.dump(A[name],include_attributes=False)==ast.dump(B[name],include_attributes=False) for name in preserved),'original caller or lifecycle selection/handling body changed')
    cases.append('all original Episode methods except observation init/report integration are exact AST matches')
    need(captured['positive_lifecycle.py']==captured['preimage/positive_lifecycle.py'] and captured['security_lifecycle.py']==captured['preimage/security_lifecycle.py'],'full positive/security helper changed')
    need(captured['capture.py']==captured['preimage/capture.py'],'capture helper changed')
    cases.append('full original positive/security and capture helper bytes preserved at true successor paths')
    def before_except(method):
        initial=next(n for n in method.body if isinstance(n,ast.Try))
        return ast.dump(ast.Module(body=initial.body,type_ignores=[]),include_attributes=False)
    need(before_except(A['run'])==before_except(B['run']),'original main positive/security execution changed')
    cases.append('complete original run try-body including deadlines/effect/retry/nonce/schema/callback assertions is exact AST match')
    need(sys.getprofile() is profile_before and sys.gettrace() is trace_before,'profile/trace hook changed')
    need([sys.monitoring.get_tool(i) for i in range(6)]==tools_before and len(os.listdir('/proc/self/fd'))==entry_fds,'instrumentation or descriptor leak')
    if sys.modules.get(name) is O:del sys.modules[name]
    return {'result':'PASS-pure-component-only','controls':cases,'control_count':len(cases),'FD_delta':0,
        'actual_Source_API_or_installed_full_guards':False,'actual_Lab_native_or_lease':False,'runtime_overhead_calibration':False,'task_complete':False,'authority_effect':'none'}
