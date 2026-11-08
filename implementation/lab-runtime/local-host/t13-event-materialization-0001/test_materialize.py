"""Negative controls for the exact original predecessor-to-draft join."""

import copy
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import materialize as m


class MaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = m.parse(m.exact(m.ACCOUNT, m.ACCOUNT_SHA))
        cls.archive = m.parse(m.exact(m.ARCHIVE, m.ARCHIVE_SHA))

    def test_all_88_inert_native_events_have_original_lineage(self):
        drafts, rows = m.prepare(self.account, self.archive)
        sealed, bodies, _ = m.native_seal(drafts)
        self.assertEqual(len(sealed), 88)
        self.assertEqual({r['member_ref'] for r in rows},
                         {r['member_ref'] for r in self.account['rows']})
        for position, (event, body, row) in enumerate(zip(sealed, bodies, rows), 1):
            self.assertEqual(event['governance_cursor'], 88 + position)
            self.assertEqual(event['semantic_ref'], row['semantic_tuple'])
            self.assertEqual(event['previous_event_digest'],
                             row['predecessor_governance_tuple']['event_digest'])
            self.assertEqual(event['complete_resulting_governance_state']['authority_effect'], 'none')
            self.assertEqual(event['complete_resulting_governance_state']['candidate_or_maturity_status'],
                             'candidate-unadmitted')
            self.assertNotEqual(event['event_digest'], '0' * 64)
            self.assertTrue(body.endswith(b'\n'))

    def test_changed_predecessor_digest_refuses(self):
        account = copy.deepcopy(self.account)
        account['rows'][37]['predecessor_governance_tuple']['event_digest'] = '0' * 64
        with self.assertRaisesRegex(m.Refusal, 'predecessor tuple changed'):
            m.prepare(account, self.archive)

    def test_changed_semantic_tuple_refuses(self):
        account = copy.deepcopy(self.account)
        account['rows'][52]['semantic_tuple']['semantic_event_digest'] = '0' * 64
        with self.assertRaisesRegex(m.Refusal, 'intent semantic tuple changed'):
            m.prepare(account, self.archive)

    def test_changed_selected_intent_body_pin_refuses(self):
        account = copy.deepcopy(self.account)
        account['rows'][17]['intent_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(m.Refusal, 'selected file bytes changed'):
            m.prepare(account, self.archive)

    def test_relocated_root_resolves_from_module_and_refuses_missing_selection(self):
        with tempfile.TemporaryDirectory(prefix='cal-t13-relocation-') as location:
            target = Path(location) / 'implementation/lab-runtime/local-host/t13-event-materialization-0001/materialize.py'
            target.parent.mkdir(parents=True)
            shutil.copyfile(Path(m.__file__), target)
            spec = importlib.util.spec_from_file_location('_cal_t13_relocated', target)
            relocated = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(relocated)
            self.assertEqual(relocated.ROOT, Path(location))
            with self.assertRaisesRegex(relocated.Refusal, 'selected file absent'):
                relocated.exact(relocated.ACCOUNT, relocated.ACCOUNT_SHA)
            with self.assertRaisesRegex(relocated.Refusal, 'escapes selected checkout'):
                relocated.selected_binding({'path': '../wrong.json', 'sha256': '0' * 64})

    def test_symlinked_parent_cannot_redirect_selected_intent(self):
        with tempfile.TemporaryDirectory(prefix='cal-t13-path-') as location:
            root = Path(location) / 'checkout'
            outside = Path(location) / 'outside'
            root.mkdir()
            outside.mkdir()
            raw = b'{"technical":"same bytes"}\n'
            (outside / 'intent.json').write_bytes(raw)
            os.symlink(outside, root / 'linked')
            original = m.ROOT
            try:
                m.ROOT = root
                with self.assertRaisesRegex(m.Refusal, 'escapes checkout|symlinked ancestor'):
                    m.selected_binding({'path': 'linked/intent.json', 'sha256': m.sha(raw)})
            finally:
                m.ROOT = original

    def test_changed_original_archive_body_refuses(self):
        archive = copy.deepcopy(self.archive)
        key = next(k for k in archive['files'] if k.startswith('governance/'))
        archive['files'][key]['sha256'] = '0' * 64
        with self.assertRaisesRegex(m.Refusal, 'archive body changed'):
            m.prepare(self.account, archive)


if __name__ == '__main__':
    unittest.main()
