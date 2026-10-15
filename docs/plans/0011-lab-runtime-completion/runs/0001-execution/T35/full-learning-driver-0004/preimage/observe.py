"""Code identity/count and sanitized exception monitoring; no frame/local inspection."""
import cProfile,os,sys,threading,time,types
from collections import Counter
from pathlib import Path

class Observer:
    def __init__(self,root,emit,profiling=False):
        self.root=str(root)+'/';self.emit=emit;self.profiling=profiling;self.tool=None
        self.phase=None;self.counts=Counter();self.registered=set();self.exception_count=0
        self.dropped=0;self.callback_errors=0;self.metadata_errors=0
    def identity(self,code):
        path=code.co_filename
        if not path.startswith(self.root) or '/installations/' in path or '/deps/' in path:return None
        return (path[len(self.root):],code.co_name,code.co_firstlineno)
    def start(self):
        monitor=getattr(sys,'monitoring',None)
        if monitor is None:raise ValueError('selected interpreter lacks sys.monitoring')
        free=next((i for i in [5,4] if monitor.get_tool(i) is None),None)
        if free is None:raise ValueError('no free diagnostic monitoring tool id')
        self.tool=free
        try:
            monitor.use_tool_id(free,'cal-full-learning-qualification')
            monitor.register_callback(free,monitor.events.PY_START,self.started)
            monitor.register_callback(free,monitor.events.RAISE,self.raised)
            monitor.register_callback(free,monitor.events.EXCEPTION_HANDLED,self.handled)
            monitor.set_events(free,monitor.events.RAISE|monitor.events.EXCEPTION_HANDLED)
        except BaseException:
            self.close()
            raise
    def started(self,code,offset):
        try:
            identity=self.identity(code)
            if identity is not None:self.counts[(identity,threading.get_ident())]+=1
        except BaseException:self.callback_errors+=1
    def exception(self,event,code,offset,error):
        try:
            identity=self.identity(code)
            if identity is None:return
            self.exception_count+=1
            if self.exception_count>20000:self.dropped+=1;return
            line=next((line for start,end,line in code.co_lines() if start<=offset<end),None)
            frames=[];tb=error.__traceback__;outside=0
            while tb is not None:
                location=self.identity(tb.tb_frame.f_code)
                if location is not None:frames.append({'path':location[0],'function':location[1],'line':tb.tb_lineno})
                else:outside+=1
                tb=tb.tb_next
            self.emit({'event':'trusted-exception','monitor_event':event,'phase':self.phase,
                'code_path':identity[0],'function':identity[1],'line':line,'instruction_offset':offset,
                'exception_class':type(error).__name__,'thread_id':threading.get_ident(),
                'sanitized_code_frames':frames,'outside_selected_repo_frames_omitted':outside,
                'exception_message_or_args_recorded':False,'frame_locals_inspected':False})
        except BaseException:self.callback_errors+=1
    def raised(self,code,offset,error):self.exception('raise',code,offset,error)
    def handled(self,code,offset,error):self.exception('handled',code,offset,error)
    def refresh(self):
        # Local PY_START avoids counting every interpreter/library call. Register
        # selected repo code currently imported; later phase refresh catches new
        # source/provider/Service methods. No function is wrapped or assigned.
        def add(code):
            if code in self.registered or self.identity(code) is None:return
            self.registered.add(code);sys.monitoring.set_local_events(self.tool,code,sys.monitoring.events.PY_START)
            for child in code.co_consts:
                if isinstance(child,types.CodeType):add(child)
        for module in list(sys.modules.values()):
            namespace=getattr(module,'__dict__',{})
            path=namespace.get('__file__')
            if not isinstance(path,str) or not path.startswith(self.root) or '/installations/' in path or '/deps/' in path:continue
            for value in list(namespace.values()):
                if isinstance(value,types.FunctionType):add(value.__code__)
                elif isinstance(value,type):
                    for member in list(vars(value).values()):
                        if isinstance(member,(staticmethod,classmethod)):member=member.__func__
                        if isinstance(member,types.FunctionType):add(member.__code__)
                        elif isinstance(member,property):
                            for function in [member.fget,member.fset,member.fdel]:
                                if function is not None:add(function.__code__)
    def safe_observation(self,metadata):
        try:return metadata()
        except BaseException as error:
            self.metadata_errors+=1
            return {'diagnostic_metadata_unavailable':True,'exception_class':type(error).__name__}
    def safe_emit(self,value):
        try:self.emit(value)
        except BaseException:self.callback_errors+=1
    def measure(self,label,callback,metadata):
        self.refresh();previous=self.phase;self.phase=label
        before=self.counts.copy();start=time.monotonic();cpu=time.process_time();failed=False
        self.safe_emit({'event':'phase-start','phase':label,'observation':self.safe_observation(metadata),
            'cProfile_enabled':self.profiling,'sys_monitoring_enabled':True})
        profiler=cProfile.Profile() if self.profiling else None
        if profiler is not None:profiler.enable()
        try:return callback()
        except BaseException:failed=True;raise
        finally:
            if profiler is not None:profiler.disable()
            elapsed=time.monotonic()-start;CPU=time.process_time()-cpu
            rows=[{'path':key[0][0],'function':key[0][1],'line':key[0][2],'thread_id':key[1],'calls':count-before[key]}
                  for key,count in self.counts.items() if count>before[key]]
            profile=[]
            if profiler is not None:
                for entry in profiler.getstats():
                    identity=self.identity(entry.code) if isinstance(entry.code,types.CodeType) else None
                    if identity is not None:profile.append({'path':identity[0],'function':identity[1],'line':identity[2],
                        'calls':entry.callcount,'recursive_calls':entry.reccallcount,
                        'inclusive_seconds':entry.totaltime,'exclusive_seconds':entry.inlinetime})
            self.safe_emit({'event':'phase-end','phase':label,'failed':failed,'elapsed_seconds':elapsed,'parent_CPU_seconds':CPU,
                'trusted_call_counts':sorted(rows,key=lambda row:(row['path'],row['line'],row['function'])),
                'count_coverage':'Currently imported selected repo functions/classes and nested code; refreshed each phase; no native child or stdlib counts.',
                'registered_code_objects':len(self.registered),'cProfile_enabled':self.profiling,
                'optional_profile_rows':profile,'observation':self.safe_observation(metadata)})
            self.phase=previous
    def close(self):
        if self.tool is None:return
        monitor=sys.monitoring;tool=self.tool;self.tool=None
        try:
            if monitor.get_tool(tool)!='cal-full-learning-qualification':return
            try:monitor.set_events(tool,0)
            except BaseException:self.callback_errors+=1
            for code in self.registered:
                try:monitor.set_local_events(tool,code,0)
                except BaseException:self.callback_errors+=1
            for event in [monitor.events.PY_START,monitor.events.RAISE,monitor.events.EXCEPTION_HANDLED]:
                try:monitor.register_callback(tool,event,None)
                except BaseException:self.callback_errors+=1
        finally:
            if monitor.get_tool(tool)=='cal-full-learning-qualification':monitor.free_tool_id(tool)
