"""Unique finalized owned runs; resumption always performs fresh qualification."""
from pathlib import Path
import json
import os
import re
import sys
import time
from ..p06.api import SupervisedQualifier
from ..p03.context import BASE,binding,check,require,C
from .generated_api import OwnedIssuance
from .runs import seal,inspect_record

HERE=Path(__file__).resolve().parent
class OwnedQualifier(SupervisedQualifier,OwnedIssuance):
    def __init__(self,run_root,policy,*,cgroup_parent=None,pids_max=None):
        require(Path(run_root).resolve().is_relative_to(HERE),'owned run root outside P07')
        super().__init__(run_root,policy,cgroup_parent=cgroup_parent,pids_max=pids_max)
        self.sources += [binding(HERE/name) for name in ['api.py','runs.py','cache.py','worker_context.py','qualification_worker.py','generated_api.py','generate_api.py','owner.schema.json','phase.schema.json','run-record.schema.json']]
        self.sources += [binding(BASE/'p06/task-acceptance.json')]
        self._resume=None;self._owned={}

    def worker_command(self):
        return [sys.executable,str(HERE/'qualification_worker.py')]+([json.dumps(self._resume)] if self._resume else [])

    def qualify(self,raw,*,cancel=None):
        started=time.monotonic()
        answer=OwnedIssuance.qualify(self,raw,cancel=cancel)
        run=answer['supervised_run']
        if run and 'job' in run:
            try:
                ref=seal(run['job'],answer);answer['owned_run']=ref
                if answer['qualified_result'] is not None:
                    require(cancel is None or not cancel.is_set(),'Cancelled during owned finalization.')
                    require(time.monotonic()-started<=self.supervisor.policy['run_seconds'],'Whole-run deadline exceeded during owned finalization.')
                    self._owned[answer['qualified_result']['run_id']]=ref
            except Exception as e:
                if answer['qualified_result'] is not None:
                    self._events.pop(answer['qualified_result']['run_id'],None)
                    job=Path(run['job']);os.chmod(job,0o700)
                    for name in ['result.json','completion.json']:
                        path=job/name
                        if path.exists():path.unlink()
                answer.update(status='cancelled' if str(e).startswith('Cancelled') else 'unknown-resource' if 'deadline' in str(e) else 'invalid',
                              qualified_result=None,claims=[],complete_closure=False,reason='Owned finalization refused: '+str(e)[:200])
        answer['schema']='relational.owned-qualification/v3'
        answer['seconds_including_owned_finalization']=time.monotonic()-started
        return answer

    def resume(self,phase_ref,raw,*,cancel=None):
        require(self._resume is None,'nested resume is unsupported')
        # This validates only the bounded selector. Phase/request/source/output
        # correlation is performed inside the supervised fixed worker.
        require(set(phase_ref)=={'path','sha256'},'invalid resume selector fields')
        require(isinstance(phase_ref['path'],str) and 0<len(phase_ref['path'])<=2048,'resume path selector byte ceiling')
        require(isinstance(phase_ref['sha256'],str) and re.fullmatch('[0-9a-f]{64}',phase_ref['sha256']) is not None,'invalid resume digest')
        self._resume=dict(phase_ref)
        try:return self.qualify(raw,cancel=cancel)
        finally:self._resume=None

    def live_event(self,result):
        if not super().live_event(result):return False
        ref=self._owned.get(result['run_id'])
        if not ref:return False
        try:return inspect_record(ref)['phase']=='completed'
        except Exception:return False
