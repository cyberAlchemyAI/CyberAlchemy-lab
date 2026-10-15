"""Correct three test assumptions, retaining the other12 inherited methods."""
from .base import B,Parent

class Checks(Parent.Checks):
    def test_04_same_cut_exact_current_records(self):
        self.assertEqual(self.selected.sources.source_cut,B.cut(self.view))
        self.assertTrue(self.selected.records)
        for row in self.selected.records:
            selected,body=self.selected.sources.get(row.artifact)
            self.assertEqual(selected.original,row.original)
            self.assertEqual(body,B.parse(row.original))
            self.assertIn(row.posture,self.reader.adapter.CURRENT)
            self.assertEqual(row.artifact['scope_ref'],self.view.data['config']['scope_ref'])
    def test_05_closure_no_inferred_authority(self):
        report=self.selected.closure_report()
        self.assertEqual(report['accounted_subjects'],len(self.view.subjects))
        self.assertEqual(report['included_current_instances'],len(self.selected.records))
        self.assertEqual(report['missing_current_carriers'],[])
        self.assertTrue(report['instance_bound_assignments'])
        self.assertFalse(any(r['assignment']['identity_ref']==B.records.ASSIGNMENT for r in report['instance_bound_assignments']))
        self.assertTrue(any(r['assignment']['identity_ref']=='agent-assignment:first-governed-agent-episode' for r in report['instance_bound_assignments']))
        self.assertEqual(report['authority_effect'],'none')
        self.assertIsNone(report['actual_owner_outcome'])
        self.assertFalse(report['fresh_Session_participation_established'])
        self.assertFalse(report['context_or_ontology_views_generated'])
    def test_06_catalog_not_agent_participation(self):
        refs={row.artifact['version_ref'] for row in self.selected.records}
        for subject in self.view.subjects.values():
            if subject['category'] in self.reader.adapter.EXCLUDED_CATEGORIES:
                self.assertNotIn(subject['version_ref'],refs)
        old=[r for r in self.selected.records if r.artifact['carrier_ref'] in ['cal.artifact-type.agent-instance/v1','cal.artifact-type.agent-session/v1']]
        self.assertTrue(old)
        self.assertFalse(any(B.records.PREFIX in r.artifact['identity_ref'] for r in old))
        for row in old:
            self.assertIn(row.artifact['version_ref'],self.view.data['baseline']['subjects'])
