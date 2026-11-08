"""Signed fixture core-output chain, without legacy phase execution."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1 import capture_parity, constructor_paths, phase_receipts, role_stage


def bind(path: str, raw: bytes) -> dict:
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}


class FixturePhaseChainTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='lc-u02-05-phases-')
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.layout = role_stage.DisposableLayout(
            PurePosixPath(str(root / 'out/legacy-phases')),
            PurePosixPath(str(root / 'snapshot')), 'legacy-phases')
        self.inputs = []
        for selected in (capture_parity.CAPTURE, capture_parity.CALLER):
            target = Path(self.layout.snapshot / selected['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / selected['path'], target)
            self.inputs.append(selected.copy())
        rows = role_stage.stage_rows(self.layout, lambda name: (REPO / name).read_bytes())
        episode = b'{"schema_version":"disposable-episode"}\n'
        role = b'{"schema_version":"disposable-role"}\n'
        controls = {'episode_contract': episode, 'context_native_role': role}
        control = {
            'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
            'authority_effect': 'none', 'instance': self.layout.instance,
            'output_family_path': str(self.layout.family),
            'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                              for item in rows],
            'episode_binding': bind(str(self.layout.family / 'source/episode-contract.json'), episode),
            'current_role_binding': bind(str(self.layout.family / 'source/context-native-role.json'), role),
            'status': 'staged-unqualified',
        }
        controls['construction_selection'] = (json.dumps(control, sort_keys=True) + '\n').encode()
        self.stage = constructor_paths.stage_30_membership(self.layout, rows, controls)
        for item in rows:
            leaf = Path(item['output']['path'])
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_bytes(item['bytes'])
        for name, suffix in constructor_paths.STAGE_CONTROLS.items():
            leaf = Path(self.layout.family / suffix)
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_bytes(controls[name])
        parity = capture_parity.DisposableT03Parity(self.layout, self.inputs, self.stage)
        self.key = Ed25519PrivateKey.generate()
        public = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        self.ledger = phase_receipts.DisposablePhaseChain(parity, public)

    def receipt(self, phase: str, *, changed: dict | None = None):
        outputs = []
        for suffix in phase_receipts.CORE_OUTPUTS[phase]:
            leaf = Path(self.layout.family / suffix)
            leaf.parent.mkdir(parents=True, exist_ok=True)
            raw = (json.dumps({'schema_version': 'synthetic-core-output/v1',
                               'phase': phase, 'path': suffix, 'authority_effect': 'none'},
                              sort_keys=True) + '\n').encode()
            leaf.write_bytes(raw)
            outputs.append(bind(str(leaf), raw))
        value = {
            'schema_version': phase_receipts.SCHEMA, 'authority_effect': 'none',
            'actual_owner_outcome': None, 'claim_ceiling': 'disposable-core-binding-only',
            'status': 'disposable-selected-unqualified',
            'instance': self.layout.instance, 'output_family_path': str(self.layout.family),
            'phase': phase, 'stage_digest': self.ledger.stage_digest,
            'predecessor_receipt_sha256': self.ledger._selected[-1][1] if self.ledger._selected else None,
            'fixture_issuer_sha256': self.ledger.issuer_sha256,
            'fixture_run_nonce': self.ledger.run_nonce,
            'input_bindings': self.ledger.expected_inputs(phase),
            'output_bindings': outputs,
        }
        if changed:
            value.update(changed)
        raw = phase_receipts.canonical_receipt(value)
        return raw, self.key.sign(raw), outputs

    def test_exact_four_phase_core_selection(self):
        prior = None
        for phase in phase_receipts.PHASES:
            raw, signature, outputs = self.receipt(phase)
            selected = self.ledger.append(raw, signature)
            self.assertEqual(selected['phase'], phase)
            self.assertEqual(selected['output_bindings'], outputs)
            self.assertEqual(json.loads(raw)['predecessor_receipt_sha256'], prior)
            prior = selected['receipt_sha256']
        self.assertEqual(self.ledger.selected_phases, phase_receipts.PHASES)
        self.assertEqual(self.ledger.verify_selected(), 4)
        with self.assertRaises(ValueError):
            self.ledger.append(raw, signature)

    def test_wrong_signer_output_and_predecessor_refuse(self):
        raw, signature, outputs = self.receipt('source')
        wrong = Ed25519PrivateKey.generate().sign(raw)
        with self.assertRaises(ValueError):
            self.ledger.append(raw, wrong)
        leaf = Path(outputs[0]['path'])
        leaf.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.ledger.append(raw, signature)
        raw, signature, _ = self.receipt('source', changed={'predecessor_receipt_sha256': '0' * 64})
        with self.assertRaises(ValueError):
            self.ledger.append(raw, signature)

    def test_prior_output_drift_and_receipt_replay_refused(self):
        raw, signature, outputs = self.receipt('source')
        self.ledger.append(raw, signature)
        fresh = phase_receipts.DisposablePhaseChain(self.ledger._parity,
            self.key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                               format=serialization.PublicFormat.Raw))
        self.assertNotEqual(fresh.run_nonce, self.ledger.run_nonce)
        with self.assertRaises(ValueError):
            fresh.append(raw, signature)
        Path(outputs[0]['path']).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.ledger.verify_selected()
        reader_raw, reader_signature, _ = self.receipt('reader')
        with self.assertRaises(ValueError):
            self.ledger.append(reader_raw, reader_signature)

    def test_cross_family_receipt_refused(self):
        raw, _, _ = self.receipt('source')
        altered = json.loads(raw)
        altered['output_family_path'] = '/tmp/another/legacy-phases'
        candidate = phase_receipts.canonical_receipt(altered)
        with self.assertRaises(ValueError):
            self.ledger.append(candidate, self.key.sign(candidate))

    def test_mutated_internal_stage_and_prior_row_refused(self):
        self.ledger._stage_rows[0]['sha256'] = '0' * 64
        raw, signature, _ = self.receipt('source')
        with self.assertRaises(ValueError):
            self.ledger.append(raw, signature)
        self.ledger._stage_rows[0].update(self.stage[sorted(self.stage)[0]])
        raw, signature, outputs = self.receipt('source')
        self.ledger.append(raw, signature)
        changed = b'changed predecessor leaf\n'
        Path(outputs[0]['path']).write_bytes(changed)
        self.ledger._selected[0][2][0]['sha256'] = hashlib.sha256(changed).hexdigest()
        reader_raw, reader_signature, _ = self.receipt('reader')
        with self.assertRaises(ValueError):
            self.ledger.append(reader_raw, reader_signature)

    def test_two_core_outputs_hardlink_alias_refused(self):
        raw, _, outputs = self.receipt('source')
        first = Path(outputs[0]['path'])
        second = Path(outputs[1]['path'])
        second.unlink()
        os.link(first, second)
        value = json.loads(raw)
        value['output_bindings'][1]['sha256'] = outputs[0]['sha256']
        candidate = phase_receipts.canonical_receipt(value)
        with self.assertRaises(ValueError):
            self.ledger.append(candidate, self.key.sign(candidate))

    def test_reordered_and_unselected_core_path_refuse(self):
        raw, signature, outputs = self.receipt('source')
        bad = json.loads(raw)
        bad['output_bindings'] = list(reversed(outputs))
        altered = phase_receipts.canonical_receipt(bad)
        with self.assertRaises(ValueError):
            self.ledger.append(altered, self.key.sign(altered))
        bad['output_bindings'] = outputs.copy()
        bad['output_bindings'][0] = bind(str(self.layout.family / 'source/other.json'), b'x')
        altered = phase_receipts.canonical_receipt(bad)
        with self.assertRaises(ValueError):
            self.ledger.append(altered, self.key.sign(altered))
        bad['output_bindings'] = outputs
        bad['phase'] = 'reader'
        altered = phase_receipts.canonical_receipt(bad)
        with self.assertRaises(ValueError):
            self.ledger.append(altered, self.key.sign(altered))

    def test_duplicate_and_nonfinite_signed_json_refuse(self):
        raw, _, _ = self.receipt('source')
        duplicate = raw[:-2] + b',"phase":"source"}\n'
        with self.assertRaises(ValueError):
            self.ledger.append(duplicate, self.key.sign(duplicate))
        nonfinite = raw.replace(b'"actual_owner_outcome":null', b'"actual_owner_outcome":NaN')
        with self.assertRaises(ValueError):
            self.ledger.append(nonfinite, self.key.sign(nonfinite))


if __name__ == '__main__':
    unittest.main()
