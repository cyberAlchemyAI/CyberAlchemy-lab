"""Disposable signed core-output selection for four external-root phases.

This verifies a scratch fixture signature and exact T03-held output bytes. It
does not execute the historical Source/reader/mapper/Context constructors or
attest their semantic manifests; no production phase or effect is enabled.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from .capture_parity import DisposableT03Parity, _single_link, CAPTURE
from .held_paths import _parse_closed
from .path_contract import canonical_path, require

PHASES = ('source', 'reader', 'mapped', 'context')
CORE_OUTPUTS = {
    'source': ('source/source-manifest.json', 'source/packages/0001/manifest.json',
               'source/packages/0001/period.json', 'source/packages/0001/build-result.json'),
    'reader': ('reader/source-manifest.json',),
    'mapped': ('mapped/source-manifest.json', 'mapped/packages/0001/manifest.json'),
    'context': ('context/source-manifest.json', 'context/packages/0001/manifest.json',
                'context/implementation-binding.json'),
}
SCHEMA = 'lab-T35-disposable-phase-core-receipt/v1-inactive'


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       allow_nan=False) + '\n').encode()


def canonical_receipt(value: dict) -> bytes:
    require(type(value) is dict, 'closed fixture receipt value required')
    return _encoded(value)


class DisposablePhaseChain:
    """Monotone fixture receipt selection; constructed files stay caller-owned."""

    def __init__(self, parity: DisposableT03Parity, issuer_public_key: bytes):
        require(type(parity) is DisposableT03Parity and type(issuer_public_key) is bytes and
                len(issuer_public_key) == 32, 'disposable T03 and exact fixture issuer required')
        parity.verify_stage()
        self._parity = parity
        self._issuer = Ed25519PublicKey.from_public_bytes(issuer_public_key)
        self._issuer_sha = _sha(issuer_public_key)
        self._run_nonce = os.urandom(32).hex()
        self._stage_rows = tuple(copy.deepcopy(parity._outputs[path]) for path in sorted(parity._outputs))
        self._stage_digest = _sha(_encoded(list(self._stage_rows)))
        self._selected: list[tuple[str, str, tuple[dict, ...]]] = []

    @property
    def stage_digest(self) -> str:
        return self._stage_digest

    @property
    def issuer_sha256(self) -> str:
        return self._issuer_sha

    @property
    def run_nonce(self) -> str:
        return self._run_nonce

    @property
    def selected_phases(self) -> tuple[str, ...]:
        return tuple(row[0] for row in self._selected)

    def expected_inputs(self, phase: str) -> list[dict]:
        require(phase in PHASES, 'closed phase required')
        if phase == 'source':
            return copy.deepcopy(list(self._stage_rows))
        previous = PHASES[:PHASES.index(phase)]
        require(self.selected_phases == previous, 'exact previous phases required')
        rows = [row for name, _, outputs, _, _ in self._selected for row in outputs]
        return copy.deepcopy(sorted(rows, key=lambda item: item['path']))

    def _verify_output(self, row: dict) -> None:
        path = Path(row['path'])
        _single_link(path)
        self._parity._check()
        observed = self._parity._capture_one(self._parity.layout.snapshot, row,
                                              code_sha256=CAPTURE['sha256'],
                                              selected_external=(row,))
        self._parity._check()
        _single_link(path)
        require(_sha(observed) == row['sha256'], 'phase output changed after T03 read')

    def _unchanged(self) -> None:
        require(_sha(_encoded(list(self._stage_rows))) == self._stage_digest,
                'selected fixture stage row map mutated')
        previous = None
        prior_rows = []
        for index, (phase, digest, outputs, raw, signature) in enumerate(self._selected):
            require(phase == PHASES[index] and _sha(raw) == digest,
                    'retained fixture phase receipt identity changed')
            try:
                self._issuer.verify(signature, raw)
            except InvalidSignature as error:
                raise ValueError('retained fixture phase signature changed') from error
            value = _parse_closed(raw)
            expected_inputs = list(self._stage_rows) if index == 0 else sorted(prior_rows, key=lambda item: item['path'])
            require(canonical_receipt(value) == raw and
                    value['phase'] == phase and value['stage_digest'] == self._stage_digest and
                    value['fixture_issuer_sha256'] == self._issuer_sha and
                    value['fixture_run_nonce'] == self._run_nonce and
                    value['predecessor_receipt_sha256'] == previous and
                    value['input_bindings'] == expected_inputs and
                    value['output_bindings'] == list(outputs),
                    'retained signed fixture phase selection mutated')
            prior_rows.extend(outputs)
            previous = digest

    def append(self, raw: bytes, signature: bytes) -> dict:
        require(type(raw) is bytes and 0 < len(raw) <= 1024 * 1024 and
                type(signature) is bytes and len(signature) == 64,
                'bounded signed fixture phase receipt required')
        phase = PHASES[len(self._selected)] if len(self._selected) < len(PHASES) else None
        require(phase is not None, 'four core phases already selected')
        self._unchanged()
        self._parity.verify_stage()
        for _, _, prior, _, _ in self._selected:
            for row in prior:
                self._verify_output(row)
        try:
            self._issuer.verify(signature, raw)
        except InvalidSignature as error:
            raise ValueError('fixture phase receipt signature differs') from error
        value = _parse_closed(raw)
        require(type(value) is dict and
                set(value) == {'schema_version', 'authority_effect', 'actual_owner_outcome',
                               'claim_ceiling', 'status', 'instance', 'output_family_path', 'phase',
                               'stage_digest', 'predecessor_receipt_sha256',
                               'fixture_issuer_sha256', 'fixture_run_nonce',
                               'input_bindings', 'output_bindings'} and
                canonical_receipt(value) == raw and value['schema_version'] == SCHEMA and
                value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None and
                value['claim_ceiling'] == 'disposable-core-binding-only' and
                value['status'] == 'disposable-selected-unqualified' and
                value['instance'] == self._parity.layout.instance and
                value['output_family_path'] == str(self._parity.layout.family) and
                value['phase'] == phase and value['stage_digest'] == self._stage_digest and
                value['fixture_issuer_sha256'] == self._issuer_sha and
                value['fixture_run_nonce'] == self._run_nonce and
                value['predecessor_receipt_sha256'] ==
                    (self._selected[-1][1] if self._selected else None) and
                value['input_bindings'] == self.expected_inputs(phase),
                'closed monotone fixture phase receipt differs')
        expected = [str(self._parity.layout.family / suffix) for suffix in CORE_OUTPUTS[phase]]
        outputs = value['output_bindings']
        require(type(outputs) is list and len(outputs) == len(expected) and
                [row['path'] for row in outputs if type(row) is dict and 'path' in row] == expected,
                'exact core phase output paths required')
        for row, path in zip(outputs, expected):
            require(type(row) is dict and set(row) == {'path', 'sha256'} and row['path'] == path and
                    type(row['sha256']) is str and len(row['sha256']) == 64,
                    'closed phase output binding required')
            canonical_path(path, absolute=True)
            self._verify_output(row)
        selected = tuple(copy.deepcopy(outputs))
        self._selected.append((phase, _sha(raw), selected, raw, signature))
        return {'phase': phase, 'receipt_sha256': _sha(raw),
                'output_bindings': copy.deepcopy(outputs),
                'authority_effect': 'none', 'fixture_only': True}

    def verify_selected(self) -> int:
        """Recheck retained signed bytes and current selected core output bytes."""
        self._unchanged()
        self._parity.verify_stage()
        for index, (phase, digest, outputs, raw, signature) in enumerate(self._selected):
            for row in outputs:
                self._verify_output(row)
        return len(self._selected)
