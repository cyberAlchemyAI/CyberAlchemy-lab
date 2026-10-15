import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from jsonschema import Draft202012Validator

PACKAGE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PACKAGE))
from verification import *


class WorkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = ROOT / os.environ['C12_PACKAGE']
        cls.audit = load(cls.package / 'audit.json'); cls.observed = load(cls.package / 'observed-episode.json')
        cls.archive = cls.package / 'branch.snapshot'; cls.archive_pin = byte_digest(cls.archive.read_bytes())
        cls.owned = TemporaryDirectory(prefix='lab-C12-independent-replay-'); cls.addClassCleanup(cls.owned.cleanup)
        cls.path = Path(cls.owned.name) / 'restored'
        cls.replayed = restore_archive(cls.archive, cls.archive_pin, cls.path)

    def test_actual_thirteen_member_audit(self):
        self.assertTrue(verify_audit_exact(self.audit))
        self.assertEqual(self.audit['member_count'], 13)
        self.assertEqual(len(self.audit['owner_authority_gaps']), 13)

    def test_changed_audit_boundary_rejected(self):
        value = copy.deepcopy(self.audit); value['members'][0]['requested_effect'] = 'activate'
        with self.assertRaisesRegex(RuntimeFault, 'member boundary'): verify_audit_exact(value)

    def test_omitted_source_check_rejected(self):
        value = copy.deepcopy(self.audit); value['members'][0]['source_checks'].pop()
        with self.assertRaisesRegex(RuntimeFault, 'source check'): verify_audit_exact(value)

    def test_self_asserted_owner_rejected(self):
        value = copy.deepcopy(self.audit); value['members'][0]['current_owner_authority_verified'] = True
        with self.assertRaisesRegex(RuntimeFault, 'fabricated owner'): verify_audit_exact(value)

    def test_actual_assessment_scope_is_explicit(self):
        assessment = load(self.package / 'assessment.json')
        self.assertTrue(assessment['actual_execution']); self.assertEqual(assessment['result'], 'PASS')
        self.assertFalse(assessment['human_satisfaction_observed']); self.assertFalse(assessment['repository_admission'])
        self.assertFalse(assessment['operational_lesson_created']); self.assertFalse(assessment['Product_benefit_claimed'])
        self.assertEqual(assessment['audit_binding'], binding(self.package / 'audit.json'))

    def test_Work_carrier_matches_real_result(self):
        work = load(self.package / 'work.json')
        Draft202012Validator(load(ROOT / 'authority/artifact-types/work/v1/schema.json')).validate(work)
        self.assertEqual(work['payload']['completion_state'], 'candidate-development-complete')
        self.assertEqual(work['payload']['output_refs'], [(self.package / name).relative_to(ROOT).as_posix() for name in ('audit.json', 'assessment.json')])
        self.assertIn('#sha256=', work['evidence_refs'][0])

    def test_signed_local_transaction_has_exact_Work(self):
        version = self.observed['local_Work_version_ref']; subject = self.replayed['projection']['subjects'][version]
        self.assertEqual(subject['effective_state'], 'local-admitted-current')
        self.assertEqual(subject['record'], load(self.package / 'work.json'))
        self.assertEqual(self.replayed['head']['sequence'], 1)
        self.assertEqual(len(self.replayed['transactions'][1]['decision_cores']), 1)
        self.assertEqual(self.observed['repository_admissions_applied'], 0)

    def test_original_archive_excludes_private_and_memory_bytes(self):
        value, files = decode_archive(self.archive, self.archive_pin)
        self.assertEqual(len(files), 5)
        self.assertFalse(value['private_key_included']); self.assertFalse(value['Session_memory_included'])
        self.assertTrue(self.observed['old_Agent_invalidated']); self.assertTrue(self.observed['short_memory_erased'])
        self.assertEqual(self.observed['context_action_permission'], 'none')

    def test_wrong_archive_pin_rejected(self):
        with self.assertRaisesRegex(RuntimeFault, 'archive pin'): decode_archive(self.archive, '0' * 64)

    def test_restore_never_overwrites_existing_store(self):
        before = (self.path / 'HEAD.json').read_bytes()
        with self.assertRaisesRegex(RuntimeFault, 'new isolated path'): restore_archive(self.archive, self.archive_pin, self.path)
        self.assertEqual(before, (self.path / 'HEAD.json').read_bytes())

    def test_fresh_process_replays_actual_committed_Work(self):
        data = load(self.archive)
        control = Path(self.owned.name) / 'controls.json'; control.write_bytes(encoded({'path': str(self.path), 'pins': data['project_pins']}))
        code = 'import sys,json;from verification import *;c=load(sys.argv[1]);r=full_replay(c["path"],ROOT,ROOT,ReplayPins(**c["pins"]),require_current=True);print(json.dumps({"head":r["head"]["transaction_digest"],"transactions":len(r["transactions"])}))'
        result = subprocess.run([sys.executable, '-c', code, str(control)], cwd=PACKAGE, capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'head': self.replayed['head']['transaction_digest'], 'transactions': 2})

    def test_original_execution_sources_remain_exact(self):
        for row in load(self.package / 'execution-manifest.json')['files']:
            self.assertEqual(byte_digest((ROOT / row['path']).read_bytes()), row['sha256'])
