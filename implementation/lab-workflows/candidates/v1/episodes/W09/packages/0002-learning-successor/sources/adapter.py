"""W06 immutable candidate sources and independent current Agent/Tool permission."""
from __future__ import annotations
import copy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

PACKAGE = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-workflows/candidates/v1')
sys.path.insert(0, str(PACKAGE/'workflows'))
import research as contracts
from research import ROOT, carrier, validate, byte_sha, encoded, parse, require, SCOPE
from evaluator import HostAuthority, SelectedRecord, SessionLease

INTERFACE = 'bounded-operational-learning/v1-candidate'
ACTION = 'prepare-and-apply-controlled-lesson'
OUTPUT_KINDS = frozenset({'implementation', 'agent-action', 'agent-reflection', 'operational-lesson',
    'lesson-application', 'lesson-outcome-assessment', 'operational-observation', 'evidence-set',
    'improvement-signal', 'improvement-target', 'effect', 'typed-relation'})
W05 = PACKAGE/'failures/receipts/0004.json'
W05_SHA = '809855809498495ce6595e4a41c9cb6313a3b8126b82c06557505eac3b0c7fc3'
SOURCE = PACKAGE/'failures/receipts/0004/observed/episode-index.json'
AUTHORIZATION = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
OLD = PACKAGE/'examples/research/attempts/0001/build_inputs.py'
CORRECTED = PACKAGE/'examples/research/build_inputs.py'
VERSION = 'candidate.1'


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def host_fixture(*, head='protocol:W06-unit-fixture-cut', context_guard=None, handles=None, now=None, store_scope=None):
    """Host setup is outside public record bodies and claims no production identity."""
    sys.path.insert(0, str(PACKAGE/'receipts/action-boundaries'))
    from fixtures import Fixture
    clock = now or [time.time()]
    session = SessionLease(clock=lambda: clock[0], context_reader=context_guard)
    if handles:
        session.instance_ref, session.session_ref = handles
    f = Fixture(session=session, head=head)
    f.now = clock
    f.status['periods'] = {'protocol:w02-period': [clock[0]-60, clock[0]+900]}
    f.by_kind['delegation']['payload']['allowed_action_kinds'] = [ACTION]
    f.by_kind['agent-profile']['payload'].update(allowed_output_kinds=sorted(OUTPUT_KINDS), tool_class_refs=['tool-class:controlled-learning'])
    f.by_kind['tool']['payload'].update(tool_name='controlled-learning', interface_version=INTERFACE,
        input_contract_ref='protocol:W06-exact-reviewed-lesson', output_contract_ref='protocol:W06-bounded-learning-evidence',
        failure_boundary_refs=['protocol:W06-pending-no-redispatch'], evidence_route_ref='protocol:W06-owned-original-ledger')
    for k in ['delegation','agent-profile','tool']:
        f.reselect(k)
    f.status['tool_classes'][f.ref('tool')] = 'tool-class:controlled-learning'
    adapter = byte_sha(Path(__file__).read_bytes())
    evidence = encoded({'authorization_path': AUTHORIZATION.relative_to(ROOT).as_posix(), 'authorization_sha256': byte_sha(AUTHORIZATION.read_bytes()),
        'fixture_only': True, 'actual_owner_outcome': None, 'scope_ref': SCOPE, 'owned_store_scope': store_scope,
        'allowed_effects': ['exact isolated lesson fixture commit', 'owned source transform and process probe', 'unadmitted assessment/proposal', 'bounded public original-branch export'],
        'public_export_max_bytes': 20971520,
        'excluded_effects': ['canonical admission', 'live stores', 'service activation', 'external effects', 'Session-note persistence']})
    f.grant = replace(f.grant, not_before=clock[0]-60, expires_at=clock[0]+900, action_kinds=frozenset({ACTION}),
        max_actions=4, max_input_bytes=65536, max_output_bytes=1048576, adapter_sha256=adapter,
        evidence_original=evidence, evidence_sha256=byte_sha(evidence), evidence_ref='protocol:W06-explicit-owned-development-permission', recovery_allowed=False)
    f.request.update(action_kind=ACTION, deadline=utc(clock[0]+800))
    module = contracts.shared.load_registered(contracts.ENGINEERING_INPUTS/'registered_evaluator.py',
        contracts.read(contracts.ENGINEERING_INPUTS/'input-manifest.json')['output_source_sha256'])
    f.authority = module.HostAuthority(session, lambda ref: f.records.get(ref), lambda: copy.deepcopy(f.status), lambda: f.grant,
        adapter_sha256=adapter, environment_sha256=f.environment_sha256, registered_interfaces=frozenset({INTERFACE}))
    return f


class CandidateSources:
    def __init__(self, output, host, *, record_scope=None):
        self.output = Path(output)
        require(not self.output.exists(), 'learning output already exists')
        self.output.mkdir(mode=0o700)
        self.host = host
        self.scope = record_scope or SCOPE
        self.records, self.blobs, self.roles = {}, {}, {}
        own = list((PACKAGE/'learning').glob('*.py')) + [AUTHORIZATION, OLD, CORRECTED] + list(Path(__file__).resolve().parent.glob('*.py'))
        self.sources = {p: byte_sha(p.read_bytes()) for p in own}
        require(byte_sha(W05.read_bytes()) == W05_SHA, 'independent W05 predecessor pin differs')
        receipt = parse(W05.read_bytes())
        require(receipt['result'] == 'PASS' and receipt['task_complete'], 'W05 incomplete')
        for row in receipt['files']:
            require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'], 'W05 source proof changed')
        selected = next(row for row in receipt['files'] if row['path'] == SOURCE.relative_to(ROOT).as_posix())
        require(byte_sha(SOURCE.read_bytes()) == selected['sha256'], 'W05 original episode changed')
        self.sources.update({W05: W05_SHA, SOURCE: selected['sha256'], contracts.shared.REGISTRY: byte_sha(contracts.shared.REGISTRY.read_bytes()),
            contracts.PAIRS: byte_sha(contracts.PAIRS.read_bytes()), Path(contracts.__file__): byte_sha(Path(contracts.__file__).read_bytes()),
            Path(contracts.shared.__file__): byte_sha(Path(contracts.shared.__file__).read_bytes())})
        for k in OUTPUT_KINDS:
            row, _ = carrier(k)
            self.sources[ROOT/row['schema_path']] = row['schema_sha256']
        self.input = encoded({'W05_episode_sha256': selected['sha256'], 'scope': 'explicit owned W06 candidate learning', 'record_scope': self.scope})
        self.host.request['input_sha256'] = byte_sha(self.input)
        self.check()
        index = parse(SOURCE.read_bytes())
        self.W05_refs = index['selected_refs']
        for row in index['records']:
            if row['kind'] == 'typed-relation':
                continue
            p = SOURCE.parent/row['path']
            self.import_record(p, row['version_ref'], row['sha256'])
        self.W05_manifest = SOURCE.parent/'observation-manifest.json'
        self.sources[self.W05_manifest] = byte_sha(self.W05_manifest.read_bytes())
        self.manifest_ref = self.blob('source-observation-manifest.json', self.W05_manifest.read_bytes())
        self.permission_ref = self.blob('host-permission.json', self.host.grant.evidence_original)
        self.actor_records = {}
        for k in self.host.by_kind:
            selected_actor = self.host.records[self.host.ref(k)]
            self.actor_records[k] = self.blob('actor-'+k+'.json', selected_actor.original)

    def check(self):
        require(isinstance(self.host.authority, HostAuthority), 'independent host authority required')
        for p, sha in self.sources.items():
            require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == sha, 'learning selected source drift')
        e = self.host.authority.check(self.host.raw())
        require(e['posture'] == 'permitted', 'current learning authority denied')
        selected = self.host.authority.resolver(e['request']['profile_ref'])
        require(isinstance(selected, SelectedRecord) and OUTPUT_KINDS <= set(selected.record('agent-profile')['payload']['allowed_output_kinds']), 'learning Profile output permission differs')
        c = e['tool_contract']
        require(c['interface_version'] == INTERFACE and c['input_contract_ref'] == 'protocol:W06-exact-reviewed-lesson'
            and c['output_contract_ref'] == 'protocol:W06-bounded-learning-evidence'
            and c['failure_boundary_refs'] == ['protocol:W06-pending-no-redispatch']
            and c['evidence_route_ref'] == 'protocol:W06-owned-original-ledger', 'learning Tool contract differs')
        require(e['request']['input_sha256'] == byte_sha(self.input), 'learning exact input differs')
        return e

    def blob(self, name, raw):
        self.check()
        require(type(raw) is bytes and Path(name).name == name and len(raw) <= self.host.grant.max_output_bytes, 'bounded original bytes required')
        p = self.output/name
        with p.open('xb') as stream:
            stream.write(raw)
        key = 'protocol:W06-original:'+byte_sha(raw)
        self.blobs[key] = (p, byte_sha(raw))
        return key

    def original(self, key):
        self.check()
        require(key in self.blobs, 'learning original evidence unresolved')
        p, sha = self.blobs[key]
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == sha, 'learning original evidence drift')
        return p.read_bytes()

    def import_record(self, path, ref, sha):
        self.check()
        path = Path(path); raw = path.read_bytes()
        require(byte_sha(raw) == sha and not path.is_symlink(), 'selected learning input drift')
        value = parse(raw); validate(value, value['kind'])
        require(ref.startswith(value['node_id']+'@') and ref not in self.records, 'learning input exact revision differs')
        dest = self.output/('input-'+byte_sha(ref.encode())[:20]+'.json')
        with dest.open('xb') as stream:
            stream.write(raw)
        self.records[ref], self.roles[ref] = (dest, sha), 'input'

    def put(self, value, version=VERSION):
        self.check()
        require(value.get('kind') in OUTPUT_KINDS, 'undeclared learning output kind')
        validate(value, value['kind'])
        require(value['authority_effect'] == 'none' and value['lifecycle_state'] == 'candidate' and value['scope_ref'] == self.scope, 'learning output must remain a scoped candidate')
        ref = value['node_id']+'@'+version
        require(ref not in self.records, 'immutable learning revision already exists')
        raw = encoded(value); require(len(raw) <= self.host.grant.max_output_bytes, 'learning record budget exceeded')
        p = self.output/(value['kind']+'-'+byte_sha(ref.encode())[:20]+'.json')
        with p.open('xb') as stream:
            stream.write(raw)
        self.records[ref], self.roles[ref] = (p, byte_sha(raw)), 'output'
        return ref

    def get(self, ref, kind=None):
        self.check()
        require(ref in self.records, 'exact learning revision unresolved')
        p, sha = self.records[ref]
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == sha, 'learning selected record drift')
        value = parse(p.read_bytes())
        require(kind is None or value['kind'] == kind, 'learning input kind differs')
        validate(value, value['kind'])
        return value

    def make(self, kind, name, payload, hint):
        require(kind in OUTPUT_KINDS, 'learning kind undeclared')
        rk, direction, counterpart_kind, counterpart_ref = hint
        value = contracts.shared.artifact(kind, name, payload, [{'relation_kind_ref': 'relation.'+rk, 'direction': direction,
            'counterpart_kind': counterpart_kind, 'counterpart_ref': counterpart_ref}])
        value.update(node_id=kind+':lab-W09:bc3c50170a404b4ba8d8:learning-retry:'+name, name='W06 candidate '+name, scope_ref=self.scope,
            owner_ref=self.host.ref('principal'), challenge_route='protocol:W06-explicit-review-and-residue', evidence_refs=[],
            claim_ceiling='Exact candidate learning only; no canonical admission, actual owner outcome, general efficacy or persistent machine memory.')
        validate(value, kind)
        return value

    def edge(self, name, rk, source, target, qualifiers):
        records = {source: self.get(source), target: self.get(target)}
        value = contracts.typed(name, 'relation.'+rk, source, target, records, qualifiers)
        value.update(node_id='typed-relation:lab-W09:bc3c50170a404b4ba8d8:learning-retry:'+name, scope_ref=self.scope, owner_ref=self.host.ref('principal'),
            evidence_refs=[], challenge_route='protocol:W06-explicit-review-and-residue', claim_ceiling='Existing declared candidate learning connection only.')
        value['payload']['relation_evidence_refs'] = ['protocol:W06-exact-source-and-outcome-evidence']
        return self.put(value)
