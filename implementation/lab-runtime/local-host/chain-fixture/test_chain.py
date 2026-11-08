import copy
from datetime import datetime, timedelta, timezone
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

import chain


WORK = {"local_project_state": "project-state:fixture:1",
        "work_version": "work:fixture@1.0.0", "source_snapshot_digest": "a" * 64}
NOW = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)
KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
PUBLIC = KEY.public_key().public_bytes(serialization.Encoding.Raw,
                                       serialization.PublicFormat.Raw).hex()
WORK_SHA = chain.sha(chain.wire(WORK))


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.body = chain.source_body(WORK, NOW)
        self.raw = chain.sign_source(self.body, KEY)

    def test_complete_four_phase_fixture(self):
        read = chain.read_source(self.raw, chain.SCOPE, NOW, PUBLIC, WORK_SHA)
        mapped = chain.map_source(read)
        view = chain.context_view(mapped, read, chain.SCOPE)
        self.assertEqual((view["node_count"], view["edge_count"], len(view["included_refs"])),
                         (15, 10, 25))
        self.assertEqual(view["source_body_sha256"], chain.sha(chain.wire(read)))

    def test_signed_body_tamper_refused(self):
        envelope = chain.plain_json(self.raw)
        envelope["body"]["records"][0]["value"] = "forged"
        envelope["body_sha256"] = chain.sha(chain.wire(envelope["body"]))
        with self.assertRaisesRegex(chain.Refused, "SOURCE_SIGNATURE"):
            chain.read_source(chain.wire(envelope), chain.SCOPE, NOW, PUBLIC, WORK_SHA)

    def test_wrong_scope_and_expired_period_refused(self):
        with self.assertRaisesRegex(chain.Refused, "SOURCE_SCOPE"):
            chain.read_source(self.raw, "scope:foreign", NOW, PUBLIC, WORK_SHA)
        with self.assertRaisesRegex(chain.Refused, "SOURCE_PERIOD"):
            chain.read_source(self.raw, chain.SCOPE, NOW + timedelta(minutes=20), PUBLIC, WORK_SHA)

    def test_foreign_key_or_work_receipt_refused(self):
        with self.assertRaisesRegex(chain.Refused, "SOURCE_SELECTED_INPUT_BINDING"):
            chain.read_source(self.raw, chain.SCOPE, NOW, "00" * 32, WORK_SHA)
        with self.assertRaisesRegex(chain.Refused, "SOURCE_SELECTED_INPUT_BINDING"):
            chain.read_source(self.raw, chain.SCOPE, NOW, PUBLIC, "00" * 32)

    def test_duplicate_json_key_refused(self):
        with self.assertRaises(chain.Refused):
            chain.plain_json(b'{"x":1,"x":2}')

    def test_mapping_mutation_refused_by_context(self):
        mapping = chain.map_source(self.body)
        mapping["nodes"][0]["label"] = "forged"
        with self.assertRaisesRegex(chain.Refused, "CONTEXT_MAPPING_BINDING"):
            chain.context_view(mapping, self.body, chain.SCOPE)

    def test_foreign_context_scope_refused(self):
        mapping = chain.map_source(self.body)
        with self.assertRaisesRegex(chain.Refused, "CONTEXT_SCOPE"):
            chain.context_view(mapping, self.body, "scope:foreign")

    def test_duplicate_relation_refuses_source_read(self):
        body = copy.deepcopy(self.body)
        body["relations"][1]["id"] = body["relations"][0]["id"]
        with self.assertRaisesRegex(chain.Refused, "SOURCE_SHAPE"):
            chain.read_source(chain.sign_source(body, KEY), chain.SCOPE, NOW, PUBLIC, WORK_SHA)


if __name__ == "__main__":
    unittest.main()
