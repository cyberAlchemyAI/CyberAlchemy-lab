"""W05 exact contest transitions; a controlled host gate never supplies R08 admission."""
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence.service import EvidenceService, utc
from research import require, byte_sha, encoded
from evaluator import timestamp


@dataclass(frozen=True)
class ControlledGate:
    gate_ref: str
    session_handle: str
    head: str
    scope_ref: str
    challenge_ref: str
    challenge_sha256: str
    subject_ref: str
    subject_sha256: str
    decision_ref: str
    decision_sha256: str
    effect_ref: str
    effect_sha256: str
    decision_scope_ref: str
    decision_scope_sha256: str
    claim_ref: str
    claim_sha256: str
    expires_at: float
    fixture_outcome: str
    original: bytes
    original_sha256: str


class ChallengeService:
    def __init__(self, evidence, contract_ref, *, gate_reader):
        require(isinstance(evidence, EvidenceService) and callable(gate_reader), 'host-selected services required')
        self.e, self.contract_ref, self.gate_reader = evidence, contract_ref, gate_reader
        self.state, self.current_ref, self.response_ref = 'not-submitted', None, None
        self.contract = evidence.get(contract_ref, 'challenge-contract')
        p = self.contract['payload']
        require(p['policy_ref'] == 'protocol:W05-controlled-contest-policy@1'
            and p['response_period'] == 'protocol:W05-300-second-response@1'
            and p['owner_route'] == 'protocol:W05-fixture-principal-route'
            and p['resolution_gate_ref'] == 'protocol:W05-exact-fixture-gate@1', 'host challenge policy unresolved')
        self.response_seconds = 300
        self.owner_ref = evidence.host.ref('principal')

    def check(self):
        self.e.check()
        require(self.e.get(self.contract_ref, 'challenge-contract') == self.contract, 'Challenge Contract drift')

    def _evidence(self, refs):
        require(refs and len(refs) == len(set(refs)), 'challenge evidence absent/duplicate')
        kinds = set()
        for r in refs:
            kinds.add(self.e.get(r)['kind'])
        require(set(self.contract['payload']['required_evidence_kinds']) <= kinds, 'required challenge evidence missing')
        # Link selected evidence to the original controlled subject, not unrelated valid carriers.
        for r in refs:
            v = self.e.get(r)
            if v['kind'] == 'evidence-set':
                require(self.e.manifest_ref in v['payload']['source_refs'], 'challenge Evidence Set provenance differs')
                for item in v['payload']['item_refs']:
                    observation = self.e.get(item, 'operational-observation')
                    require(self.e.manifest_ref in observation['payload']['evidence_refs'], 'challenge observation provenance differs')
        self.e.original(self.e.manifest_ref)

    def submit(self, subject_ref, challenger_ref, ground, evidence_refs):
        self.check()
        require(self.state == 'not-submitted', 'challenge already submitted')
        p = self.contract['payload']
        subject = self.e.get(subject_ref)
        require(subject['kind'] in p['challengeable_subject_kinds'], 'subject kind not challengeable')
        require(subject_ref == self.e.subject_ref, 'evidence does not challenge this exact subject')
        require(challenger_ref == self.e.host.ref('principal') and 'principal' in p['eligible_challenger_kinds'], 'current challenger ineligible')
        require(ground in p['grounds'], 'challenge ground undeclared')
        self._evidence(evidence_refs)
        record = self.e.make('challenge-event', 'historical-builder-contract', {
            'challenge_contract_ref': self.contract_ref, 'challenger_ref': challenger_ref,
            'subject_ref': subject['node_id'], 'subject_version_ref': subject_ref,
            'ground': ground, 'evidence_refs': evidence_refs, 'submitted_at': utc(self.e.host.now[0]),
            'response_state': 'submitted', 'resolution_decision_ref': 'none', 'residue_refs': ['protocol:W05-old-revision-review-pending']})
        self.current_ref = self.e.put(record)
        self.state = 'submitted'
        return self.current_ref

    def eligible(self):
        self.check()
        require(self.state == 'submitted', 'challenge submitted state required')
        v = self.e.get(self.current_ref, 'challenge-event')
        self._evidence(v['payload']['evidence_refs'])
        self.e.get(v['payload']['subject_version_ref'])
        require(self.e.host.now[0] - timestamp(v['payload']['submitted_at']) < self.response_seconds, 'eligibility response window expired')
        return self._transition(v, 'eligible', 'candidate.2')

    def respond(self, mode, evidence_refs):
        self.check()
        require(self.state == 'eligible', 'eligible challenge required before response')
        v = self.e.get(self.current_ref, 'challenge-event')
        require(self.e.host.ref('principal') == self.owner_ref, 'current response owner differs')
        require(mode in self.contract['payload']['response_modes'], 'response mode undeclared')
        elapsed = self.e.host.now[0] - timestamp(v['payload']['submitted_at'])
        require(0 <= elapsed < self.response_seconds, 'response window expired or clock moved backward')
        self._evidence(evidence_refs)
        self.response_ref = self.e.blob('challenge-response.json', encoded({'challenge_ref': self.current_ref,
            'challenge_sha256': self.e.records[self.current_ref][1], 'subject_version_ref': v['payload']['subject_version_ref'],
            'contract_ref': self.contract_ref, 'owner_ref': self.owner_ref, 'response_mode': mode,
            'evidence_refs': evidence_refs, 'fixture_only': True, 'actual_owner_outcome': None,
            'response_scope': 'contest disposition; original source remains unchanged', 'responded_at': utc(self.e.host.now[0])}))
        v['payload']['evidence_refs'] = list(dict.fromkeys(v['payload']['evidence_refs'] + evidence_refs))
        return self._transition(v, 'responded', 'candidate.3')

    def _transition(self, value, state, version):
        value['payload']['response_state'] = state
        old = self.current_ref
        self.current_ref = self.e.put(value, version)
        self.e.edge('challenge-'+state, 'relation.successor-of', self.current_ref, old,
            {'succession_effect': 'candidate-contest-state-only'})
        self.state = state
        return self.current_ref

    def resolve(self, decision_ref, effect_ref, decision_scope_ref):
        self.check()
        require(self.state == 'responded' and self.response_ref is not None, 'exact response required before resolution')
        self.e.original(self.response_ref)
        v = self.e.get(self.current_ref, 'challenge-event')
        subject_ref = v['payload']['subject_version_ref']
        self.e.get(subject_ref)
        d = self.e.get(decision_ref, 'decision')['payload']
        effect = self.e.get(effect_ref, 'effect')['payload']
        scope_record = self.e.get(decision_scope_ref, 'decision-scope')
        scope = scope_record['payload']
        claim_ref = scope_record['relation_refs'][0]['counterpart_ref']
        claim = self.e.get(claim_ref, 'authority-claim')['payload']
        require(d['decision_maker_ref'] == self.owner_ref and d['subject_refs'] == [self.current_ref]
            and d['declared_effect_refs'] == [effect_ref] and d['selected_outcome'] == 'fixture-accept-contest-for-revision', 'Decision exact declaration differs')
        require(d['evidence_basis_refs'] == [self.response_ref], 'Decision response evidence differs')
        require(effect == {'effect_kind': 'challenge-disposition', 'subject_ref': self.current_ref,
            'intended_state': 'resolved-for-revision', 'effective_when': 'exact-current-W05-controlled-host-gate',
            'verification_refs': [self.response_ref, subject_ref]}, 'Effect includes undeclared subject/state/verification')
        require(scope['subject_refs'] == [self.current_ref] and scope['subject_kind_refs'] == ['challenge-event']
            and scope['permitted_effects'] == ['challenge-disposition']
            and set(scope['excluded_effects']) == {'challenged-subject-mutation', 'canonical-admission', 'live-activation'}, 'Decision Scope differs')
        require(claim['decision_scope_ref'] == decision_scope_ref and claim['claimant_ref'] == self.owner_ref
            and claim['claimed_permissions'] == ['challenge-disposition']
            and claim['authority_basis_refs'] == [self.e.host.grant.evidence_ref]
            and set(claim['limitations']) == {'fixture-only', 'no-challenged-subject-mutation', 'no-canonical-admission', 'no-live-activation'}, 'controlled Authority Claim differs')
        gate = self.gate_reader()
        require(isinstance(gate, ControlledGate), 'separate host fixture gate required; request declarations insufficient')
        require(byte_sha(gate.original) == gate.original_sha256, 'host gate original evidence changed')
        expected = {'fixture_only': True, 'actual_owner_outcome': None, 'challenge_ref': self.current_ref,
            'subject_ref': subject_ref, 'decision_ref': decision_ref, 'effect_ref': effect_ref,
            'decision_scope_ref': decision_scope_ref, 'response_ref': self.response_ref,
            'claim_ref': claim_ref,
            'fixture_outcome': 'fixture-accept-contest-for-revision'}
        require(gate.original == encoded(expected), 'host gate evidence scope differs')
        require(gate.gate_ref == self.contract['payload']['resolution_gate_ref'] and gate.scope_ref == self.e.host.scope
            and gate.session_handle == self.e.host.session.session_ref and gate.head == self.e.host.status['head']
            and self.e.host.now[0] < gate.expires_at and gate.fixture_outcome == d['selected_outcome'], 'host gate expired or belongs to another scope/Session/cut')
        for key, sha in [(gate.challenge_ref, gate.challenge_sha256), (gate.subject_ref, gate.subject_sha256),
            (gate.decision_ref, gate.decision_sha256), (gate.effect_ref, gate.effect_sha256),
            (gate.decision_scope_ref, gate.decision_scope_sha256), (gate.claim_ref, gate.claim_sha256)]:
            self.e.get(key)
            require(self.e.records[key][1] == sha, 'host gate exact original revision changed')
        require((gate.challenge_ref, gate.subject_ref, gate.decision_ref, gate.effect_ref, gate.decision_scope_ref, gate.claim_ref)
            == (self.current_ref, subject_ref, decision_ref, effect_ref, decision_scope_ref, claim_ref), 'host gate wrong exact target')
        # Immutable candidate postimage only; never an overwrite of the challenged subject.
        v['payload'].update(resolution_decision_ref=decision_ref, response_state='resolved-for-revision')
        original_subject = self.e.records[subject_ref][1]
        result = self._transition(v, 'resolved-for-revision', 'candidate.4')
        self.e.get(subject_ref)
        require(self.e.records[subject_ref][1] == original_subject, 'challenged subject changed during disposition')
        self.e.edge('decision-contest', 'relation.declares-effect-on', decision_ref, gate.challenge_ref,
            {'effect_kind': 'challenge-disposition', 'exact_target_version_ref': gate.challenge_ref})
        self.state = 'resolved'
        return result
