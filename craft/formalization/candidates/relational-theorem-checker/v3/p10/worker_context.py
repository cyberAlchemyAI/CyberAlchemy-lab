"""Timing only: every operation delegates to the unchanged accepted P07 context."""
from ..p07.worker_context import WorkerContext as OwnedContext
from .timing import tool_name

class WorkerContext(OwnedContext):
    def __init__(self,job,policy,layout,trace):
        self.trace=trace
        with self.trace.span('context:construction'):super().__init__(job,policy,layout)
    def run_tool(self,args,**kwargs):
        with self.trace.span(tool_name(args)):return super().run_tool(args,**kwargs)
    def assert_current(self):
        with self.trace.span('context:source-and-cache-current'):return super().assert_current()
    def boundary(self,*args,**kwargs):
        with self.trace.span('context:normalization-projection'):return super().boundary(*args,**kwargs)
    def prepare(self,*args,**kwargs):
        with self.trace.span('context:dependency-preparation'):return super().prepare(*args,**kwargs)
    def compile_default(self,build,modules):
        with self.trace.span('context:compile:'+modules[0][0]):return super().compile_default(build,modules)
    def evaluate(self,*args,**kwargs):
        with self.trace.span('context:reference-evaluator'):return super().evaluate(*args,**kwargs)
    def inspect(self,*args,**kwargs):
        with self.trace.span('context:exact-evidence-inspection'):return super().inspect(*args,**kwargs)
