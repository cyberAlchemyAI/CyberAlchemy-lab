"""Operator-fixed measurement client; submitted JSON cannot select instrumentation."""
import sys
from pathlib import Path
from ..p03.context import BASE,binding,require
from ..p07.api import OwnedQualifier
from ..p09.api import Client as PublicClient

HERE=Path(__file__).resolve().parent
class TimedQualifier(OwnedQualifier):
    def __init__(self,run_root,policy,**options):
        super().__init__(run_root,policy,**options)
        self.measurement_sources=[binding(HERE/name) for name in ['api.py','worker_context.py','qualification_worker.py','timing.py','performance-report.schema.json']]
        self.sources+=self.measurement_sources
    def worker_command(self):
        require(self._resume is None,'benchmark dispatch does not accept resume')
        return [sys.executable,str(HERE/'qualification_worker.py')]

class Client(PublicClient):
    def __init__(self,policy,run_root=None,*,cgroup_parent=None,pids_max=None):
        run_root=run_root or BASE/'p07/consumer-runs/P10'
        super().__init__(policy,run_root,cgroup_parent=cgroup_parent,pids_max=pids_max)
        original_sources=self.owned.sources
        self.owned=TimedQualifier(run_root,policy,cgroup_parent=cgroup_parent,pids_max=pids_max)
        self.owned.sources+=original_sources
        self.shadow.api=self.owned
        self.shadow._sources+=self.owned.measurement_sources;self.shadow.mapped.sources+=self.owned.measurement_sources
