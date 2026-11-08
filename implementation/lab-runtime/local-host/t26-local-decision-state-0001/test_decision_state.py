import unittest

from decision_state import DecisionError, DecisionState, Event, Target, digest


BODY = b'{"member":"fixture-a","effect":"local"}\n'
BASE = digest(b"base")
BUNDLE = digest(b"bundle")


def target(body=BODY, scope="local-import"):
    return Target.from_bytes(member="fixture-a", scope=scope,
                             base_digest=BASE, bundle_digest=BUNDLE, body=body)


class DecisionTests(unittest.TestCase):
    def test_four_choices_have_distinct_effects(self):
        expected = {"approve": ("approved", True),
                    "reject": ("rejected", False),
                    "defer": ("deferred", False),
                    "revise": ("revision_requested", False)}
        for choice, (state, importable) in expected.items():
            with self.subTest(choice=choice):
                model, selected = DecisionState(), target()
                event = Event(choice, selected, choice,
                              digest(b"new body") if choice == "revise" else None)
                self.assertEqual(model.apply(event, body=BODY), state)
                self.assertEqual(model.can_import(selected, body=BODY), importable)
                self.assertEqual(model.apply(event, body=BODY), state)

    def test_defer_can_be_followed_by_a_final_choice(self):
        model, selected = DecisionState(), target()
        first = Event("first", selected, "defer")
        model.apply(first, body=BODY)
        self.assertEqual(model.apply(Event("second", selected, "approve"), body=BODY),
                         "approved")
        self.assertEqual(model.apply(first, body=BODY), "deferred")
        self.assertEqual(model.status(selected), "approved")
        with self.assertRaisesRegex(DecisionError, "final disposition"):
            model.apply(Event("third", selected, "reject"), body=BODY)

    def test_changed_bytes_scope_base_or_bundle_cannot_reuse_a_decision(self):
        model, selected = DecisionState(), target()
        model.apply(Event("one", selected, "approve"), body=BODY)
        with self.assertRaisesRegex(DecisionError, "target bytes changed"):
            model.can_import(selected, body=BODY + b" ")
        for changed in (
            target(scope="release"),
            Target.from_bytes(member="fixture-a", scope="local-import",
                              base_digest=digest(b"changed base"), bundle_digest=BUNDLE,
                              body=BODY),
            Target.from_bytes(member="fixture-a", scope="local-import",
                              base_digest=BASE, bundle_digest=digest(b"changed bundle"),
                              body=BODY),
        ):
            self.assertFalse(model.can_import(changed, body=BODY))

    def test_event_id_collision_and_revision_invalidate_old_target(self):
        model, selected = DecisionState(), target()
        successor_body = b"revised member"
        successor = target(body=successor_body)
        self.assertEqual(model.apply(Event("one", selected, "revise",
                                           successor.body_digest), body=BODY),
                         "revision_requested")
        self.assertEqual(model.successor(selected), successor.body_digest)
        self.assertFalse(model.can_import(selected, body=BODY))
        self.assertEqual(model.status(successor), "pending")
        with self.assertRaisesRegex(DecisionError, "event id reused"):
            model.apply(Event("one", successor, "approve"), body=successor_body)
        with self.assertRaisesRegex(DecisionError, "final disposition"):
            model.apply(Event("two", selected, "approve"), body=BODY)

    def test_invalid_revision_and_target_inputs_refuse(self):
        selected = target()
        with self.assertRaisesRegex(DecisionError, "distinct exact successor"):
            Event("one", selected, "revise", selected.body_digest)
        with self.assertRaisesRegex(DecisionError, "invalid base_digest"):
            Target.from_bytes(member="fixture-a", scope="local-import",
                              base_digest="not-a-hash", bundle_digest=BUNDLE, body=BODY)
        with self.assertRaisesRegex(DecisionError, "exact bytes"):
            target(body="text")


if __name__ == "__main__":
    unittest.main()
