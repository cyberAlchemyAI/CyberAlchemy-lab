"""Synthetic query-exclusion successor checks; original56 methods unchanged."""
from dataclasses import replace
import unittest
from rules import Rules, SelectionFault, encoded
from test_rules import Scenario


class QueryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rules = Rules()

    def test_explicit_exclusion_omitted(self):
        s=Scenario(); f=s.add(); s.lessons[0]=replace(f,query_excluded=True)
        route,facts=s.build(); out=self.rules.select(encoded(route),facts,s.read)
        self.assertEqual(out.result['items'][0]['posture'],'omitted')
        self.assertEqual(out.result['items'][0]['reason'],'explicit-request-exclusion')

    def test_excluded_influence_does_not_block_eligible(self):
        s=Scenario(); s.add(); f=s.add(influence='other'); s.lessons[1]=replace(f,query_excluded=True)
        route,facts=s.build(); out=self.rules.select(encoded(route),facts,s.read)
        self.assertEqual([r['posture'] for r in out.result['items']],['selected','omitted'])
        self.assertEqual(out.result['items'][0]['conflict_refs'],[])

    def test_exclusion_does_not_invent_missing_review(self):
        s=Scenario(); f=s.add(missing_review=True); s.lessons[0]=replace(f,query_excluded=True)
        route,facts=s.build(); out=self.rules.select(encoded(route),facts,s.read)
        self.assertEqual(out.result['items'][0]['posture'],'blocked')

    def test_exclusion_boolean_required(self):
        s=Scenario(); f=s.add(); s.lessons[0]=replace(f,query_excluded='yes')
        route,facts=s.build()
        with self.assertRaises(SelectionFault): self.rules.select(encoded(route),facts,s.read)

    def test_expired_excluded_retains_expiry(self):
        s=Scenario(); f=s.add(payload={'expires_at':'2026-10-11T11:00:00Z'}); s.lessons[0]=replace(f,query_excluded=True)
        route,facts=s.build(); row=self.rules.select(encoded(route),facts,s.read).result['items'][0]
        self.assertTrue(row['expired']); self.assertEqual(row['posture'],'omitted')


if __name__ == '__main__': unittest.main(verbosity=2)
