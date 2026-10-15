"""Trusted code event timings; never inspect args, locals, return or proof values."""
import ast,cProfile,fcntl,hashlib,os,resource,sys,threading,time,types
from collections import Counter
from pathlib import Path

class Observer:
    def __init__(self,root,emit,profiling=False,source_rows=None,source_reader=None):
        self.root=str(root)+'/';self.emit=emit;self.profiling=profiling;self.tool=None
        self.source_rows={} if source_rows is None else dict(source_rows);self.source_reader=source_reader
        self.phase=None;self.token=None;self.serial=0;self.counts=Counter();self.registered=set();self.exception_count=0
        self.dropped=0;self.callback_errors=0;self.metadata_errors=0;self.identities={};self.stacks={};self.timings={}
        self.unmatched=Counter();self.cross_phase=Counter();self.lock_sites={};self.c_pending={};self.held={};self.ambiguous_held=set();self.lock_samples=[]
        self.spans={};self.inline={};self.state_lock=threading.RLock();self.dropped_lock_observations=0
    def identity(self,code):
        if code in self.identities:return self.identities[code]
        path=code.co_filename
        if not path.startswith(self.root) or '/installations/' in path or '/deps/' in path or path==__file__:return None
        relative=path[len(self.root):];pin=self.source_rows.get(relative)
        if pin is None:return None
        value=(relative,code.co_qualname,code.co_firstlineno,pin,hashlib.sha256(code.co_code).hexdigest())
        self.identities[code]=value;return value
    def start(self):
        monitor=getattr(sys,'monitoring',None)
        if monitor is None:raise ValueError('selected interpreter lacks sys.monitoring')
        free=next((i for i in [5,4] if monitor.get_tool(i) is None),None)
        if free is None:raise ValueError('no free diagnostic tool id')
        self.tool=free
        try:
            monitor.use_tool_id(free,'cal-full-learning-measurement-v2')
            callbacks={monitor.events.PY_START:self.started,monitor.events.PY_RETURN:self.returned,
                       monitor.events.PY_UNWIND:self.unwound,monitor.events.PY_YIELD:self.yielded,monitor.events.PY_RESUME:self.resumed,
                       monitor.events.RAISE:self.raised,monitor.events.EXCEPTION_HANDLED:self.handled,
                       monitor.events.CALL:self.called,monitor.events.C_RETURN:self.c_returned,monitor.events.C_RAISE:self.c_raised,
                       monitor.events.LINE:self.line_event}
            for event,callback in callbacks.items():monitor.register_callback(free,event,callback)
            # New trusted imports within a phase get their first start observed.
            # Returning DISABLE suppresses this tool's unselected code locations;
            # no restart_events or other tool state is changed.
            monitor.set_events(free,monitor.events.PY_START|monitor.events.PY_UNWIND|monitor.events.RAISE|monitor.events.EXCEPTION_HANDLED)
        except BaseException:self.close();raise
    def _register(self,code):
        if code in self.registered:return
        identity=self.identity(code)
        if identity is None:return
        event=sys.monitoring.events;mask=event.PY_RETURN|event.PY_YIELD|event.PY_RESUME
        sites={}
        if self.source_reader is not None:
            raw=self.source_reader(Path(self.root+identity[0]),identity[3]);lines=raw.decode().splitlines()
            # Static selected public-source line classification only. No fd or
            # lock instance argument is inspected. Multiple operations per line
            # remain explicitly ambiguous.
            for _,_,line in code.co_lines():
                if line and line<=len(lines) and 'fcntl.flock(' in lines[line-1]:
                    text=lines[line-1];kind='unlock' if 'LOCK_UN' in text else 'acquire' if ('LOCK_EX' in text or 'LOCK_SH' in text) else 'unknown'
                    if 'LOCK_UN' in text and ('LOCK_EX' in text or 'LOCK_SH' in text):kind='unknown'
                    sites[line]=kind
        self.lock_sites[code]=sites
        if sites:mask|=event.CALL
        if code in self.spans:mask|=event.LINE
        sys.monitoring.set_local_events(self.tool,code,mask);self.registered.add(code)
    def started(self,code,offset):
        try:
            identity=self.identity(code)
            if identity is None:return sys.monitoring.DISABLE
            with self.state_lock:
                self._register(code);tid=threading.get_ident();self.counts[(identity,tid)]+=1
                self._push(code,tid,'start')
        except BaseException:self.callback_errors+=1
    def _push(self,code,tid,kind):
        self.stacks.setdefault(tid,[]).append([code,self.token,self.phase,time.monotonic_ns(),time.thread_time_ns(),0,0,kind])
    def resumed(self,code,offset):
        try:
            if self.identity(code) is None:return
            with self.state_lock:self._push(code,threading.get_ident(),'resume')
        except BaseException:self.callback_errors+=1
    def _end(self,code,kind):
        if self.identity(code) is None:return
        tid=threading.get_ident();now=time.monotonic_ns();cpu=time.thread_time_ns()
        with self.state_lock:
            stack=self.stacks.get(tid,[])
            if not stack or stack[-1][0] is not code:self.unmatched[(self.token,kind)]+=1;return
            item=stack.pop();wall=max(0,now-item[3]);CPU=max(0,cpu-item[4]);identity=self.identity(code)
            key=(item[1],identity,tid);row=self.timings.setdefault(key,Counter())
            row['segments']+=1;row['inclusive_elapsed_ns']+=wall;row['inclusive_thread_CPU_ns']+=CPU
            row['exclusive_elapsed_ns']+=max(0,wall-item[5]);row['exclusive_thread_CPU_ns']+=max(0,CPU-item[6]);row[kind]+=1
            if item[1]!=self.token:self.cross_phase[(item[1],self.token)]+=1
            if stack:stack[-1][5]+=wall;stack[-1][6]+=CPU
            if kind in {'unwind','return'} and (tid,code) in self.inline:self._inline_end(code,True)
    def returned(self,code,offset,retval):
        try:self._end(code,'return') # retval intentionally unused
        except BaseException:self.callback_errors+=1
    def yielded(self,code,offset,retval):
        try:self._end(code,'yield') # yielded values intentionally unused
        except BaseException:self.callback_errors+=1
    def unwound(self,code,offset,error):
        try:self._end(code,'unwind') # exception object ignored here
        except BaseException:self.callback_errors+=1
    def _location(self,code,offset):return next((line for start,end,line in code.co_lines() if start<=offset<end),None)
    def called(self,code,offset,callee,arg0):
        # arg0 may be private; never inspect/log/type/compare it.
        try:
            if callee is not fcntl.flock:return
            identity=self.identity(code)
            if identity is None:return
            line=self._location(code,offset);kind=self.lock_sites.get(code,{}).get(line,'unknown');tid=threading.get_ident()
            with self.state_lock:
                self.c_pending[(tid,code,offset)]=(time.monotonic_ns(),time.thread_time_ns(),self.token,self.phase,kind,line)
        except BaseException:self.callback_errors+=1
    def lock_sample(self,row):
        if len(self.lock_samples)<20000:self.lock_samples.append(row)
        else:self.dropped_lock_observations+=1
    def _c_end(self,code,offset,callee,failed):
        if callee is not fcntl.flock:return
        tid=threading.get_ident()
        with self.state_lock:
            item=self.c_pending.pop((tid,code,offset),None)
            if item is None:self.unmatched[(self.token,'flock-return-without-call')]+=1;return
            now=time.monotonic_ns();CPU=time.thread_time_ns();identity=self.identity(code)
            self.lock_sample({'phase_token':item[2],'phase':item[3],'identity':identity,'thread_id':tid,'line':item[5],
                'observation':'fcntl-flock-'+item[4]+'-call','elapsed_ns':now-item[0],'thread_CPU_ns':CPU-item[1],'failed':failed,
                'pure_kernel_wait_isolated':False,'lock_instance_args_observed':False})
            if item[4]=='unlock' and not failed:
                key=(tid,code);held=self.held.get(key,[])
                if len(held)==1 and key not in self.ambiguous_held:
                    acquired=held.pop();self.lock_sample({'phase_token':acquired[2],'phase':acquired[3],'identity':identity,'thread_id':tid,
                        'observation':'same-code-single-outstanding-flock-hold-interval','elapsed_ns':item[0]-acquired[0],
                        'lock_instance_args_observed':False,'coverage':'Acquire completion to successful unlock invocation; descriptor identity unobserved.'})
                elif held:self.unmatched[(self.token,'ambiguous-lock-instance-hold')]+=1;held.pop()
                else:self.unmatched[(self.token,'unlock-without-observed-same-code-acquire')]+=1
                if not held:self.ambiguous_held.discard(key)
            if item[4]=='acquire' and not failed:
                key=(tid,code);held=self.held.setdefault(key,[])
                if held:self.ambiguous_held.add(key)
                held.append((now,CPU,item[2],item[3]))
    def c_returned(self,code,offset,callee,arg0):
        try:self._c_end(code,offset,callee,False)
        except BaseException:self.callback_errors+=1
    def c_raised(self,code,offset,callee,arg0):
        try:self._c_end(code,offset,callee,True)
        except BaseException:self.callback_errors+=1
    def exception(self,event,code,offset,error):
        try:
            identity=self.identity(code)
            if identity is None:return
            self.exception_count+=1
            if self.exception_count>20000:self.dropped+=1;return
            frames=[];tb=error.__traceback__;outside=0
            while tb is not None:
                location=self.identity(tb.tb_frame.f_code)
                if location is not None:frames.append({'path':location[0],'function':location[1],'line':tb.tb_lineno})
                else:outside+=1
                tb=tb.tb_next
            self.safe_emit({'event':'trusted-exception','monitor_event':event,'phase':self.phase,'code_path':identity[0],'function':identity[1],
                'source_byte_sha256':identity[3],'instruction_bytes_sha256':identity[4],'line':self._location(code,offset),'instruction_offset':offset,
                'exception_class':type(error).__name__,'thread_id':threading.get_ident(),'sanitized_code_frames':frames,
                'outside_selected_repo_frames_omitted':outside,'exception_message_or_args_recorded':False,'frame_locals_inspected':False})
        except BaseException:self.callback_errors+=1
    def raised(self,code,offset,error):self.exception('raise',code,offset,error)
    def handled(self,code,offset,error):self.exception('handled',code,offset,error)
    def refresh(self):return None # global first-start handles later selected imports
    def safe_observation(self,metadata):
        try:return metadata()
        except BaseException as error:
            self.metadata_errors+=1;return {'diagnostic_metadata_unavailable':True,'exception_class':type(error).__name__}
    def safe_emit(self,value):
        try:self.emit(value)
        except BaseException:self.callback_errors+=1
    def children(self):
        value=resource.getrusage(resource.RUSAGE_CHILDREN)
        return value.ru_utime,value.ru_stime
    def rows(self,token):
        with self.state_lock:items=[(key,dict(counts)) for key,counts in self.timings.items()]
        result=[]
        for (phase,identity,tid),counts in items:
            if phase!=token:continue
            result.append({'path':identity[0],'function':identity[1].split('.')[-1],'qualname':identity[1],'line':identity[2],'source_byte_sha256':identity[3],
                          'instruction_bytes_sha256':identity[4],'thread_id':tid,**counts})
        return sorted(result,key=lambda row:(row['path'],row['line'],row['qualname'],row['thread_id']))
    def measure(self,label,callback,metadata):
        with self.state_lock:
            previous=self.phase;previous_token=self.token;self.serial+=1;token=self.serial;self.phase=label;self.token=token;before=self.counts.copy()
        start=time.monotonic();cpu=time.process_time();threadCPU=time.thread_time();children=self.children();failed=False
        self.safe_emit({'event':'phase-start','phase':label,'phase_token':token,'observation':self.safe_observation(metadata),
            'cProfile_enabled':self.profiling,'sys_monitoring_enabled':True})
        profiler=cProfile.Profile() if self.profiling else None
        try:
            if profiler is not None:profiler.enable()
            return callback()
        except BaseException:failed=True;raise
        finally:
            try:
                if profiler is not None:profiler.disable()
                elapsed=time.monotonic()-start;CPU=time.process_time()-cpu;thread_delta=time.thread_time()-threadCPU;after=self.children()
                with self.state_lock:
                    counted=list(self.counts.items());locks=[dict(r) for r in self.lock_samples if r['phase_token']==token]
                    unmatched={kind:count for (phase,kind),count in self.unmatched.items() if phase==token}
                    active=sum(item[1]==token for stack in self.stacks.values() for item in stack)
                    cross=sum(n for (began,ended),n in self.cross_phase.items() if began==token or ended==token)
                counts=[{'path':key[0][0],'function':key[0][1].split('.')[-1],'qualname':key[0][1],'line':key[0][2],
                    'source_byte_sha256':key[0][3],'instruction_bytes_sha256':key[0][4],'thread_id':key[1],'calls':count-before[key]}
                    for key,count in counted if count>before[key]]
                profile=[]
                if profiler is not None:
                    for entry in profiler.getstats():
                        identity=self.identity(entry.code) if isinstance(entry.code,types.CodeType) else None
                        if identity is not None:profile.append({'path':identity[0],'function':identity[1].split('.')[-1],'qualname':identity[1],'line':identity[2],
                            'calls':entry.callcount,'recursive_calls':entry.reccallcount,'inclusive_seconds':entry.totaltime,'exclusive_seconds':entry.inlinetime})
                self.safe_emit({'event':'phase-end','phase':label,'phase_token':token,'failed':failed,'elapsed_seconds':elapsed,
                    'parent_CPU_seconds':CPU,'measuring_thread_CPU_seconds':thread_delta,
                    'reaped_children_user_CPU_seconds':after[0]-children[0],'reaped_children_system_CPU_seconds':after[1]-children[1],
                    'child_CPU_coverage':'RUSAGE_CHILDREN delta charged for reaped descendants; running/unreaped children and unrelated processes unobserved; not exact execution-within-phase attribution.',
                    'trusted_call_counts':sorted(counts,key=lambda row:(row['path'],row['line'],row['qualname'])),
                    'nested_code_timings':self.rows(token),'lock_observations':locks,
                    'timing_coverage':'Active selected Python segments entered during this phase; elapsed includes waits/callback instrumentation; per-thread CPU excludes child CPU; exclusive subtracts selected nested segments only. Generator suspension excluded. First registration/source capture cost lies in phase envelope but before timed code push.',
                    'count_coverage':'First-start selected source-table repo code including later imports; stdlib/dependency/native child instructions excluded.',
                    'native_timing_coverage':'Selected Python native/schema wrappers inclusive of IPC/waits; child internal native instructions and per-child identity unavailable.',
                    'source_code_identity_claim':'Source pin plus observed instruction-byte hash only; no code constants/globals/args/values inspected; full source/callback security qualification remains separate.',
                    'unmatched_observations':unmatched,'active_selected_segments_at_phase_end':active,'cross_phase_segment_exits':cross,
                    'registered_code_objects':len(self.registered),'cProfile_enabled':self.profiling,'optional_profile_rows':profile,
                    'dropped_lock_observations':self.dropped_lock_observations,'observation':self.safe_observation(metadata)})
            except BaseException as error:
                self.metadata_errors+=1
                self.safe_emit({'event':'phase-bookkeeping-unavailable','phase':label,'phase_token':token,'exception_class':type(error).__name__,
                                'original_primary_failure_preserved':failed,'no_message_or_args':True})
            finally:
                with self.state_lock:self.phase=previous;self.token=previous_token
    def add_inline_span(self,code,start,end,label):
        if self.identity(code) is None:raise ValueError('inline span outside selected source')
        self.spans[code]=(start,end,label);self._register(code)
        if code in self.registered:
            current=sys.monitoring.get_local_events(self.tool,code);sys.monitoring.set_local_events(self.tool,code,current|sys.monitoring.events.LINE)
    def line_event(self,code,line):
        try:
            span=self.spans.get(code)
            if span is None:return
            key=(threading.get_ident(),code)
            if line==span[0] and key not in self.inline:
                self.inline[key]=(time.monotonic_ns(),time.thread_time_ns(),self.phase,self.token,span[2]);self.safe_emit({'event':'security-negative-inline-start','phase':span[2],'parent_phase':self.phase})
            if line==span[1] and key in self.inline:self._inline_end(code,False)
        except BaseException:self.callback_errors+=1
    def _inline_end(self,code,failed):
        item=self.inline.pop((threading.get_ident(),code),None)
        if item:self.safe_emit({'event':'security-negative-inline-end','phase':item[4],'parent_phase':item[2],'failed':failed,
            'elapsed_ns':time.monotonic_ns()-item[0],'thread_CPU_ns':time.thread_time_ns()-item[1],
            'coverage':'Exact selected unchanged security-helper line boundaries; no constructor args/body values observed.'})
    def close(self):
        if self.tool is None:return
        monitor=sys.monitoring;tool=self.tool;self.tool=None
        try:
            if monitor.get_tool(tool)!='cal-full-learning-measurement-v2':return
            try:monitor.set_events(tool,0)
            except BaseException:self.callback_errors+=1
            for code in self.registered:
                try:monitor.set_local_events(tool,code,0)
                except BaseException:self.callback_errors+=1
            for event in [monitor.events.PY_START,monitor.events.PY_RETURN,monitor.events.PY_UNWIND,monitor.events.PY_YIELD,monitor.events.PY_RESUME,
                          monitor.events.RAISE,monitor.events.EXCEPTION_HANDLED,monitor.events.CALL,monitor.events.C_RETURN,monitor.events.C_RAISE,monitor.events.LINE]:
                try:monitor.register_callback(tool,event,None)
                except BaseException:self.callback_errors+=1
        finally:
            if monitor.get_tool(tool)=='cal-full-learning-measurement-v2':monitor.free_tool_id(tool)
