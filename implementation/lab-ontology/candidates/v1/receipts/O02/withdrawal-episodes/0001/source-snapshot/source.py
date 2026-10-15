"""Exact Work-only disposable source scope and independently replayed cuts.

The existing C11 admit-only provisioner is unchanged. This scope explicitly
permits two local fixture effects and cannot select an existing store.
"""
import base64
import copy
from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from translation import *

RUNTIME = ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
sys.path.insert(0, str(RUNTIME))
from lab_runtime.common import digest, encoded
from lab_runtime.replay import ReplayPins, legacy_runtime, full_replay

BINDINGS = 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json'
MANIFEST_SHA = '064217cb94e0a97654052338bf8338bb437f3a6311e71061caa2343760d95abe'
HERE = Path(__file__).resolve().parent
WORK = HERE/'work.json'
REF = 'work:lab-O02:source-withdrawal@candidate.1'
STORE_ID = 'o02-source-withdrawal-fixture'
OPERATOR = 'role:candidate-o02-source-withdrawal'
SCOPE = 'scope:lab-runtime-local:'+STORE_ID
_CUT_FACTORY = object()


@dataclass(frozen=True)
class WithdrawalScope:
    store_id: str = STORE_ID
    operator_ref: str = OPERATOR
    scope_ref: str = SCOPE
    version_ref: str = REF
    carrier_ref: str = 'cal.artifact-type.work/v1'
    allowed_categories: tuple = ('artifact-instance',)
    allowed_effects: tuple = ('admit', 'withdraw')
    candidate_only: bool = True

    def check(self):
        require(asdict(self)==asdict(WithdrawalScope()), 'unselected Work-only fixture scope')

    def target(self, operation, record):
        self.check()
        require(operation in self.allowed_effects, 'undeclared fixture effect')
        if operation=='admit':
            require(record==parse(WORK.read_bytes()) and record['kind']=='work'
                and record['scope_ref']==self.scope_ref, 'exact controlled Work required')
        else:
            require(record is None, 'withdrawal cannot carry a new record')
        return {'category':'artifact-instance','operation':operation,'version_ref':self.version_ref,
            'carrier_ref':self.carrier_ref,'record':copy.deepcopy(record),
            'predecessor_ref':self.version_ref if operation=='withdraw' else None,
            'decision_ref':'decision:O02:controlled-source-'+operation+'@candidate.1','contract':None}


def closure(path, sequence):
    require(type(sequence) is int and sequence in (0,1,2), 'fixture cut outside declared history')
    paths = ['config.json','baseline.json','HEAD.json']+[
        f'transactions/{i:010d}.json' for i in range(sequence+1)]
    require(not path.is_symlink() and path.is_dir(), 'source root unavailable or symlink')
    require({p.name for p in path.iterdir()} <= {'config.json','baseline.json','HEAD.json','transactions','.writer.lock'},
        'undeclared source root entry')
    require(not (path/'transactions').is_symlink(), 'source transactions symlink')
    require({p.name for p in (path/'transactions').iterdir()}=={Path(p).name for p in paths if p.startswith('transactions/')},
        'source committed transaction closure differs')
    for name in paths:
        require((path/name).is_file() and not (path/name).is_symlink(), 'source original entry unavailable or symlink')
    return {name:sha((path/name).read_bytes()) for name in paths}


class VerifiedSourceCut:
    def __init__(self, path, pins, data, scope, token):
        require(token is _CUT_FACTORY, 'caller metadata is not verified source replay')
        self.path = Path(path);self.pins=copy.deepcopy(pins);self.scope=scope
        self.data=copy.deepcopy(data);self.data_sha=object_sha(self.data)
        self.expected=closure(self.path,self.data['head']['sequence'])
        self.pin_sha=object_sha(asdict(self.pins));self.closed=False

    def guard(self):
        require(not self.closed, 'source cut closed')
        self.scope.check()
        require(object_sha(self.data)==self.data_sha and object_sha(asdict(self.pins))==self.pin_sha,
            'verified source replay or external pins changed')
        require(closure(self.path,self.data['head']['sequence'])==self.expected, 'source original cut bytes changed')
        require(sha((ROOT/BINDINGS).read_bytes())==MANIFEST_SHA, 'source runtime binding changed')

    def effect(self):
        self.guard();data=self.data;scope=self.scope
        sequence=data['head']['sequence']
        require(sequence in (1,2), 'no signed controlled Work effect in genesis')
        operation='admit' if sequence==1 else 'withdraw'
        target=data['transactions'][sequence]['proposal']['targets'][0]
        require(data['transactions'][sequence]['proposal']['targets']==[scope.target(operation,
            parse(WORK.read_bytes()) if operation=='admit' else None)], 'signed fixture effect differs from exact selection')
        subject=data['projection']['subjects'][scope.version_ref]
        require(subject['record']==parse(WORK.read_bytes()) and subject['kind']=='work'
            and subject['identity']=='work:lab-O02:source-withdrawal'
            and subject['carrier_ref']==scope.carrier_ref, 'signed source revision/body/carrier mismatch')
        record_sha=sha(encoded(subject['record']))
        require(record_sha==sha(WORK.read_bytes()), 'original controlled Work encoding differs')
        admission=data['transactions'][1]
        require(admission['proposal']['targets']==[scope.target('admit',subject['record'])], 'original source admission differs')
        require(subject['effective_state']==('local-admitted-current' if sequence==1 else 'local-withdrawn'),
            'signed source posture differs')
        tx=data['transactions'][sequence]
        return {'source_store_id':scope.store_id,'source_scope_ref':scope.scope_ref,'source_operator_ref':scope.operator_ref,
            'source_version_ref':scope.version_ref,'source_identity_ref':subject['identity'],'source_kind':'work',
            'carrier_ref':scope.carrier_ref,'record_binding':bind(WORK),'record_sha256':record_sha,
            'record_selector':'/proposal/targets/0/record','record_transaction_sha256':self.expected['transactions/0000000001.json'],
            'source_effect':operation,'source_posture':subject['effective_state'],'source_eligible':operation=='admit',
            'effect_transaction_sha256':self.expected[f'transactions/{sequence:010d}.json'],
            'effect_transaction_digest':tx['digest'],'source_head':data['head']['transaction_digest'],
            'source_sequence':sequence,'config_sha256':self.pins.config_sha256,
            'baseline_snapshot_digest':self.pins.baseline_snapshot_digest,
            'project_histories':{k:{'identity_ref':v['node_id'],'cursor':len(v['payload']['events']),
                'chain_digest':v['payload']['chain_digest']} for k,v in data['projection']['histories'].items()},
            'source_admission_is_repository_admission':False,'authority_effect':'none','actual_owner_outcome':None}


def replay_cut(path, pins, scope):
    require(type(scope) is WithdrawalScope, 'explicit Work-only scope required');scope.check()
    require(type(pins) is ReplayPins and pins.runtime_version=='v2' and pins.manifest_path==BINDINGS
        and pins.manifest_sha256==MANIFEST_SHA and pins.expected_head is not None, 'independent exact runtime and HEAD pins required')
    path=Path(path)
    head=parse((path/'HEAD.json').read_bytes());before=closure(path,head['sequence'])
    data=full_replay(path,ROOT,ROOT,pins,require_current=True)
    config=data['config']
    require(config['store_id']==scope.store_id and config['owner_ref']==scope.operator_ref
        and config['scope_ref']==scope.scope_ref and config['allowed_categories']==list(scope.allowed_categories)
        and config['allowed_effects']==list(scope.allowed_effects), 'source provisioned scope differs')
    require(before==closure(path,head['sequence']), 'source original closure changed during replay')
    cut=VerifiedSourceCut(path,pins,data,scope,_CUT_FACTORY)
    if head['sequence']:cut.effect()
    return cut


class SourceFixture:
    def __init__(self, scope):
        require(type(scope) is WithdrawalScope, 'explicit isolated withdrawal scope required');scope.check()
        self.scope=scope;self.work_binding=bind(WORK);self.closed=False;self.expires=time.monotonic()+900
        self.owned=tempfile.TemporaryDirectory(prefix='cal-O02-controlled-source-')
        self.root=Path(self.owned.name);self.path=self.root/'project';self.key=self.root/'fixture-only.pem'
        require(not self.root.is_relative_to(ROOT), 'source fixture must be outside repository')
        pins=ReplayPins('v2',BINDINGS,MANIFEST_SHA,'','')
        self.module,self.engine,self.stage=legacy_runtime(ROOT,pins)
        self.snapshots={};self.closed_cuts=[];self.expected={}
        try:
            pub=self.root/'fixture-only.pub';self.engine.keygen(self.key,pub)
            self.store=self.engine.Store(self.path,ROOT)
            self.store.initialize(parse((Path(self.stage.name)/'profile.json').read_bytes()),scope.store_id,
                scope.operator_ref,pub.read_text().strip(),list(scope.allowed_categories),list(scope.allowed_effects))
            require(self.key.stat().st_mode & 0o777==0o600 and not self.key.is_relative_to(self.path), 'fixture key custody differs')
            self.update_pins();replay_cut(self.path,self.pins,scope)
        except BaseException:self.close();raise

    def update_pins(self):
        head=parse((self.path/'HEAD.json').read_bytes());baseline=parse((self.path/'baseline.json').read_bytes())
        self.pins=ReplayPins('v2',BINDINGS,MANIFEST_SHA,sha((self.path/'config.json').read_bytes()),
            baseline['snapshot_digest'],head['transaction_digest'])
        self.expected=closure(self.path,head['sequence'])

    def guard(self):
        require(not self.closed and time.monotonic()<self.expires, 'source fixture closed or expired')
        self.scope.check();original(self.work_binding)
        require(self.expected==closure(self.path,parse((self.path/'HEAD.json').read_bytes())['sequence']), 'owned committed bytes changed')

    def proposal(self, operation):
        self.guard();config=parse((self.path/'config.json').read_bytes())
        return {'schema_version':'lab-runtime-proposal/v1','proposal_id':'O02-controlled-source-'+operation,
            'expected_head':self.pins.expected_head,'source_snapshot_digest':config['source_snapshot_digest'],
            'scope_ref':config['scope_ref'],'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],
            'schemas':{},'targets':[self.scope.target(operation,parse(WORK.read_bytes()) if operation=='admit' else None)]}

    def commit(self, operation):
        self.guard();proposal=self.proposal(operation)
        expected_sequence=0 if operation=='admit' else 1
        require(parse((self.path/'HEAD.json').read_bytes())['sequence']==expected_sequence, 'out-of-order fixture effect')
        review=self.store.review(proposal);approval=self.store.authorize(proposal,self.key)
        result=self.store.apply(proposal,approval)
        require(result['idempotent'] is False, 'new source effect unexpectedly repeated')
        before=copy.deepcopy(self.expected);self.update_pins()
        require(all(self.expected[p]==v for p,v in before.items() if p!='HEAD.json'), 'signed effect rewrote original committed bytes')
        data=replay_cut(self.path,self.pins,self.scope)
        sequence=data.data['head']['sequence'];snap=self.root/f'cut-{sequence}';snap.mkdir();(snap/'transactions').mkdir()
        for name in self.expected:shutil.copyfile(self.path/name,snap/name)
        cut=replay_cut(snap,self.pins,self.scope);self.closed_cuts.append(cut)
        self.snapshots[operation]={'pins':asdict(self.pins),'head_original_bytes':base64.b64encode((snap/'HEAD.json').read_bytes()).decode(),
            'projection_sha256':object_sha(cut.data['projection']),'effect':cut.effect()}
        return cut,{'proposal':proposal,'approval':approval,'review':review,'result':result}

    def retry(self, committed):
        self.guard();before=copy.deepcopy(self.expected)
        result=self.store.apply(committed['proposal'],committed['approval'])
        require(result['idempotent'] is True and closure(self.path,2)==before, 'source retry appended or rewrote committed bytes')
        return result

    def export(self):
        self.guard();require(set(self.snapshots)=={'admit','withdraw'}, 'both actual source effects required')
        return {'schema_version':'lab-O02-controlled-source-archive/v1-candidate','authority_effect':'none',
            'actual_owner_outcome':None,'scope':asdict(self.scope),'cuts':copy.deepcopy(self.snapshots),
            'files':{name:{'sha256':v,'base64_original_bytes':base64.b64encode((self.path/name).read_bytes()).decode()}
                for name,v in self.expected.items()},'private_key_included':False,'Session_memory_included':False,
            'repository_admissions_applied':0,'actual_local_fixture_effects':2}

    def close(self):
        if self.closed:return
        self.closed=True
        for cut in getattr(self,'closed_cuts',[]):cut.closed=True
        if hasattr(self,'stage'):self.stage.cleanup()
        if hasattr(self,'module'):
            for name in list(sys.modules):
                if name==self.module or name.startswith(self.module+'.'):sys.modules.pop(name,None)
        self.owned.cleanup()


def restore_cut(archive, operation, destination, independent_pins):
    """Archive SHA and pins are supplied independently by its bound witness."""
    require(operation in ('admit','withdraw') and not destination.exists(), 'new selected cut destination required')
    require(archive['authority_effect']=='none' and archive['actual_owner_outcome'] is None
        and archive['private_key_included'] is False and archive['Session_memory_included'] is False
        and archive['repository_admissions_applied']==0, 'public source archive authority/custody differs')
    scope=WithdrawalScope();scope.check()
    expected_scope=json.loads(json.dumps(asdict(scope)))
    require(archive['scope']==expected_scope and set(archive['cuts'])=={'admit','withdraw'}, 'source archive scope/cuts differ')
    require(archive['cuts'][operation]['pins']==asdict(independent_pins), 'source archive differs from independent replay pins')
    require(set(archive['files'])=={'config.json','baseline.json','HEAD.json',
        'transactions/0000000000.json','transactions/0000000001.json','transactions/0000000002.json'}, 'public source archive closure differs')
    destination.mkdir(mode=0o700);(destination/'transactions').mkdir()
    sequence=1 if operation=='admit' else 2
    for name,row in archive['files'].items():
        raw=base64.b64decode(row['base64_original_bytes'],validate=True)
        require(sha(raw)==row['sha256'], 'source archive original byte digest mismatch')
        if name=='transactions/0000000002.json' and sequence==1:continue
        if name=='HEAD.json':raw=base64.b64decode(archive['cuts'][operation]['head_original_bytes'],validate=True)
        with (destination/name).open('xb') as stream:stream.write(raw)
    cut=replay_cut(destination,independent_pins,scope)
    require(object_sha(cut.data['projection'])==archive['cuts'][operation]['projection_sha256']
        and cut.effect()==archive['cuts'][operation]['effect'], 'cold original source projection/effect differs')
    return cut
