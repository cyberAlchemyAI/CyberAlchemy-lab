"""Client-side reply/recovery boundary. This module grants no host authority.

Schema/signature/currentness checks remain the selected host's responsibility.
No method here dispatches or retries an effect or restores a live resource.
"""
from dataclasses import dataclass, asdict
import copy
import re

KNOWN_CODES = frozenset(('unauthorized', 'unauthenticated-channel', 'deadline-exceeded',
    'invalid-contract', 'invalid-envelope', 'malformed-json', 'unsupported-protocol',
    'unsupported-operation', 'invalid-call-id', 'input-too-large', 'integrity-failed',
    'indeterminate', 'recovery-required', 'not-found', 'conflict', 'stale-source'))


def public_token(value):
    return re.sub(r'[^a-zA-Z0-9_.:-]', '_', str(value))[:80]


@dataclass(frozen=True)
class Decision:
    state: str
    envelope: str
    code: str | None
    next_action: str
    retry_allowed: bool = False
    effect_may_have_started: bool | None = None

    def record(self):
        return asdict(self)


def classify(reply):
    if not isinstance(reply, dict):
        return Decision('invalid', 'invalid', 'invalid-reply', 'stop')
    kind = reply.get('kind')
    message = reply.get('message')
    if kind in ('result', 'error') and isinstance(message, dict):
        if kind == 'result':
            return Decision('completed', 'domain-result', None, 'consume-result')
        code = message.get('code')
        safe_code = code if code in KNOWN_CODES else 'unknown-domain-error'
        uncertain = (code in ('indeterminate', 'recovery-required') or
                     message.get('retry_policy') == 'reconcile-first')
        if uncertain:
            return Decision('uncertain', 'domain-error', safe_code,
                            'inspect-owned-operation-then-reconcile', False, True)
        # A domain failure is not a universal assertion that no claim occurred.
        return Decision('refused', 'domain-error', safe_code, 'stop', False, None)
    if kind is None and reply.get('schema_version') == 'lab-api-transport-error/v1-candidate':
        code = reply.get('code')
        safe_code = code if code in KNOWN_CODES else 'unknown-transport-error'
        effect = reply.get('effect_may_have_started')
        if effect is True or reply.get('recovery_policy') == 'reconcile-first':
            return Decision('uncertain', 'transport-error', safe_code,
                            'inspect-owned-operation-then-reconcile', False, effect)
        if effect is False and reply.get('recovery_policy') == 'no-retry':
            return Decision('refused-no-effect', 'transport-error', safe_code, 'stop', False, False)
        return Decision('invalid', 'transport-error', safe_code, 'stop')
    return Decision('invalid', 'invalid', 'invalid-reply', 'stop')


class CallerBoundaryError(RuntimeError):
    def __init__(self, operation, decision):
        self.operation = public_token(operation)
        self.decision = decision
        # Do not forward raw request/domain/error/credential material in exception text.
        super().__init__(f'{self.operation}: {decision.state}/{decision.code}; '
                         f'{decision.next_action}; automatic retry disabled')


def result_message(reply, operation):
    decision = classify(reply)
    if decision.state != 'completed':
        raise CallerBoundaryError(operation, decision)
    return reply['message']


@dataclass(frozen=True)
class OwnedOperation:
    operation: str
    idempotency_key: str
    context_ref: str
    principal_ref: str
    original_call_sha256: str
    workspace_ref: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v for v in asdict(self).values()):
            raise ValueError('Exact independently selected ownership fields required')
        if not re.fullmatch('[0-9a-f]{64}', self.original_call_sha256):
            raise ValueError('Exact original call digest required')
        if self.operation == 'operation.inspect':
            raise ValueError('An inspection cannot authorize an effect recovery loop')


class RecoveryGate:
    """Only plan an owned read and consume its evidence; never construct a retry.

    Ownership fields are an independently supplied client selection, not new
    authentication. The actual host must repeat its original scope/Actor checks.
    """
    def __init__(self, owned, reply):
        if not isinstance(owned, OwnedOperation):
            raise ValueError('Explicit owned operation selection required')
        if classify(reply).state != 'uncertain':
            raise ValueError('Recovery gate requires an uncertain original outcome')
        self.owned = owned
        self.state = 'inspection-required'
        self.retry_allowed = False
        self.original_reply = copy.deepcopy(reply)

    def inspection_call(self, original, context, *, call_id):
        if (original.get('operation') != self.owned.operation or
            original.get('idempotency_key') != self.owned.idempotency_key or
            original.get('caller_context_ref') != self.owned.context_ref or
            context.get('context_ref') != self.owned.context_ref or
            context.get('principal_ref') != self.owned.principal_ref or
            not isinstance(call_id, str) or not call_id or call_id == original.get('call_id')):
            raise ValueError('Foreign or changed operation/context/key cannot be inspected here')
        actor = original.get('message', {}).get('actor')
        if not isinstance(actor, dict) or actor.get('principal_ref') != self.owned.principal_ref:
            raise ValueError('Original Actor does not match the owned principal')
        # Preserve independently selected profile, original deadline and budgets.
        # A expired read needs a separately authorized fresh call, not silent renewal.
        result = copy.deepcopy(original)
        result.update(operation='operation.inspect', call_id=call_id,
                      idempotency_key=None, expected_source_cut=None)
        message = {'schema_version': 'lab-operation-inspect-request/v1-candidate',
                   'request_ref': 'request:T04-inspect:' + public_token(call_id),
                   'actor': copy.deepcopy(actor),
                   'budget': copy.deepcopy(original['message']['budget']),
                   'lookup': {'operation': self.owned.operation,
                              'idempotency_key': self.owned.idempotency_key},
                   'authority_effect': 'none'}
        result['message'] = message
        self.state = 'inspection-planned'
        return result

    def observe_inspection(self, reply):
        if self.state != 'inspection-planned':
            raise ValueError('An exact owned inspection must be planned first')
        message = result_message(reply, 'operation.inspect')
        binding = message.get('original_call_binding')
        if (message.get('schema_version') != 'lab-operation-inspect-result/v1-candidate' or
            message.get('operation') != self.owned.operation or
            not isinstance(binding, dict) or
            binding.get('sha256') != self.owned.original_call_sha256 or
            message.get('retry_allowed') is not False or
            not isinstance(message.get('reconciliation_required'), bool) or
            (message['reconciliation_required'] and message.get('posture') != 'indeterminate') or
            (not message['reconciliation_required'] and message.get('posture') not in ('completed','failed'))):
            raise ValueError('Inspection evidence does not close the exact owned operation')
        self.state = ('reconciliation-required' if message['reconciliation_required'] else
                      'observed-completed' if message.get('posture') == 'completed' else
                      'observed-failed')
        # Even not-found/completed evidence grants no dispatch/retry authority.
        self.retry_allowed = False
        return {'state': self.state, 'retry_allowed': False,
                'operation': self.owned.operation,
                'original_call_sha256': self.owned.original_call_sha256,
                'next_action': 'independent-reconciliation-disposition' if
                               message['reconciliation_required'] else 'stop-no-redispatch',
                'authority_effect': 'none'}
