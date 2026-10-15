"""Actual pure monitoring/lock/CPU controls; no Lab constructors/callback writes."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile,threading,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def require(v,m):
    if not v:raise AssertionError(m)
def check():
    entry_fds=len(list(Path('/proc/self/fd').iterdir()))
    O=load('_T35_observer_v2_controls',HERE/'observe.py');C=load('_T35_capture_v2_controls',HERE/'capture.py')
    F=load('_T35_owned_inert',HERE/'owned_observer_fixture.py');rows={'owned_observer_fixture.py':sha((HERE/'owned_observer_fixture.py').read_bytes())}
    events=[];checks=[];o=O.Observer(HERE,events.append,False,rows,C.read);o.start();tool=o.tool
    try:
        require(o.measure('nested',F.nested,lambda:{})==F.nested(),'callback changed')
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='nested')
        by={r['function']:r for r in phase['nested_code_timings']}
        require(by['leaf']['segments']==2 and by['nested']['segments']==1,'nested segments differ')
        require(by['nested']['inclusive_elapsed_ns']>=by['nested']['exclusive_elapsed_ns']>=0 and by['leaf']['inclusive_elapsed_ns']>0,'nested timings invalid')
        checks.append('actual nested call durations and selected-exclusive subtraction')
        o.measure('caught',F.caught,lambda:{})
        require(any(e.get('monitor_event')=='raise' and e.get('exception_class')=='ValueError' for e in events),'inner raise missing')
        require(any(e.get('monitor_event')=='handled' and e.get('sanitized_code_frames') for e in events),'swallowed code traceback missing')
        checks.append('actual swallowed inner exception class/code trace')
        def unavailable():raise LookupError('PRIVATE-METADATA-SENTINEL')
        try:o.measure('primary',F.primary,unavailable)
        except RuntimeError:pass
        else:raise AssertionError('primary fault lost')
        require(o.phase is None and o.token is None and o.metadata_errors==2,'phase/metadata cleanup failed')
        checks.append('primary exception preserved across both failing metadata observations')
        def consume():
            g=F.generator();next(g);time.sleep(.025);next(g)
            try:next(g)
            except StopIteration:pass
        o.measure('generator',consume,lambda:{})
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='generator')
        row=next(r for r in phase['nested_code_timings'] if r['function']=='generator')
        require(row['yield']==2 and row['return']==1 and row['inclusive_elapsed_ns']<20_000_000,'suspension incorrectly timed')
        checks.append('yield/resume segments exclude own deliberate suspension')
        with tempfile.TemporaryDirectory(prefix='cal-T35-observer-inert-locks-') as temp:
            a=os.open(Path(temp)/'a',os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);b=os.open(Path(temp)/'b',os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600)
            try:
                o.measure('locks',lambda:F.locks(a),lambda:{})
                phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='locks')
                require(len(phase['lock_observations'])==3,'actual flock envelopes/hold missing')
                require(any(r['observation']=='same-code-single-outstanding-flock-hold-interval' and r['elapsed_ns']>1_000_000 for r in phase['lock_observations']),'hold interval invalid')
                o.measure('ambiguous',lambda:F.ambiguous_locks(a,b),lambda:{})
                phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='ambiguous')
                require(not any(r['observation']=='same-code-single-outstanding-flock-hold-interval' for r in phase['lock_observations']),'ambiguous fd inferred')
                require(phase['unmatched_observations']['ambiguous-lock-instance-hold']==2,'ambiguous holds not disclosed')
                checks.extend(['real own flock acquire/unlock envelopes and qualified hold interval','multiple descriptor ambiguity refuses inferred hold identity'])
            finally:os.close(a);os.close(b)
        barrier=threading.Barrier(3)
        def parallel():
            workers=[threading.Thread(target=F.threaded,args=(barrier,)) for _ in range(2)]
            for w in workers:w.start()
            barrier.wait()
            for w in workers:w.join()
        o.measure('parallel',parallel,lambda:{})
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='parallel')
        require(len({r['thread_id'] for r in phase['nested_code_timings'] if r['function']=='threaded'})==2,'thread attribution missing')
        require(sum(r['calls'] for r in phase['trusted_call_counts'] if r['function']=='nested')==16,'concurrent counts differ')
        checks.append('actual concurrent threads attributed separately without reading arguments')
        source=(HERE/'owned_observer_fixture.py').read_text().splitlines();a=next(i+1 for i,l in enumerate(source) if "bad='" in l);b=next(i+1 for i,l in enumerate(source) if 'application=leaf' in l)
        o.add_inline_span(F.inline.__code__,a,b,'security-owned-inline');o.measure('inline',F.inline,lambda:{})
        require(any(e['event']=='security-negative-inline-end' and e['failed'] is False for e in events),'inline scope missing')
        checks.append('selected unchanged inline negative line boundaries measured')
        # New selected code is loaded after observer starts, not pre-refreshed.
        new=load('_T35_owned_inert_later',HERE/'owned_observer_fixture.py');o.measure('later-import',new.nested,lambda:{})
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='later-import')
        require(any(r['function']=='nested' and r['calls']==1 for r in phase['trusted_call_counts']),'first new import call missed')
        checks.append('first call to newly imported selected code observed')
        late=compile('def unselected(): return 42\n',str(HERE/'unselected-owned.py'),'exec');ns={};exec(late,ns)
        o.measure('unselected',ns['unselected'],lambda:{})
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='unselected')
        require(not phase['trusted_call_counts'],'unselected source attributed')
        checks.append('unselected source excluded from trusted attribution')
        command=[str(I/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(I/'lib/abi'),str(I/'bin/python'),'-I','-B','-S','-c','sum(i*i for i in range(600000))']
        o.measure('child-reaped',lambda:subprocess.run(command,check=True,stdout=subprocess.DEVNULL),lambda:{})
        phase=next(e for e in events if e['event']=='phase-end' and e['phase']=='child-reaped')
        require(phase['reaped_children_user_CPU_seconds']+phase['reaped_children_system_CPU_seconds']>0,'reaped child CPU absent')
        require('running/unreaped' in phase['child_CPU_coverage'],'child coverage overclaimed')
        checks.append('real selected-interpreter reaped inert child CPU delta and coverage limits')
        require(o.callback_errors==0 and o.dropped==0 and o.dropped_lock_observations==0,'observer callback/overflow failure')
        require('PRIVATE-' not in json.dumps(events),'private fixture sentinel exposed')
        checks.append('all event fields omit fixture args/messages/return private values')
    finally:o.close()
    require(sys.monitoring.get_tool(tool) is None,'observer tool leaked');checks.append('owned observer closes local/global events and tool')
    # Failing emitter must preserve caller failure and restore phase.
    def emit_fail(v):raise OSError('PRIVATE-EMITTER-SENTINEL')
    bad=O.Observer(HERE,emit_fail,False,rows,C.read);bad.start()
    try:
        try:bad.measure('emit-failure',F.primary,lambda:{})
        except RuntimeError:pass
        else:raise AssertionError('emitter replaced primary')
        require(bad.phase is None and bad.callback_errors>0,'failed emitter phase leak')
    finally:bad.close()
    checks.append('failed diagnostic emitter preserves primary fault and cleans phase')
    # Pure fixed workload observed/unobserved costs are descriptive, not any
    # prediction/calibration of real protected runtime or empirical gate policy.
    overhead=[]
    for enabled in [False,True,False,True]:
        obs=O.Observer(HERE,lambda v:None,False,rows,C.read) if enabled else None
        if obs:obs.start()
        start=time.monotonic_ns();cpu=time.process_time_ns();thread=time.thread_time_ns()
        try:
            for _ in range(3):
                if obs:obs.measure('overhead-owned-fixed-workload',F.workload,lambda:{})
                else:F.workload()
        finally:
            elapsed=time.monotonic_ns()-start;CPU=time.process_time_ns()-cpu;threadCPU=time.thread_time_ns()-thread
            if obs:obs.close()
        overhead.append({'monitoring_enabled':enabled,'cProfile_enabled':False,'workload_invocations':3,'nested_invocations':750,'leaf_invocations':1500,'elapsed_ns':elapsed,'parent_CPU_ns':CPU,'thread_CPU_ns':threadCPU})
    checks.append('actual separate unobserved/observed own pure fixed workload overhead measured')
    require(entry_fds==len(list(Path('/proc/self/fd').iterdir())),'owned observer/capture FD leak');checks.append('all own capture/lock/observer descriptors closed')
    return {'result':'PASS-pure-observer-component','checks':checks,'checks_count':len(checks),'events':events,'overhead_experiment':overhead,
        'overhead_is_runtime_calibration':False,'software_source_rows':rows,'interpreter':sys.executable,
        'actual_Lab_constructors_or_leases':False,'original_callbacks_modified':False,'task_complete':False,'authority_effect':'none'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
