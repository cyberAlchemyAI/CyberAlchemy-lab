"""Causal, effect-disabled Context public closure tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import closure as C


class ClosureTests(unittest.TestCase):
    def test_exact_public_inventory_and_explicit_hold(self):
        result = C.verify_public()
        self.assertEqual(result['status'], 'PUBLIC_59_EXACT_PASS')
        self.assertEqual((result['api_v25'], result['fact_scope'], result['carrier_rows']),
                         (34, 4, 21))
        self.assertEqual(result['protected_archives_excluded'], 6)
        self.assertEqual(result['development_authorization'], 'UNMINTED')
        self.assertEqual(result['mapper_package'], 'UNSELECTED')
        with self.assertRaisesRegex(C.Refused, 'fresh Mapper'):
            C.final_context_source_manifest()
        with self.assertRaisesRegex(C.Refused, 'effect-disabled'):
            C.launch_context()

    def test_changed_selector_rejected_before_historical_or_target_open(self):
        original = json.loads((C.HERE / 'public-selection.json').read_bytes())
        changed = copy.deepcopy(original)
        changed['public_rows'][0]['path'] = '/tmp/branch.snapshot'
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'public-selection.json').write_text(json.dumps(changed))
            touched = []
            real = C.read_exact
            def observed(path, pin):
                touched.append(str(path))
                return real(path, pin)
            with mock.patch.object(C, 'HERE', Path(temp)), mock.patch.object(C, 'read_exact', observed):
                with self.assertRaisesRegex(C.Refused, 'bytes differ'):
                    C.verify_public()
            self.assertEqual(touched, [str(Path(temp) / 'public-selection.json')])

    def test_closed_selection_rejects_protected_and_reused_grant(self):
        selected = json.loads((C.HERE / 'public-selection.json').read_bytes())
        historical = json.loads(C.read_exact(C.HISTORICAL, C.HISTORICAL_SHA))
        changed = copy.deepcopy(selected)
        changed['public_rows'][0]['path'] = 'private/branch.snapshot'
        with self.assertRaisesRegex(C.Refused, 'protected or unselected'):
            C.validate_selection(changed, historical)
        changed = copy.deepcopy(selected)
        changed['development_authorization'] = 'REUSED_HISTORICAL'
        with self.assertRaisesRegex(C.Refused, 'effect-disabled'):
            C.validate_selection(changed, historical)

    def test_public_byte_change_and_growth_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'public.json'
            path.write_bytes(b'public')
            self.assertEqual(C.read_exact(path, C.sha(b'public')), b'public')
            path.write_bytes(b'changed')
            with self.assertRaisesRegex(C.Refused, 'bytes differ'):
                C.read_exact(path, C.sha(b'public'))
            path.write_bytes(b'')
            with mock.patch.object(C.os, 'read', lambda fd, count: b'x' * count):
                with self.assertRaisesRegex(C.Refused, 'grew during read'):
                    C.read_exact(path, C.sha(b''))

    def test_same_family_reader_binding_requires_actual_selected_bytes(self):
        selection = json.loads(C.read_exact(
            C.REPO / 'implementation/lab-runtime/local-host/context-integration-0002/selection.json',
            '16b46adf47f2f5c1482de4bd23597b32f49185d9c02d9e8d6a5dbdcaba78ae65'))
        with tempfile.TemporaryDirectory() as temp:
            family = Path(temp) / 'new-family'
            reader = family / 'reader'
            reader.mkdir(parents=True)
            (reader / 'reader.py').write_bytes(Path(selection['reader']['reader_code_path']).read_bytes())
            (reader / 'source-manifest.json').write_bytes(
                Path(selection['reader']['source_manifest_path']).read_bytes())
            with mock.patch.object(C, 'FAMILY', str(family)):
                candidate = json.loads(C.project_reader_binding(family))
                self.assertEqual(candidate['code_binding']['sha256'], C.READER_CODE_SHA)
                self.assertEqual(candidate['entrypoint_ref'], str(reader / 'reader.py') +
                                 '#SelectedReader.open_signed')
                self.assertEqual(candidate['authority_effect'], 'none')
                (reader / 'reader.py').write_bytes(b'unreviewed reader')
                with self.assertRaises(C.Refused):
                    C.project_reader_binding(family)
                with self.assertRaisesRegex(C.Refused, 'same-family'):
                    C.project_reader_binding(Path('/tmp/legacy-live-reused'))

    def test_auth_projection_requires_fresh_path_and_has_no_grant(self):
        plan = C.auth_projection_plan('authorization/context-development.json', 'a' * 64)
        self.assertEqual(plan['old_path_assignments'], 1)
        self.assertEqual(plan['old_pin_assignments'], 1)
        self.assertEqual(plan['unguarded_auth_reads_to_replace'], 2)
        self.assertFalse(plan['authorization_file_created'])
        self.assertEqual(plan['final_projection'], 'REFUSED_PENDING_FRESH_AUTH_BYTES')
        projected = C.project_auth_pure('authorization/context-development.json', 'a' * 64)
        self.assertEqual(projected.count(b'_context_development_auth(self.source.sources.scope_ref)'), 2)
        self.assertEqual(projected.count(b'AUTH.read_bytes()'), 1)
        self.assertIn(b"sha(raw) == AUTH_SHA", projected)
        self.assertIn(b"value['authority_effect'] == 'none'", projected)
        with self.assertRaisesRegex(C.Refused, 'fresh development AUTH'):
            C.auth_projection_plan(
                'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json',
                'a' * 64)


if __name__ == '__main__':
    unittest.main(verbosity=2)
