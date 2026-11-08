"""In-memory probe for the emitted Context emit seam; no writer or transport."""
from __future__ import annotations

import hashlib
import json
import secrets
import sys
import types
from pathlib import Path

import admission

MODEL_PATH = admission.REPO / 'implementation/lab-runtime/local-host/context-construction-0003/completion_model.py'
MODEL_SHA = '86c4303f94dcc4b862552de3bf252e5e897b80e8ba88a118f3d6151cc5025123'
CLAIM = 'Actual historical construction delivery at its recorded expiry; later use must revalidate current source, host permission and expiry.'
LEAVES = ('request.json', 'authentication-proof.json', 'trusted-context.json',
          'host-permission-public.json',
          *(f'artifacts/{number:02d}.json' for number in range(30)),
          'artifact-index.json', 'delivery.json', 'lesson-selection.json',
          'delivery-provenance.json', 'build-result.json', 'manifest.json')
if len(LEAVES) != 40:
    raise RuntimeError('closed inert Context leaf schedule differs')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class Refused(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def model():
    raw = admission.read_exact(MODEL_PATH, MODEL_SHA)
    name = '_ctx_inert_model_' + secrets.token_hex(12)
    module = types.ModuleType(name)
    module.__file__ = str(MODEL_PATH)
    sys.modules[name] = module
    exec(compile(raw, str(MODEL_PATH), 'exec'), module.__dict__)
    return module


class InertTranscript:
    """Scripted ACK assertions test order only; they are not mediator receipts."""

    def __init__(self, out: Path, binding, source_binding: dict, fault: str | None = None):
        self.out = out
        self.binding = binding
        self.source_binding = source_binding
        self.fault = fault
        self.rows = []
        self.trace = []
        self.poisoned = False
        self.M = model()

    def emit(self, path: Path, raw: bytes):
        require(not self.poisoned, 'inert attempt already poisoned or completed')
        try:
            require(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024,
                    'bounded exact emitted bytes required')
            index = len(self.rows)
            require(index < 40 and path == self.out / LEAVES[index], 'emitted leaf order differs')
            self.trace.append(('EMIT', LEAVES[index], sha(raw)))
            if index < 39:
                self.rows.append(self.binding(path, raw))
                return
            self._finish(raw)
            self.poisoned = True  # completed attempts are never reused
        except BaseException:
            self.poisoned = True  # no retry after any admitted protocol fault
            raise

    def _finish(self, raw: bytes):
        try:
            manifest = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as error:
            raise Refused('manifest JSON differs') from error
        keys = {'schema_version', 'files', 'source_manifest_binding', 'authority_effect',
                'actual_owner_outcome', 'delivery_binding', 'provenance_binding', 'claim_ceiling'}
        require(type(manifest) is dict and set(manifest) == keys and
                manifest['schema_version'] == 'lab-actual-context-delivery-package/v1-candidate' and
                manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None and
                manifest['claim_ceiling'] == CLAIM and
                manifest['files'] == sorted(self.rows, key=lambda row: row['path']) and
                manifest['source_manifest_binding'] == self.source_binding and
                manifest['delivery_binding'] == self.rows[LEAVES.index('delivery.json')] and
                manifest['provenance_binding'] == self.rows[LEAVES.index('delivery-provenance.json')],
                'original-profile manifest/39-row binding differs')
        M = self.M
        digest = sha(raw)
        selected = M.Selection(
            'synthetic-attempt', 'synthetic-peer', digest,
            sha(b'manifest-request:' + raw), sha(b'manifest-response:' + raw), digest,
            sha(b'finish-request:' + raw), sha(b'finish-response:' + raw),
            sha(b'model-request:' + raw), sha(b'inventory:' + raw),
            sha(b'client-close:' + raw), 'synthetic-selected-finish-ack-schema')
        state = M.begin(selected)
        common = {'attempt': selected.attempt, 'peer': selected.peer}
        ack = common | {'ordinal': 40, 'manifest_sha256': digest,
                        'request_sha256': selected.manifest_request_sha256,
                        'response_sha256': selected.manifest_response_sha256,
                        'selected_leaf_sha256': digest,
                        'prior_39_durable': True, 'release_private_ack': True,
                        'private_root_absent': True, 'build_result_durable': True,
                        'manifest_durable': True, 'manifest_readback_fsync': True}
        if self.fault == 'manifest_ack_loss':
            ack = None
        if ack is None:
            raise Refused('synthetic manifest ACK lost')
        state = M.next_state(state, 'MANIFEST_EMIT_ACK', ack)
        self.trace.append(('MANIFEST_EMIT_ACK', state.step))
        require(state.step == 'await_finish_send', 'manifest ACK rejected')
        sent = common | {'ordinal': 41, 'action_payload': {},
                         'request_sha256': selected.finish_request_sha256,
                         'send_count': 1, 'transport_send_observed': True}
        if self.fault == 'finish_send_loss':
            raise Refused('synthetic FINISH send lost')
        state = M.next_state(state, 'FINISH_SENT', sent)
        self.trace.append(('FINISH_SENT', state.step))
        require(state.step == 'await_finish_ack' and state.finish_send_count == 1,
                'FINISH send rejected')
        finish_ack = common | {'ordinal': 41, 'request_sha256': selected.finish_request_sha256,
                               'response_sha256': selected.finish_response_sha256,
                               'model_request_sha256': selected.model_request_sha256,
                               'inventory_sha256': selected.inventory_sha256,
                               'schema_version': selected.finish_ack_schema, 'effect': 'none',
                               'original_profile_valid': True, 'forty_leaves_valid': True,
                               'thirty_nine_rows_valid': True, 'writer_readback': True,
                               'writer_closed': self.fault != 'writer_close_failure',
                               'private_root_absent': True, 'completion_observed': True}
        if self.fault == 'finish_ack_loss':
            raise Refused('synthetic FINISH ACK lost')
        state = M.next_state(state, 'FINISH_ACK', finish_ack)
        self.trace.append(('FINISH_ACK', state.step))
        require(state.step == 'await_client_close', 'FINISH ACK rejected')
        close = common | {'close_count': 1, 'checked': self.fault != 'client_close_failure',
                          'close_receipt_sha256': selected.close_receipt_sha256}
        state = M.next_state(state, 'CLIENT_CLOSED', close)
        self.trace.append(('CLIENT_CLOSED', state.step))
        require(state.step == 'summary_permitted', 'checked client close failed')
