"""W02 durable pending ledger and observational recovery for one local Tool."""
from contextlib import contextmanager
import base64
from dataclasses import asdict, dataclass
import fcntl
import os
from pathlib import Path
import sys
import uuid

from evaluator import BoundaryFault, HostAuthority, byte_sha, encoded, parse, require
TOOLS = Path(__file__).resolve().parents[1] / 'tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from counter import CounterTool, INPUT_CONTRACT, OUTPUT_CONTRACT, atomic, fsync_directory, regular_json
from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class LedgerPins:
    ledger_id: str
    config_sha256: str
    journal_sha256: str
    counter_sha256: str


def pins(root):
    root = Path(root)
    config = regular_json(root / 'config.json')
    regular_json(root / 'journal.json')
    regular_json(root / 'counter.json')
    return LedgerPins(config['ledger_id'], byte_sha((root/'config.json').read_bytes()),
                      byte_sha((root/'journal.json').read_bytes()), byte_sha((root/'counter.json').read_bytes()))


def initialize(root):
    """Host-only explicit initialization; never infer missing records mean no effect."""
    root = Path(root)
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    config = {'ledger_id': 'protocol:w02-local-ledger:' + str(uuid.uuid4()),
              'interface': 'bounded-local-counter/v1-candidate', 'authority_effect': 'none'}
    atomic(root / 'config.json', config)
    atomic(root / 'journal.json', {'entries': []})
    atomic(root / 'counter.json', {'value': 0, 'action_id': 'protocol:counter-genesis', 'input_sha256': '0'*64})
    (root / '.writer.lock').touch(mode=0o600)
    fsync_directory(root)
    return pins(root)


class LocalDispatcher:
    def __init__(self, root, expected, authority):
        require(isinstance(expected, LedgerPins), 'independent operational ledger pins required')
        require(isinstance(authority, HostAuthority), 'trusted host authority required')
        self.root = Path(root)
        require(not self.root.is_symlink(), 'unsafe operational root')
        self.expected = expected
        self.authority = authority
        self.tool = CounterTool(self.root)
        self.verify()

    @contextmanager
    def locked(self):
        path = self.root / '.writer.lock'
        require(path.is_file() and not path.is_symlink(), 'operational lock missing')
        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)

    def verify(self):
        observed = pins(self.root)
        require(observed.ledger_id == self.expected.ledger_id
                and observed.config_sha256 == self.expected.config_sha256
                and observed.journal_sha256 == self.expected.journal_sha256,
                'operational ledger drift; reconcile from independent pins')
        journal = regular_json(self.root / 'journal.json')
        require(set(journal) == {'entries'} and type(journal['entries']) is list, 'ledger contract invalid')
        self.tool.state()
        if observed.counter_sha256 != self.expected.counter_sha256:
            pending = [e for e in journal['entries'] if e['posture'] == 'pending']
            require(len(pending) == 1 and observed.counter_sha256 in {
                byte_sha(encoded(pending[0]['before'])), byte_sha(encoded(pending[0]['predicted']))},
                'unbound Tool state drift')
            # An externally pinned pending journal already binds both possible states.
            # Accepting observed bytes here is read verification, never reconciliation.
            self.expected = observed
        return journal

    def save(self, journal):
        atomic(self.root / 'journal.json', journal)
        self.expected = pins(self.root)

    def fingerprint(self, request, original):
        # Narrow original-byte protocol, explicitly distinct from API JCS.
        return byte_sha(encoded({'scheme': 'W02-local-original-byte/v1',
            'principal': request['principal_ref'], 'scope': request['scope_ref'],
            'operation': 'local.counter.dispatch', 'request_sha256': byte_sha(original)}))

    def denied(self, evaluation):
        return {'authority_effect': 'none', 'posture': 'denied', 'evaluation': public_evaluation(evaluation),
                'started': False, 'outputs': [], 'retry_allowed': False, 'reconciliation_required': False}

    def dispatch(self, original_request, original_input, *, interruption=None, pending_observer=None):
        """Interruption hook is host-only fixture machinery, outside request bytes."""
        with self.locked():
            journal = self.verify()
            require(byte_sha((TOOLS/'counter.py').read_bytes()) == self.authority.adapter_sha256,
                    'selected adapter original bytes changed')
            # Neither a prepare/evaluate response nor an existing receipt bypasses this.
            evaluation = self.authority.check(original_request)
            if evaluation['posture'] != 'permitted':
                return self.denied(evaluation)
            request = evaluation['request']; grant = evaluation['grant']
            require(byte_sha(original_input) == request['input_sha256'], 'original Tool input binding changed')
            require(len(original_input) <= grant.max_input_bytes, 'Tool input budget exceeded')
            payload = parse(original_input)
            require(Draft202012Validator(INPUT_CONTRACT).is_valid(payload), 'Tool input contract rejected')
            require(evaluation['tool_contract']['input_contract_ref'] == 'protocol:w02-counter-input:'+byte_sha(encoded(INPUT_CONTRACT)), 'selected Tool input contract differs')
            require(evaluation['tool_contract']['output_contract_ref'] == 'protocol:w02-counter-output:'+byte_sha(encoded(OUTPUT_CONTRACT)), 'selected Tool output contract differs')
            fingerprint = self.fingerprint(request, original_request)
            namespace = (request['principal_ref'], request['scope_ref'], request['idempotency_key'])
            for entry in journal['entries']:
                if tuple(entry['namespace']) == namespace:
                    require(entry['fingerprint'] == fingerprint, 'idempotency-conflict')
                    return entry['receipt'] if entry.get('receipt') else self.uncertain(entry)
            require(not any(e['posture'] == 'pending' for e in journal['entries']), 'reconciliation-required before another effect')
            require(len(journal['entries']) < grant.max_actions, 'local action budget exceeded')
            # Reject before the effect if the possible result cannot fit its ceiling.
            old = self.tool.state()
            predicted = {'value': old['value'] + payload['increment'], 'action_id': 'protocol:w02-action:'+str(uuid.uuid4()), 'input_sha256': byte_sha(original_input)}
            require(len(encoded(predicted)) <= grant.max_output_bytes, 'Tool output budget exceeded')
            entry = {'action_id': predicted['action_id'], 'namespace': list(namespace), 'fingerprint': fingerprint,
                'request_sha256': byte_sha(original_request), 'input_sha256': byte_sha(original_input),
                'request_original_b64': base64.b64encode(original_request).decode('ascii'),
                'input_original_b64': base64.b64encode(original_input).decode('ascii'),
                'before': old, 'predicted': predicted, 'posture': 'pending', 'evaluation': public_evaluation(evaluation), 'receipt': None}
            journal['entries'].append(entry); self.save(journal)
            if pending_observer is not None:
                pending_observer(self.expected)
            if interruption == 'before-effect':
                return self.uncertain(entry)
            # Persisting pending may have consumed time or changed current permission.
            immediate = self.authority.check(original_request)
            if immediate['posture'] != 'permitted':
                entry['posture'] = 'failed'; entry['receipt'] = self.denied(immediate); self.save(journal)
                return entry['receipt']
            try:
                output = self.tool.execute(original_input, entry['action_id'])
                self.expected = pins(self.root)
                require(output == predicted and Draft202012Validator(OUTPUT_CONTRACT).is_valid(output), 'observed output mismatch')
                if interruption == 'after-effect':
                    return self.uncertain(entry)
                receipt = {'authority_effect': 'none', 'posture': 'completed', 'action_id': entry['action_id'],
                    'request_sha256': entry['request_sha256'], 'input_sha256': entry['input_sha256'],
                    'output_sha256': byte_sha((self.root/'counter.json').read_bytes()), 'output': output,
                    'evaluation': public_evaluation(immediate), 'started': True, 'retry_allowed': False,
                    'reconciliation_required': False, 'residue': []}
                entry['posture'] = 'completed'; entry['receipt'] = receipt; self.save(journal)
                return receipt
            except BaseException:
                # Tool might have committed before returning. Never rerun to find out.
                self.expected = pins(self.root)
                raise

    def uncertain(self, entry):
        return {'authority_effect': 'none', 'posture': 'indeterminate', 'action_id': entry['action_id'],
                'reconciliation_required': True, 'retry_allowed': False,
                'residue': ['protocol:w02-ledger-pending:'+entry['action_id']]}

    def reconcile(self, original_request, *, recovery_request=None):
        with self.locked():
            journal = self.verify()
            evaluation = self.authority.check(recovery_request or original_request, recovery=True)
            if evaluation['posture'] != 'permitted':
                return self.denied(evaluation)
            request = parse(original_request)
            recovery_actor = evaluation['request']
            require(recovery_actor['principal_ref'] == request['principal_ref']
                    and recovery_actor['scope_ref'] == request['scope_ref'], 'recovery scope differs from original action')
            fingerprint = self.fingerprint(request, original_request)
            namespace = [request['principal_ref'], request['scope_ref'], request['idempotency_key']]
            matches = [e for e in journal['entries'] if e['namespace'] == namespace]
            require(len(matches) == 1 and matches[0]['fingerprint'] == fingerprint, 'exact uncertain action unresolved')
            entry = matches[0]
            if entry['posture'] != 'pending':
                return entry['receipt']
            actual = self.tool.state()
            if actual == entry['predicted']:
                posture = 'completed'
            elif actual == entry['before']:
                posture = 'failed'
            else:
                return self.uncertain(entry)
            entry['posture'] = posture
            entry['receipt'] = {'authority_effect': 'none', 'posture': posture,
                'action_id': entry['action_id'], 'observational_recovery': True,
                'output': actual if posture == 'completed' else None,
                'retry_allowed': False, 'reconciliation_required': False,
                'counter_original_sha256': byte_sha((self.root/'counter.json').read_bytes()),
                'evaluation': public_evaluation(evaluation)}
            self.save(journal)
            return entry['receipt']


def public_evaluation(value):
    return {k: v for k, v in value.items() if k not in {'grant', 'tool_contract'}}
