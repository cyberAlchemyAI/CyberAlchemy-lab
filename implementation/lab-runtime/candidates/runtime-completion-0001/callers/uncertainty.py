"""Keep the primary refusal distinct from later caller and cleanup failures."""
from dataclasses import dataclass, field
import re

from lab_contracts.codec import need


def _code(value):
    need(type(value) is str and re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}', value) is not None,
         'FAILURE_CODE')


def classify_reply(reply, *, operation_id, expected_call_id=None,
                   expected_request_sha256=None, expected_operation=None,
                   domain_verified=False):
    """Classify the outer transport envelope before touching domain message.

    This is an inert decision. ``domain_verified`` means the selected checker
    has validated the entire domain reply/profile/schema; this function also
    checks its exact original call/operation binding. ``inspect_operation_id`` instructs the owning
    caller to inspect its exact durable operation before any later action; it
    does not perform inspection or give authority to redispatch.
    """
    need(type(operation_id) is str and bool(operation_id), 'OPERATION_ID')
    need(type(domain_verified) is bool, 'DOMAIN_VERIFICATION')
    identity_current = (type(expected_call_id) is str and bool(expected_call_id)
                        and type(expected_request_sha256) is str
                        and re.fullmatch(r'[0-9a-f]{64}', expected_request_sha256) is not None)
    if type(reply) is not dict:
        return _classification('unknown', 'MALFORMED_ENVELOPE', operation_id, True)
    if 'kind' not in reply:
        if (not identity_current
                or set(reply) != {'schema_version', 'call_id', 'request_byte_sha256',
                                  'code', 'public_message', 'effect_may_have_started',
                                  'recovery_policy', 'authority_effect'}
                or reply.get('schema_version') != 'lab-api-transport-error/v1-candidate'
                or reply.get('call_id') != expected_call_id
                or reply.get('request_byte_sha256') != expected_request_sha256
                or reply.get('authority_effect') != 'none'
                or type(reply.get('public_message')) is not str
                or not reply['public_message'] or len(reply['public_message']) > 1024
                or type(reply.get('effect_may_have_started')) is not bool
                or reply.get('recovery_policy') not in ('no-retry', 'inspect-first')
                or reply.get('code') not in ('malformed-json', 'invalid-envelope',
                    'unauthenticated-channel', 'unsupported-protocol',
                    'unsupported-operation', 'invalid-call-id', 'input-too-large',
                    'deadline-exceeded')):
            return _classification('unknown', 'MALFORMED_TRANSPORT', operation_id, True)
        if (reply['effect_may_have_started'] and reply['recovery_policy'] != 'inspect-first'):
            return _classification('unknown', 'MALFORMED_TRANSPORT', operation_id, True)
        if (reply['code'] in ('malformed-json', 'invalid-envelope',
                'unauthenticated-channel', 'unsupported-protocol',
                'unsupported-operation', 'invalid-call-id', 'input-too-large')
                and (reply['effect_may_have_started'] or reply['recovery_policy'] != 'no-retry')):
            return _classification('unknown', 'MALFORMED_TRANSPORT', operation_id, True)
        if reply['effect_may_have_started'] or reply['recovery_policy'] == 'inspect-first':
            return _classification('unknown', 'TRANSPORT_UNCERTAIN', operation_id, True)
        return _classification('refused-no-effect', 'TRANSPORT_REFUSED', operation_id, False)
    kind = reply['kind']
    request_binding = reply.get('request_binding')
    if (not identity_current or type(expected_operation) is not str
            or not expected_operation or reply.get('call_id') != expected_call_id
            or reply.get('operation') != expected_operation
            or type(request_binding) is not dict
            or request_binding.get('sha256') != expected_request_sha256
            or kind not in ('result', 'error')
            or reply.get('schema_version') != 'lab-api-reply/v2-candidate'):
        return _classification('unknown', 'MALFORMED_DOMAIN', operation_id, True)
    # Domain validation belongs to the selected API contract checker. A bare
    # kind/message from an unverified reply cannot establish completion.
    if not domain_verified or type(reply.get('message')) is not dict:
        return _classification('unknown', 'UNVERIFIED_DOMAIN', operation_id, True)
    if kind == 'result':
        return _classification('completed', 'DOMAIN_RESULT', operation_id, False)
    return _classification('unknown', 'DOMAIN_ERROR_INSPECT', operation_id, True)


def _classification(state, code, operation_id, inspect):
    return {'schema_version': 'lab-caller-reply-classification/v1',
            'state': state, 'code': code,
            'effect_state': 'none' if state == 'refused-no-effect' else
                            'observed' if state == 'completed' else 'unknown',
            'inspect_operation_id': operation_id if inspect else None,
            'retry_allowed': False, 'continue_positive': state == 'completed',
            'authority_effect': 'none'}


@dataclass
class FailureChain:
    primary_code: str | None = None
    caller_codes: list[str] = field(default_factory=list)
    cleanup_codes: list[str] = field(default_factory=list)
    effect_state: str = 'none'
    response_received: bool = True

    def primary(self, code):
        _code(code)
        if self.primary_code is None:
            self.primary_code = code
        else:
            self.caller_codes.append(code)

    def caller(self, code):
        _code(code)
        self.caller_codes.append(code)

    def cleanup(self, code):
        _code(code)
        self.cleanup_codes.append(code)

    def lost_response(self):
        self.response_received = False
        if self.effect_state != 'observed':
            self.effect_state = 'unknown'

    def public(self):
        need(self.effect_state in ('none', 'observed', 'unknown'), 'EFFECT_STATE')
        return {'schema_version': 'lab-caller-failure-summary/v1',
                'primary_failure': self.primary_code,
                'caller_failure_count': len(self.caller_codes),
                'cleanup_failure_count': len(self.cleanup_codes),
                'effect_state': self.effect_state,
                'response_received': self.response_received,
                'retry_allowed': False if self.effect_state == 'unknown' or not self.response_received else None,
                'authority_effect': 'none'}

    def protected(self):
        """Return only typed codes; raw exception messages remain with the caller."""
        return {'primary_failure': self.primary_code,
                'caller_failures': list(self.caller_codes),
                'cleanup_failures': list(self.cleanup_codes)}
