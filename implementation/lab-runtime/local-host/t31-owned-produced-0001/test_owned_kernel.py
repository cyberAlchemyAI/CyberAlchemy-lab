"""Synthetic host proofs isolate the private profile; no actual grant claim."""
import ast
import copy
import importlib
import inspect
import json
import unittest

import owned_kernel as K
from currentness import S
from host_headers import HostHeaders

F = importlib.import_module(S.J.K.__package__ + '.fixtures')


class OwnedKernelTests(unittest.TestCase):
    def setUp(self):
        self.message, self.facts = F.build()
        self.rows = self.facts['selected_headers']

    def selected(self, *, coordination=False, guard=lambda: None):
        def source(header):
            return None if coordination else copy.deepcopy(self.rows.get(header['version_ref']))
        def private(header):
            row = copy.deepcopy(self.rows.get(header['version_ref']))
            if row is None:
                return None
            row.update(posture='owned-coordination-current',
                       lineage_binding={'ref': 'fixture:private-coordination', 'sha256': 'a' * 64})
            return row
        return HostHeaders(source_resolver=source, coordination_resolver=private,
                           owned_resolver=None, guard=guard)

    def test_original_signed_source_plan_is_identical(self):
        expected = S.J.K.plan(self.message, **self.facts)
        self.facts['selected_headers'] = self.selected()
        self.assertEqual(K.plan(self.message, **self.facts), expected)

    def test_explicit_private_coordination_does_not_change_original_kernel(self):
        self.facts['selected_headers'] = self.selected(coordination=True)
        result = K.plan(self.message, **self.facts)
        self.assertEqual(result['next_run']['state'], 'inspected')
        self.assertFalse(result['event']['canonical_admission_granted'])
        self.assertFalse(result['work_satisfaction_asserted'])
        self.assertEqual(S.J.K.CURRENT, ('admitted-current', 'local-admitted-current'))
        strict = copy.deepcopy(self.rows)
        for row in strict.values():
            row['posture'] = 'owned-coordination-current'
        self.facts['selected_headers'] = strict
        with self.assertRaises(ValueError):
            S.J.K.plan(self.message, **self.facts)
        with self.assertRaisesRegex(ValueError, 'private owned'):
            K.plan(self.message, **self.facts)

    def test_wire_dictionary_and_invalid_lineage_refuse(self):
        with self.assertRaises(ValueError):
            K.plan(self.message, **self.facts)
        self.facts['selected_headers'] = HostHeaders(source_resolver=lambda h: None, owned_resolver=None,
            coordination_resolver=lambda h: {'artifact': h, 'posture': 'owned-coordination-current',
                                            'semantic_kind': 'fixture', 'lineage_binding': {}}, guard=lambda: None)
        with self.assertRaisesRegex(ValueError, 'lineage'):
            K.plan(self.message, **self.facts)

    def test_missing_obligation_foreign_actor_cut_and_scope_still_refuse(self):
        for name in ('authenticated_actor', 'current_cut', 'selected_obligations'):
            facts = copy.deepcopy(self.facts)
            facts[name] = {}
            facts['selected_headers'] = self.selected(coordination=True)
            with self.assertRaises(ValueError):
                K.plan(self.message, **facts)
        bad = copy.deepcopy(self.message)
        bad['input_artifacts'][0]['scope_ref'] = 'project:foreign'
        self.facts['selected_headers'] = self.selected(coordination=True)
        with self.assertRaises(ValueError):
            K.plan(bad, **self.facts)

    def test_guard_refusal_at_exit_prevents_returned_plan(self):
        calls = []
        def guard():
            calls.append(1)
            if len(calls) == 12:  # entry + two for each of five refs, then exit
                raise ValueError('fixture grant revoked before plan return')
        self.facts['selected_headers'] = self.selected(coordination=True, guard=guard)
        with self.assertRaisesRegex(ValueError, 'revoked'):
            K.plan(self.message, **self.facts)

    def test_only_explicit_profile_predicates_differ_from_original_plan(self):
        original = ast.parse(inspect.getsource(S.J.K.plan)).body[0]
        selected = ast.parse(inspect.getsource(K.plan)).body[0]
        # Every predicate except the typed currentness block and guarded entry/exit
        # is byte-for-byte equivalent in AST. This catches incidental weakening.
        selected.body = selected.body[:1] + selected.body[3:]
        selected.body.pop(-2)
        for node in ast.walk(selected):
            if isinstance(node, ast.For) and ast.unparse(node.target) == 'header':
                original_loop = next(n for n in ast.walk(original) if isinstance(n, ast.For)
                                     and ast.unparse(n.target) == 'header')
                node.body = original_loop.body
        self.assertEqual(ast.dump(selected, include_attributes=False), ast.dump(original, include_attributes=False))


if __name__ == '__main__':
    unittest.main()
