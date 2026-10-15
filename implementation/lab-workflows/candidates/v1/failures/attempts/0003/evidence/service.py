"""W05 original-byte evidence and current host permission, candidate scope only."""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / 'workflows'))
import research as upstream
from research import ROOT, SCOPE, carrier, validate, require, byte_sha, encoded, parse
from evaluator import HostAuthority, SelectedRecord

INTERFACE = 'bounded-evidence-failure-challenge/v1-candidate'
ACTION = 'prepare-evidence-failure-challenge'
AUTHORIZATION = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
OUTPUT_KINDS = frozenset({'implementation', 'agent-action', 'operational-observation', 'evidence-set',
    'classification-scheme', 'classification-value', 'classification-assignment', 'failure-mode',
    'failure-occurrence', 'failure-assessment', 'failure-control-binding', 'incident', 'hypothesis',
    'challenge-contract', 'challenge-event', 'decision', 'decision-scope', 'effect', 'authority-claim', 'typed-relation'})
OLD_BUILDER = PACKAGE / 'examples/research/attempts/0001/build_inputs.py'
NEW_BUILDER = PACKAGE / 'examples/research/build_inputs.py'
VERSION = 'candidate.1'
PREDECESSOR = PACKAGE/'examples/research/receipts/0002.json'
PREDECESSOR_SHA256 = '20fb853bbf599d567c2723fc0734a37fd1bdaf7b20211c5cd26a358ff4edf742'
SELECTION_SHA256 = '9ea324cf32469efa00d32c522bdf9baeab710e4463b5bc0ba69aba9d2996f148'


def utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def host_fixture():
    """Development owner selects this outside the caller/annotation boundary."""
    sys.path.insert(0, str(PACKAGE / 'receipts/action-boundaries'))
    from fixtures import Fixture
    f = Fixture()
    f.by_kind['delegation']['payload']['allowed_action_kinds'] = [ACTION]
    f.by_kind['agent-profile']['payload'].update(allowed_output_kinds=sorted(OUTPUT_KINDS),
        tool_class_refs=['tool-class:W05-controlled-evidence'])
    f.by_kind['tool']['payload'].update(tool_name='W05-controlled-evidence', interface_version=INTERFACE,
        input_contract_ref='protocol:W05-exact-controlled-builders', output_contract_ref='protocol:W05-original-byte-candidates',
        failure_boundary_refs=['protocol:W05-pending-no-redispatch'], evidence_route_ref='protocol:W05-owned-journal')
    for k in ['delegation', 'agent-profile', 'tool']:
        f.reselect(k)
    f.status['tool_classes'][f.ref('tool')] = 'tool-class:W05-controlled-evidence'
    adapter = byte_sha(Path(__file__).read_bytes())
    evidence = encoded({'authorization_path': AUTHORIZATION.relative_to(ROOT).as_posix(),
        'authorization_sha256': byte_sha(AUTHORIZATION.read_bytes()), 'fixture_only': True,
        'scope': SCOPE, 'actual_owner_outcome': None,
        'excluded_effects': ['canonical-admission', 'challenged-subject-mutation', 'live-operation', 'production-incident']})
    f.grant = replace(f.grant, action_kinds=frozenset({ACTION}), max_actions=2, max_input_bytes=65536,
        max_output_bytes=1048576, adapter_sha256=adapter, evidence_original=evidence,
        evidence_sha256=byte_sha(evidence), evidence_ref='protocol:W05-explicit-development-grant', recovery_allowed=False)
    f.request['action_kind'] = ACTION
    module = upstream.shared.load_registered(upstream.ENGINEERING_INPUTS / 'registered_evaluator.py',
        upstream.read(upstream.ENGINEERING_INPUTS / 'input-manifest.json')['output_source_sha256'])
    f.authority = module.HostAuthority(f.session, lambda r: f.records.get(r), lambda: copy.deepcopy(f.status),
        lambda: f.grant, adapter_sha256=adapter, environment_sha256=f.environment_sha256,
        registered_interfaces=frozenset({INTERFACE}))
    return f


class EvidenceService:
    """Host-owned resolver pins original bytes; caller records cannot grant permission."""
    def __init__(self, output, host):
        self.output = Path(output)
        require(not self.output.exists(), 'W05 output already exists')
        self.output.mkdir(mode=0o700)
        self.host = host
        self.manifest_ref = None
        self.subject_ref = None
        self.records = {}   # exact version -> (path, independent original-byte hash)
        self.record_roles = {}
        self.blobs = {}
        self.sources = {p: byte_sha(p.read_bytes()) for p in [OLD_BUILDER, NEW_BUILDER, AUTHORIZATION,
            Path(__file__), PACKAGE/'failures/service.py', PACKAGE/'challenges/service.py', PACKAGE/'evidence/probe_child.py']}
        require(byte_sha(PREDECESSOR.read_bytes()) == PREDECESSOR_SHA256, 'independent W04 predecessor pin differs')
        predecessor = parse(PREDECESSOR.read_bytes())
        require(predecessor['result'] == 'PASS' and predecessor['task_complete'], 'W04 predecessor incomplete')
        for row in predecessor['files']:
            require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'], 'W04 verified source closure drift')
        self.sources[PREDECESSOR] = PREDECESSOR_SHA256
        for p in [upstream.shared.REGISTRY, upstream.PAIRS, Path(upstream.__file__), Path(upstream.shared.__file__),
            PACKAGE/'authority/evaluator.py', PACKAGE/'authority/dispatch.py', PACKAGE/'tools/counter.py',
            upstream.ENGINEERING_INPUTS/'registered_evaluator.py']:
            self.sources[p] = byte_sha(p.read_bytes())
        for kind in OUTPUT_KINDS | {'product-capability'}:
            row, _ = carrier(kind)
            self.sources[ROOT/row['schema_path']] = row['schema_sha256']
        self.input = encoded({'old_builder_sha256': self.sources[OLD_BUILDER], 'successor_builder_sha256': self.sources[NEW_BUILDER],
            'scope': 'controlled historical source replay; no original-environment claim'})
        self.host.request['input_sha256'] = byte_sha(self.input)
        self.actions = 0
        self.check()
        selection_path = PACKAGE/'examples/research/packages/0007/selection.json'
        require(byte_sha(selection_path.read_bytes()) == SELECTION_SHA256, 'independent current research context pin differs')
        selected = next(r for r in parse(selection_path.read_bytes())['records'] if r['kind'] == 'product-capability')
        cap_path = selection_path.parent / selected['path']
        require(byte_sha(cap_path.read_bytes()) == selected['sha256'], 'selected capability original bytes differ')
        self.sources[selection_path] = byte_sha(selection_path.read_bytes())
        self.sources[cap_path] = selected['sha256']
        v = parse(cap_path.read_bytes()); validate(v, 'product-capability')
        p = self.output/'selected-input-capability.json'
        with p.open('xb') as stream:
            stream.write(cap_path.read_bytes())
        self.capability_ref = selected['version_ref']
        self.records[self.capability_ref] = (p, selected['sha256'])
        self.record_roles[self.capability_ref] = 'input'
        attribution = []
        for kind in self.host.by_kind:
            selected = self.host.records[self.host.ref(kind)]
            original_ref = self.blob('actor-'+kind+'.json', selected.original)
            attribution.append({'version_ref': selected.version_ref, 'kind': kind,
                'sha256': selected.expected_sha256, 'original_ref': original_ref,
                'posture': selected.posture})
        self.blob('host-attribution.json', encoded({'selected_records': attribution,
            'permission_original_ref': self.blob('host-permission.json', self.host.grant.evidence_original),
            'permission_sha256': self.host.grant.evidence_sha256,
            'instance_handle': self.host.session.instance_ref, 'session_handle': self.host.session.session_ref,
            'authority_cut': self.host.status['head'], 'fixture_only': True, 'actual_owner_outcome': None}))

    def check(self):
        require(isinstance(self.host.authority, HostAuthority), 'trusted host authority required')
        for p, digest in self.sources.items():
            require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == digest, 'W05 selected source drift')
        e = self.host.authority.check(self.host.raw())
        require(e['posture'] == 'permitted', 'current W05 authority denied')
        p = self.host.authority.resolver(e['request']['profile_ref'])
        require(isinstance(p, SelectedRecord), 'current Profile unresolved')
        require(OUTPUT_KINDS <= set(p.record('agent-profile')['payload']['allowed_output_kinds']), 'Profile denies W05 outputs')
        c = e['tool_contract']
        require(c['interface_version'] == INTERFACE and c['input_contract_ref'] == 'protocol:W05-exact-controlled-builders'
            and c['output_contract_ref'] == 'protocol:W05-original-byte-candidates'
            and c['failure_boundary_refs'] == ['protocol:W05-pending-no-redispatch']
            and c['evidence_route_ref'] == 'protocol:W05-owned-journal', 'W05 Tool contract differs')
        require(byte_sha(self.input) == e['request']['input_sha256'], 'W05 exact input differs')
        return e

    def blob(self, name, raw):
        self.check()
        require(type(raw) is bytes and Path(name).name == name, 'original bytes and local blob name required')
        p = self.output / name
        with p.open('xb') as stream:
            stream.write(raw)
        key = 'protocol:W05-original:' + byte_sha(raw)
        self.blobs[key] = (p, byte_sha(raw))
        return key

    def original(self, key):
        self.check()
        require(key in self.blobs, 'original evidence unresolved')
        p, digest = self.blobs[key]
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == digest, 'original evidence changed')
        return p.read_bytes()

    def put(self, record, version=VERSION):
        self.check()
        validate(record, record['kind'])
        require(record['authority_effect'] == 'none' and record['lifecycle_state'] == 'candidate'
            and record['scope_ref'] == SCOPE, 'candidate posture required; classification cannot grant authority')
        key = record['node_id'] + '@' + version
        require(key not in self.records, 'immutable revision already selected')
        raw = encoded(record)
        require(len(raw) <= self.host.grant.max_output_bytes, 'output budget exceeded')
        path = self.output / (record['kind'] + '-' + byte_sha(key.encode())[:20] + '.json')
        with path.open('xb') as stream:
            stream.write(raw)
        self.records[key] = (path, byte_sha(raw))
        self.record_roles[key] = 'output'
        return key

    def get(self, key, kind=None):
        self.check()
        require(key in self.records, 'exact W05 revision unresolved')
        p, digest = self.records[key]
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == digest, 'W05 original revision drift')
        v = parse(p.read_bytes())
        require(key.startswith(v['node_id'] + '@'), 'W05 identity differs')
        require(kind is None or v['kind'] == kind, 'mode is not occurrence; record kind differs')
        validate(v, v['kind'])
        return v

    def make(self, kind, name, payload):
        def planned(k, n):
            return k+':lab-W05:'+n+'@'+VERSION
        hints = {
            'implementation': ('realizes', 'source', 'product-capability', self.capability_ref),
            'agent-action': ('produces', 'source', 'operational-observation', planned('operational-observation', 'builder-preparation')),
            'operational-observation': ('evidence-bears-on', 'source', 'failure-occurrence', planned('failure-occurrence', 'retained-builder-rejection')),
            'classification-scheme': ('member-of', 'target', 'classification-value', payload.get('value_refs', [''])[0] if payload.get('value_refs') else ''),
            'classification-value': ('member-of', 'source', 'classification-scheme', payload.get('scheme_ref', '')),
            'classification-assignment': ('governed-by', 'source', 'classification-scheme', payload.get('scheme_version_ref', '')),
            'failure-mode': ('instance-of', 'target', 'failure-occurrence', planned('failure-occurrence', 'retained-builder-rejection')),
            'failure-occurrence': ('affects', 'source', 'implementation', payload.get('subject_ref', '')),
            'failure-assessment': ('evaluates', 'source', 'failure-occurrence', payload.get('occurrence_ref', '')),
            'failure-control-binding': ('controls', 'source', 'failure-mode', payload.get('failure_mode_ref', '')),
            'incident': ('member-of', 'target', 'failure-occurrence', payload.get('occurrence_refs', [''])[0] if payload.get('occurrence_refs') else ''),
            'evidence-set': ('evidence-bears-on', 'source', 'hypothesis', planned('hypothesis', 'cause-proposal')),
            'hypothesis': ('evidence-bears-on', 'target', 'evidence-set', planned('evidence-set', 'controlled-preparation')),
            'challenge-contract': ('governed-by', 'target', 'challenge-event', planned('challenge-event', 'historical-builder-contract')),
            'challenge-event': ('governed-by', 'source', 'challenge-contract', payload.get('challenge_contract_ref', '')),
            'effect': ('declares-effect-on', 'target', 'decision', planned('decision', 'local-fixture-disposition')),
            'decision': ('declares-effect-on', 'source', 'effect', payload.get('declared_effect_refs', [''])[0] if payload.get('declared_effect_refs') else ''),
            'decision-scope': ('scopes-authority-over', 'target', 'authority-claim', planned('authority-claim', 'controlled-contest-claim')),
            'authority-claim': ('scopes-authority-over', 'source', 'decision-scope', payload.get('decision_scope_ref', ''))}
        require(kind in hints, 'W05 output kind undeclared')
        relation, direction, counterpart_kind, counterpart_ref = hints[kind]
        value = upstream.shared.artifact(kind, name, payload, [{'relation_kind_ref': 'relation.'+relation,
            'direction': direction, 'counterpart_kind': counterpart_kind, 'counterpart_ref': counterpart_ref}])
        value.update(node_id=kind + ':lab-W05:' + name, name='W05 controlled ' + name,
            evidence_refs=[], challenge_route='protocol:W05-candidate-challenge',
            owner_ref=self.host.ref('principal'),
            claim_ceiling='Controlled candidate only; no canonical admission, production Incident or actual R08 outcome.')
        validate(value, kind)
        return value

    def edge(self, name, kind, source, target, qualifiers):
        a, b = self.get(source), self.get(target)
        v = upstream.typed(name, kind, source, target, {source: a, target: b}, qualifiers)
        v.update(node_id='typed-relation:lab-W05:' + name, evidence_refs=[], challenge_route='protocol:W05-candidate-challenge',
            owner_ref=self.host.ref('principal'), claim_ceiling='Existing exact pair in controlled candidate scope only.')
        v['payload']['relation_evidence_refs'] = ['protocol:W05-original-byte-candidates']
        return self.put(v)

    def observe(self):
        """Only two host-selected retained sources execute in owned fresh child directories."""
        self.check()
        journal = self.output / 'probe-journal.json'
        require(not journal.exists() and self.actions == 0, 'pending/completed probe prohibits redispatch')
        self.blob('probe-journal.json', encoded({'posture': 'pending', 'retry_allowed': False,
            'request_sha256': byte_sha(self.host.raw()), 'input_sha256': byte_sha(self.input), 'actual_owner_outcome': None}))
        result = []
        for label, source in [('historical', OLD_BUILDER), ('successor', NEW_BUILDER)]:
            self.check()
            require(self.actions < self.host.grant.max_actions, 'probe action budget exceeded')
            self.actions += 1
            try:
                p = subprocess.run([sys.executable, str(PACKAGE/'evidence/probe_child.py'), str(source),
                    str(self.output/(label+'-inputs')), self.sources[source]], capture_output=True, timeout=20)
            except subprocess.TimeoutExpired as exc:
                self.blob(label+'-timeout-stdout.log', exc.stdout or b'')
                self.blob(label+'-timeout-stderr.log', exc.stderr or b'')
                self.blob(label+'-timeout.json', encoded({'posture': 'inconclusive-timeout', 'retry_allowed': False,
                    'controlled': True, 'seconds_bound': 20}))
                raise
            require(len(p.stdout) + len(p.stderr) <= self.host.grant.max_output_bytes, 'probe output budget exceeded')
            out = self.blob(label+'-stdout.json', p.stdout)
            err = self.blob(label+'-stderr.log', p.stderr)
            require(p.returncode == 0, 'probe child incomplete; pending requires inspection')
            data = parse(p.stdout)
            require(data['controlled'] is True and data['source_sha256'] == self.sources[source], 'probe source/context differs')
            result.append({'label': label, 'returncode': p.returncode, 'stdout_ref': out, 'stderr_ref': err,
                'result': data, 'observed_at': utc(self.host.now[0])})
        self.check()
        manifest = {'controlled': True, 'actual_owner_outcome': None, 'observations': result,
            'failed_preparations': sum(v['result']['preparation_posture'] == 'rejected' for v in result),
            'subject_bytes_unchanged': byte_sha(OLD_BUILDER.read_bytes()) == self.sources[OLD_BUILDER]}
        key = self.blob('observation-manifest.json', encoded(manifest))
        self.blob('probe-completed.json', encoded({'posture': 'completed', 'manifest_ref': key, 'retry_allowed': False}))
        self.manifest_ref = key
        return key
