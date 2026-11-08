"""Join selected role projection to the original checkpoint verification kernel."""

import importlib
from datetime import timedelta
from pathlib import Path
import sys
import unittest

import test_role_projection as projection

ROOT = projection.ROOT
governance = projection.governance
selection = projection.selection
sha = projection.sha
encoded = projection.encoded
utc = projection.utc

sys.path.insert(0, str(ROOT / "product/lab/release-candidates/v1/interface"))
kernel_tests = importlib.import_module("checkpoint-resolution-v1.test_kernel")


def joined():
    fixture = kernel_tests.Resolution("test_01_actual_independent_owner_and_channel_signatures")
    fixture.setUp()
    host, selected = selection()
    owner = selected["recognized_owners"][0]
    key = fixture.owner_key.public_key().public_bytes_raw().hex()
    owner["public_key_hex"] = key
    recognition_ref = owner["recognition_binding"]["ref"]
    recognition = host.document(owner["recognition_binding"])
    recognition["public_key_hex"] = key
    host.rows[recognition_ref] = encoded(recognition)
    owner["recognition_binding"]["sha256"] = sha(host.rows[recognition_ref])
    required = fixture.required[0]
    required["owner_principal_ref"] = owner["principal_ref"]
    required["owner_role_ref"] = owner["role_ref"]
    required["recognition_binding"] = owner["recognition_binding"]
    fixture.materials[recognition_ref] = host.rows[recognition_ref]
    fixture.owners = governance.recognition(host, selected)
    fixture.select("approve-exact-effect")
    return fixture, host, selected


class CheckpointRoleJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        projection.SelectedRoleProjectionTests.setUpClass()

    def test_current_role_and_key_verify_signed_checkpoint(self):
        fixture, _, _ = joined()
        result = fixture.call()
        self.assertTrue(result["all_required_members_authorized"])
        self.assertEqual(result["actual_effects_applied"], 0)

    def test_expired_owner_key_refuses_at_checkpoint(self):
        fixture, _, _ = joined()
        pair = next(iter(fixture.owners))
        fixture.owners[pair]["expires_at"] = utc(fixture.now - timedelta(seconds=1))
        with self.assertRaisesRegex(ValueError, "recognition absent, changed or expired"):
            fixture.call()

    def test_future_owner_key_refuses_at_checkpoint(self):
        fixture, _, _ = joined()
        pair = next(iter(fixture.owners))
        fixture.owners[pair]["not_before"] = utc(fixture.now + timedelta(seconds=1))
        with self.assertRaisesRegex(ValueError, "recognition absent, changed or expired"):
            fixture.call()

    def test_revoked_assignment_refuses_before_checkpoint(self):
        _, host, selected = joined()
        binding = selected["recognized_owners"][0]["assignment_binding"]
        record = host.document(binding)
        record["assignment_state"] = "revoked"
        host.rows[binding["ref"]] = encoded(record)
        binding["sha256"] = sha(host.rows[binding["ref"]])
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)


if __name__ == "__main__":
    unittest.main()
