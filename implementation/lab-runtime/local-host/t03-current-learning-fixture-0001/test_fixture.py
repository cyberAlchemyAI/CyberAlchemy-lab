"""Cold contract tests using the actual selected lesson rule implementation."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fixture
from fixture import ROOT, bind, build, compact


FIXED = datetime(2026, 10, 22, 20, 0, tzinfo=timezone.utc)


class SyntheticLesson(unittest.TestCase):
    def setUp(self):
        self.rules_module, self.lesson, self.route, self.facts, self.read, self.originals = build(FIXED)
        self.rules = self.rules_module.Rules()

    def evaluate(self, route=None, facts=None, read=None):
        return self.rules.select(compact(self.route if route is None else route),
                                 self.facts if facts is None else facts,
                                 self.read if read is None else read)

    def test_01_exact_synthetic_candidate_is_selected_without_effect(self):
        result = self.evaluate()
        self.assertEqual(len(result.result['items']), 1)
        self.assertEqual(result.result['items'][0]['posture'], 'selected')
        self.assertEqual(result.result['items'][0]['reason'], 'exact-reviewed-current-applicable')
        self.assertEqual(result.applications_created, 0)
        self.assertEqual(result.authority_effect, 'none')
        self.assertEqual(len(result.checks), 1)

    def test_02_changed_cut_or_assignment_refuses(self):
        for field in ('source_cut', 'assignment'):
            with self.subTest(field=field):
                route = copy.deepcopy(self.route)
                if field == 'source_cut':
                    route[field]['commit_sha256'] = '0' * 64
                else:
                    route[field]['version_ref'] = 'agent-assignment:foreign@1'
                with self.assertRaises(self.rules_module.SelectionFault):
                    self.evaluate(route=route)

    def test_03_expired_candidate_is_omitted(self):
        facts = replace(self.facts, now=FIXED + timedelta(hours=25))
        row = self.evaluate(facts=facts).result['items'][0]
        self.assertEqual((row['posture'], row['reason'], row['expired']),
                         ('omitted', 'expired', True))

    def test_04_changed_evidence_refuses(self):
        evidence = self.lesson['payload']['evidence_refs'][0]
        def tampered(binding):
            if binding['ref'] == evidence:
                return b'changed independent evidence'
            return self.read(binding)
        with self.assertRaises(self.rules_module.SelectionFault):
            self.evaluate(read=tampered)

    def test_05_instruction_veto_omits(self):
        instructions = self.originals[self.facts.instruction_binding['ref']]
        replacement = copy.deepcopy(self.facts)
        from fixture import bind
        import json
        changed = json.loads(instructions)
        changed['veto_lesson_influence'] = True
        raw = compact(changed)
        new_binding = bind('fixture:T03-veto-instruction', raw)
        route = copy.deepcopy(self.route)
        route['instruction_precedence_binding'] = new_binding
        refs = dict(self.originals)
        refs[new_binding['ref']] = raw
        def read(binding):
            return refs[binding['ref']]
        replacement = replace(replacement, instruction_veto=True, instruction_binding=new_binding)
        row = self.evaluate(route=route, facts=replacement, read=read).result['items'][0]
        self.assertEqual((row['posture'], row['reason']),
                         ('omitted', 'current-instruction-precedence'))

    def test_06_unresolved_review_blocks(self):
        fact = replace(self.facts.lessons[0], review=None)
        route = copy.deepcopy(self.route)
        route['lessons'][0]['review_binding'] = None
        facts = replace(self.facts, lessons=(fact,))
        row = self.evaluate(route=route, facts=facts).result['items'][0]
        self.assertEqual((row['posture'], row['reason']), ('blocked', 'exact-durable-review-absent'))

    def test_07_selected_native_family_cannot_be_relabelled_as_this_fixture(self):
        family = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8'
        mapping = json.loads((family / 'mapped/packages/0001/mapping.json').read_bytes())
        selection = json.loads((family / 'context/packages/0001/lesson-selection.json').read_bytes())
        self.assertNotEqual(mapping['source_cut'], self.facts.source_cut)
        self.assertEqual(selection['current_catalog_lessons'], 0)
        self.assertEqual(selection['selected_lesson_refs'], [])
        self.assertNotIn(self.facts.lessons[0].artifact['version_ref'],
                         {row['artifact']['version_ref'] for row in mapping['rows']})

    def changed_context(self, *, family=None, source=None):
        facts = self.facts
        route = copy.deepcopy(self.route)
        originals = dict(self.originals)
        basis = json.loads(originals[facts.context_basis_binding['ref']])
        if family is not None:
            basis['family'] = family
            facts = replace(facts, family=family)
        if source is not None:
            new_binding = bind('fixture:T03-alternate-source', source)
            originals[new_binding['ref']] = source
            basis['source_binding'] = new_binding
            facts = replace(facts, source_binding=new_binding)
        basis_raw = compact(basis)
        basis_b = bind('fixture:T03-alternate-basis', basis_raw)
        originals[basis_b['ref']] = basis_raw
        domain = json.loads(originals[route['domain_profile_binding']['ref']])
        domain['context_basis_binding'] = basis_b
        domain_raw = compact(domain)
        domain_b = bind('fixture:T03-alternate-domain', domain_raw)
        originals[domain_b['ref']] = domain_raw
        route['domain_profile_binding'] = domain_b
        facts = replace(facts, context_basis_binding=basis_b)
        return route, facts, lambda binding: originals[binding['ref']]

    def test_08_foreign_family_or_source_omits(self):
        for value in ({'family': 'family:unrelated'}, {'source': b'other exact synthetic source'}):
            with self.subTest(value=value):
                route, facts, read = self.changed_context(**value)
                row = self.evaluate(route=route, facts=facts, read=read).result['items'][0]
                self.assertEqual(row['posture'], 'omitted')
                self.assertEqual(row['reason'], 'family-excluded' if 'family' in value else 'source-version-excluded')

    def test_09_unresolved_literal_exclusion_blocks(self):
        fact = replace(self.facts.lessons[0],
                       exclusions=((self.lesson['payload']['exclusions'][0], None),))
        row = self.evaluate(facts=replace(self.facts, lessons=(fact,))).result['items'][0]
        self.assertEqual((row['posture'], row['reason']), ('blocked', 'literal-exclusion-unresolved'))


class ManifestClosure(unittest.TestCase):
    def changed(self, mutate):
        manifest = json.loads(fixture.MANIFEST.read_bytes())
        mutate(manifest)
        with tempfile.TemporaryDirectory(prefix='t03-cold-manifest-') as directory:
            path = Path(directory) / 'source-manifest.json'
            path.write_bytes(compact(manifest))
            with patch.object(fixture, 'MANIFEST', path):
                with self.assertRaises(ValueError):
                    fixture.verify_manifest()

    def test_10_missing_executable_or_native_input_refuses(self):
        self.changed(lambda m: m['files'].pop(0))
        self.changed(lambda m: m['input_bindings'].pop(-1))

    def test_11_extra_row_or_changed_native_byte_pin_refuses(self):
        self.changed(lambda m: m['files'].append({'path': 'unselected:extra', 'sha256': '0' * 64}))
        self.changed(lambda m: m['input_bindings'][-1].update(sha256='0' * 64))


if __name__ == '__main__':
    unittest.main()
