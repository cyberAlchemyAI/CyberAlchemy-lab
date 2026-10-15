"""Retained supervised mathematics with independently anchored imports and phases."""
from ..p06.worker_context import WorkerContext as SupervisedContext
from ..p03.context import C,BASE,read,check,require,write
from .cache import CacheAnchor
from .runs import record_phase

class WorkerContext(SupervisedContext):
    def __init__(self,job,policy,layout):
        self.cache_check=None
        super().__init__(job,policy)
        for predecessor in ['P05','P06']:
            receipt=read(BASE/(predecessor.lower()+'/task-acceptance.json'))
            require(receipt['result']=='accepted',predecessor+' is not accepted')
            for ref in receipt['artifacts']+receipt['inputs']:check(ref)
            self.trusted += receipt['artifacts']+receipt['inputs']
        self.cache=CacheAnchor(layout);self.trusted += self.cache.references
        self.cache_check=self.cache.verify();self.assert_current()

    def assert_current(self):
        super().assert_current()
        if hasattr(self,'cache'):self.cache.verify()

    def allocate(self,request):
        path=super().allocate(request)
        record_phase(self.job,'request-accepted',request_identity=C.identity(request),cache_check=self.cache_check)
        return path

    def prepare(self,build,info,mode):
        self.cache_check=self.cache.verify()
        require([m['source'] for m in self.cache.metadata['modules']]==info['runtime_sources'],'anchored cache and source projection disagree')
        write(build/'cache-check.json',self.cache_check)
        result=super().prepare(build,info,mode)
        record_phase(self.job,'dependencies-prepared',cache_check=self.cache_check)
        return result

    def compile_default(self,build,modules):
        result=super().compile_default(build,modules)
        record_phase(self.job,'compiled-'+modules[-1][0],cache_check=self.cache_check)
        return result

    def inspect(self,request,result):
        checked=super().inspect(request,result)
        record_phase(self.job,'exact-proof-inspected',request_identity=C.identity(request),cache_check=self.cache_check)
        return checked
