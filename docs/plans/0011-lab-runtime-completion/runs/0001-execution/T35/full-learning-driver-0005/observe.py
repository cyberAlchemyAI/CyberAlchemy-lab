"""Explicit phase-only observation: no function, exception, line or lock hooks.

A selected sys.monitoring tool name may be reserved for the existing runtime
instrumentation contract. Reservation is not event collection. No original
callback, clock, args, frame locals, return values or proofs are inspected.
"""
import resource
import sys
import threading
import time

MEASUREMENT_FIELDS={'schema_version','collection_mode','monitoring_reservation','cProfile_enabled','authority_effect'}
TOOL_NAME='cal-full-learning-measurement-v2'


def need(value,message):
    if not value:raise ValueError(message)


def measurement_check(value):
    need(type(value) is dict and set(value)==MEASUREMENT_FIELDS,'closed independent measurement selection required')
    need(value['schema_version']=='lab-full-learning-measurement-selection/v1-candidate'
         and value['collection_mode']=='phase-only' and value['cProfile_enabled'] is False
         and value['authority_effect']=='none','explicit phase-only unprofiled selection required')
    reservation=value['monitoring_reservation']
    need(type(reservation) is dict and set(reservation)=={'tool_id','tool_name'}
         and type(reservation['tool_id']) is int and reservation['tool_id'] in [4,5]
         and reservation['tool_name']==TOOL_NAME,'independent exact tool reservation required')
    return value


class Observer:
    def __init__(self,root,emit,profiling=False,source_rows=None,source_reader=None,*,measurement=None):
        selected=measurement_check(measurement)
        need(profiling is False,'phase-only cannot enable cProfile')
        self.emit=emit;self.profiling=False;self.tool=None
        self.expected_tool=selected['monitoring_reservation']['tool_id']
        self.serial=0;self.lock=threading.RLock();self.metadata_errors=0;self.bookkeeping_errors=0
        # Null means deliberately uncollected. It must never become a zero-count
        # completeness claim. Source rows/reader are not cached or traversed.
        self.callback_errors=None;self.dropped=None;self.dropped_lock_observations=None
    def coverage(self):
        return {'collection_mode':'phase-only','cProfile_enabled':False,
            'monitoring_reservation':{'tool_id':self.expected_tool,'tool_name':TOOL_NAME,'active':self.tool is not None},
            'sys_monitoring_event_collection_enabled':False,'monitoring_callbacks_registered_by_this_observer':False,
            'function_counts_collected':False,'nested_function_timings_collected':False,
            'handled_or_swallowed_exception_events_collected':False,'lock_acquire_wait_hold_events_collected':False,
            'inline_security_negative_event_timings_collected':False,
            'escaping_failure_coverage':'Phase failure flag/class and unchanged driver outer exception code frames only; swallowed inner faults unavailable.',
            'event_state_coverage':'Own selected tool global event mask checked at phase boundaries; this observer registers no local events. Foreign per-code local masks are not enumerated.',
            'observer_overhead_calibrated_for_runtime':False}
    def check(self):
        need(self.tool==self.expected_tool and sys.monitoring.get_tool(self.tool)==TOOL_NAME,'owned selected reservation changed')
        need(sys.monitoring.get_events(self.tool)==0,'phase-only global event collection unexpectedly enabled')
        need(sys.getprofile() is None and sys.gettrace() is None,'phase-only requires independently selected absent profile/trace hooks')
    def start(self):
        monitor=getattr(sys,'monitoring',None)
        need(monitor is not None,'selected interpreter lacks sys.monitoring')
        need(self.tool is None and monitor.get_tool(self.expected_tool) is None,'selected reservation unavailable; no alternate tool fallback')
        monitor.use_tool_id(self.expected_tool,TOOL_NAME);self.tool=self.expected_tool
        try:self.check()
        except BaseException:self.close();raise
    def safe_emit(self,value):
        try:self.emit(value)
        except BaseException:self.bookkeeping_errors+=1
    def safe_observation(self,metadata):
        try:return metadata()
        except BaseException as error:
            self.metadata_errors+=1
            return {'diagnostic_metadata_unavailable':True,'exception_class':type(error).__name__}
    def children(self):
        value=resource.getrusage(resource.RUSAGE_CHILDREN)
        return value.ru_utime,value.ru_stime
    def measure(self,label,callback,metadata):
        self.check()
        with self.lock:self.serial+=1;token=self.serial
        start=time.monotonic();cpu=time.process_time();threadCPU=time.thread_time();children=self.children()
        failed=False;exception_class=None
        self.safe_emit({'event':'phase-start','phase':label,'phase_token':token,
            'observation':self.safe_observation(metadata),'measurement_coverage':self.coverage()})
        try:return callback()
        except BaseException as error:
            failed=True;exception_class=type(error).__name__;raise
        finally:
            try:
                elapsed=time.monotonic()-start;CPU=time.process_time()-cpu;thread_delta=time.thread_time()-threadCPU;after=self.children()
                self.check()
                self.safe_emit({'event':'phase-end','phase':label,'phase_token':token,'failed':failed,'escaping_exception_class':exception_class,
                    'elapsed_seconds':elapsed,'parent_CPU_seconds':CPU,'measuring_thread_CPU_seconds':thread_delta,
                    'reaped_children_user_CPU_seconds':after[0]-children[0],'reaped_children_system_CPU_seconds':after[1]-children[1],
                    'child_CPU_coverage':'RUSAGE_CHILDREN delta charged for reaped descendants; running/unreaped children and unrelated processes unobserved; not exact execution-within-phase attribution.',
                    'phase_timing_coverage':'Real monotonic wall/process CPU/measuring-thread CPU envelope; includes phase-start metadata/trace work and all nested calls, waits and instrumentation remaining in the callback. End metadata/trace work follows the sampled endpoint. Nested phase envelopes overlap and must not be summed.',
                    'trusted_call_counts':None,'nested_code_timings':None,'lock_observations':None,'optional_profile_rows':None,
                    'unmatched_observations':None,'registered_code_objects':None,'dropped_lock_observations':None,
                    'measurement_coverage':self.coverage(),'observation':self.safe_observation(metadata)})
            except BaseException as error:
                self.bookkeeping_errors+=1
                self.safe_emit({'event':'phase-bookkeeping-unavailable','phase':label,'phase_token':token,
                    'exception_class':type(error).__name__,'original_primary_failure_preserved':failed,'no_message_or_args':True})
    def add_inline_span(self,code,start,end,label):
        # Preserve the unchanged security helper invocation and all its checks.
        # No code registration, line hook or private inspection is performed.
        self.safe_emit({'event':'inline-observation-uncollected','requested_label':label,
            'reason':'Explicit phase-only collection; actual foreign-attachment negative still executes inside the full unchanged lifecycle phase.'})
        return False
    def close(self):
        if self.tool is None:return
        tool=self.tool;self.tool=None
        need(sys.monitoring.get_tool(tool)==TOOL_NAME,'refuse to free unselected replacement reservation')
        sys.monitoring.free_tool_id(tool)
