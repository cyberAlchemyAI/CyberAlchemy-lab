"""Explicit owned technical fixture; never a governing authorization handle."""
import copy, datetime, hashlib, json, os, stat, time
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')

class TechnicalBoundaryRefusal(ValueError):
    pass

class OwnedTechnicalBoundary:
    """Real current byte/custody/time checks plus one declared fault checkpoint.

    This deliberately supplies only an owned technical test boundary. It cannot
    be passed off as a production Actor, Session, machine grant or owner route.
    No native executable, original callback, clock or guard is replaced.
    """
    def __init__(self,packet,packet_binding,capture,io):
        self.packet=copy.deepcopy(packet)
        self.binding=copy.deepcopy(packet_binding)
        self.capture=capture
        self.io=io
        self.raw=self.capture(ROOT/packet_binding['path'],packet_binding['sha256'])
        self.started=time.monotonic()
        self.fault=None
        self.acknowledged=False
        self.check_base()

    def check_base(self):
        if self.capture(ROOT/self.binding['path'],self.binding['sha256'])!=self.raw:
            raise ValueError('selected technical packet changed')
        now=datetime.datetime.now(datetime.timezone.utc)
        deadline=datetime.datetime.fromisoformat(self.packet['technical_deadline_utc'])
        if deadline.utcoffset()!=datetime.timedelta(0) or now>=deadline or time.monotonic()-self.started>=900:
            raise ValueError('technical fixture expired; no Session or grant revival')
        for row in self.packet['active_code_bindings']:
            self.capture(ROOT/row['path'],row['sha256'])
        for name in ('api_source_binding','api_profile_binding','root_dispatch_binding'):
            row=self.packet[name];self.capture(ROOT/row['path'],row['sha256'])
        for name in ('store_parent','output_root'):
            selected=self.packet[name]
            path=Path(selected['path'])
            if not path.is_absolute() or '..'in path.parts or path.is_relative_to(ROOT):
                raise ValueError('technical custody must be exact and outside repository')
            with self.io.directory(path)as fd:
                s=os.fstat(fd)
                if [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]!=selected['identity'] or s.st_uid!=os.getuid()or stat.S_IMODE(s.st_mode)!=0o700:
                    raise ValueError('independent technical custody changed')

    def guard(self):
        self.check_base()
        if self.fault is None or self.acknowledged:return
        head=self.capture(self.fault['head'])
        if hashlib.sha256(head).hexdigest()!=self.fault['before_sha256']:
            marker=Path(self.packet['output_root']['path'])/'postcommit-refusal-observed.json'
            if not marker.exists():
                self.io.write(marker,self.io.canonical({'authority_effect':'none',
                    'fault':'explicit-owned-postcommit-boundary-refusal',
                    'before_head_sha256':self.fault['before_sha256'],
                    'observed_head_sha256':hashlib.sha256(head).hexdigest()}))
            raise TechnicalBoundaryRefusal('declared owned postcommit boundary refusal; explicit acknowledgement required')

    def arm_after_head_transition(self,store_root):
        self.guard()
        root=Path(store_root)
        if self.fault is not None or root.name!='native'or root.parent.parent!=Path(self.packet['store_parent']['path']):
            raise ValueError('one exact owned native fault selection required')
        head=root/'HEAD.json'
        raw=self.capture(head)
        self.fault={'head':head,'before_sha256':hashlib.sha256(raw).hexdigest()}

    def acknowledge_retained_commit(self,control_binding):
        self.check_base()
        if self.fault is None or self.acknowledged:raise ValueError('one explicit observed fault acknowledgement required')
        marker=Path(self.packet['output_root']['path'])/'postcommit-refusal-observed.json'
        observed=json.loads(self.capture(marker))
        head=self.capture(self.fault['head'])
        if observed['observed_head_sha256']!=hashlib.sha256(head).hexdigest()or observed['before_head_sha256']!=self.fault['before_sha256']:
            raise ValueError('retained postcommit generation changed')
        control=Path(control_binding['path'])
        if control.parent!=self.fault['head'].parent.parent:
            raise ValueError('selected recovery control outside exact failed store')
        self.capture(control,control_binding['sha256'])
        self.acknowledged=True
        self.guard()
