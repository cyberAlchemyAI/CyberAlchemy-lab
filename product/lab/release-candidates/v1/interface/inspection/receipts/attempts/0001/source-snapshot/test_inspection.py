"""Actual signed read, exact-source, state separation and CLI negative checks."""
from contextlib import ExitStack
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import lab_operator as op
from render import readable


class InspectionGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack = ExitStack()
        cls.view = cls.stack.enter_context(op.replay_source('engineering'))
        cls.project = 'project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1'
        cls.old_project = 'project:cyberalchemy-v2-to-lab-migration@foundation.1'
        cls.definition = 'cal.definition.artifact-surface-classification@1.0.0-candidate.2'
        cls.old_definition = 'cal.definition.artifact-surface-classification@1.0.0-candidate.1'

    @classmethod
    def tearDownClass(cls):
        cls.stack.close()

    def test_currentness_is_explicit(self):
        v=self.view.status(); self.assertEqual(v['currentness']['status'],'current')
        self.assertEqual(v['source_cut']['signed_head'],self.view.selected['expected_head'])

    def test_definitions_exact_counts(self):
        v=self.view.definitions(limit=1000); self.assertEqual(v['total'],189)
        self.assertEqual(Counter(s['status_facets']['admission'] for s in v['items']),{'admitted-current':183,'admitted-historical':6})

    def test_definitions_current_selection(self):
        v=self.view.definitions(state='admitted-current',limit=1000)
        self.assertEqual(len(v['items']),183)
        self.assertTrue(all(s['status_facets']['admission']=='admitted-current' for s in v['items']))

    def test_definitions_historical_selection(self):
        v=self.view.definitions(state='admitted-historical');self.assertEqual(v['total'],6)
        self.assertIn(self.old_definition,[r['version_ref'] for r in v['items']])

    def test_candidate_suffix_is_not_unadmitted(self):
        v=self.view.inspect(self.definition)
        self.assertIn('candidate',v['artifact']['version_ref'])
        self.assertEqual(v['artifact']['status_facets']['admission'],'admitted-current')
        self.assertIn('/candidates/',v['artifact']['source_binding']['path'])

    def test_empty_candidate_selection_discloses_coverage(self):
        v=self.view.definitions(state='candidate-unadmitted');self.assertEqual(v['total'],0)
        self.assertIn('does not prove',v['coverage'])

    def test_definition_paging_disjoint(self):
        first=self.view.definitions(limit=10); second=self.view.definitions(offset=first['next_offset'],limit=10)
        self.assertFalse({x['version_ref'] for x in first['items']} & {x['version_ref'] for x in second['items']})
        self.assertEqual(first['total'],second['total'])

    def test_invalid_page_budgets_rejected(self):
        for kw in [{'offset':-1},{'limit':0},{'limit':1001},{'limit':True},{'state':'active'}]:
            with self.assertRaises(ValueError):self.view.definitions(**kw)

    def test_order_is_deterministic(self):
        one=self.view.definitions(limit=1000);two=self.view.definitions(limit=1000)
        self.assertEqual(op.encoded(one),op.encoded(two))

    def test_unknown_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,'not found'):self.view.inspect('definition:missing')

    def test_ambiguous_identity_requires_revision(self):
        with self.assertRaisesRegex(ValueError,'ambiguous'):self.view.inspect('cal.definition.artifact-surface-classification')

    def test_historical_definition_content_exact(self):
        v=self.view.inspect(self.old_definition)
        self.assertEqual(v['artifact']['status_facets']['admission'],'admitted-historical')
        self.assertEqual(v['body'],op.parse(op.original(v['artifact']['source_binding'])))

    def test_current_definition_content_exact(self):
        v=self.view.inspect(self.definition)
        self.assertEqual(v['body'],op.parse(op.original(v['artifact']['source_binding'])))
        self.assertTrue(v['original_source']['parsed_record_matches'])

    def test_no_body_selection(self):
        v=self.view.inspect(self.definition,include_body=False)
        self.assertIsNone(v['body']);self.assertFalse(v['body_included'])

    def test_local_record_hash_is_not_transaction_file_hash(self):
        v=self.view.inspect(self.project)
        self.assertTrue(v['original_source']['parsed_record_matches'])
        self.assertNotEqual(v['original_source']['original_file_sha256'],v['artifact']['source_binding']['sha256'])
        self.assertEqual(v['record_structural_sha256'],v['artifact']['source_binding']['sha256'])

    def test_admission_does_not_imply_runtime_or_outcome(self):
        v=self.view.inspect(self.project); f=v['artifact']['status_facets']
        self.assertEqual(f['admission'],'local-admitted-current')
        self.assertIsNone(f['runtime_observation']);self.assertIsNone(f['outcome']);self.assertIsNone(f['implementation'])

    def test_authored_lifecycle_independent(self):
        r=self.view.inspect(self.project)
        self.assertNotEqual(r['artifact']['status_facets']['admission'],r['artifact']['status_facets']['authored_lifecycle'])

    def test_canonical_authority_evidence_or_explicit_gap(self):
        a=self.view.inspect(self.definition)['authority']
        self.assertIsNotNone(a['selected_decision_ref'])
        self.assertEqual(bool(a['resolved_evidence_bindings']),a['resolution_posture']=='resolved-captured-evidence')

    def test_local_authority_evidence_resolves(self):
        a=self.view.inspect(self.project)['authority']
        self.assertEqual(a['resolution_posture'],'resolved-captured-evidence')
        self.assertTrue(all('store_id' in b for b in a['resolved_evidence_bindings']))

    def test_project_connections_exact_endpoints(self):
        v=self.view.connections(self.project)
        row=next(r for r in v['connections'] if r['connection']['version_ref']=='typed-relation:lab-engineering:engineering-evidence-membership@candidate.1')
        self.assertEqual(row['validation_posture'],'validated-selected-cut')
        self.assertEqual(row['endpoint_views'][1]['carrier_kind'],'project-identity')
        self.assertEqual(row['endpoint_views'][1]['represented_endpoint_kind'],'project')
        self.assertFalse(row['permission_from_connection'])

    def test_historical_project_relation_remains_inspectable(self):
        v=self.view.connections(self.old_project)
        self.assertTrue(v['connections'])
        self.assertTrue(all(r['validation_posture']=='validated-selected-cut' for r in v['connections']))
        self.assertTrue(any(e['eligibility_role']=='historical-read-only' for r in v['connections'] for e in r['endpoint_views']))

    def test_unresolved_connection_not_silently_valid(self):
        with patch.object(self.view.handle.operations,'validate_relation',side_effect=ValueError('invalid')):
            v=self.view.connections(self.project)
            self.assertTrue(all(r['validation_posture']=='unresolved' and r['gap'] for r in v['connections']))

    def test_review_exact_original_targets(self):
        v=self.view.review();p=op.parse(op.original(self.view.selected['proposal_binding']))
        self.assertEqual([r['target_ref'] for r in v['targets']],[r['version_ref'] for r in p['targets']])
        self.assertEqual([r['operation'] for r in v['targets']],[r['operation'] for r in p['targets']])

    def test_review_has_independent_decision_cores(self):
        v=self.view.review();self.assertEqual(len({r['decision_core']['node_id'] for r in v['targets']}),3)
        self.assertFalse(v['final_owner_review'])

    def test_review_same_body_revision_diff_is_empty(self):
        row=next(r for r in self.view.review()['targets'] if r['target_ref']==self.project)
        self.assertEqual(row['structural_diff'],[])
        self.assertNotEqual(row['before_binding'],row['after_binding'])

    def test_new_target_diff_shows_whole_body(self):
        row=next(r for r in self.view.review()['targets'] if r['operation']=='admit')
        self.assertEqual(row['structural_diff'][0]['path'],'/')
        self.assertEqual(row['status_before_application'],'candidate-unadmitted')

    def test_diff_paths_escape_json_pointer(self):
        d=op.differences({'a/b':{'~x':1}},{'a/b':{'~x':2}})
        self.assertEqual(d[0]['path'],'/a~1b/~0x')

    def test_receipt_exact_original_application(self):
        v=self.view.receipt();a=op.parse(op.original(self.view.selected['application_binding']))
        self.assertEqual(v['application_receipt'],a['receipt'])
        self.assertEqual(v['transaction_digest'],a['transaction_digest'])

    def test_receipt_why_path_separates_digests(self):
        v=self.view.receipt();self.assertEqual(len(v['why_path']),6)
        self.assertNotEqual(v['transaction_file_sha256'],v['transaction_digest'])
        self.assertEqual(len(v['why_path'][2]['digests']),3)

    def test_invalid_review_receipt_sequence_rejected(self):
        for seq in [0,-1,2,True]:
            for method in [self.view.review,self.view.receipt]:
                with self.assertRaises(ValueError):method(seq)

    def test_unsupported_api_disclosed(self):
        v=self.view.status();self.assertEqual(v['remaining_api_operations'],34)
        self.assertEqual(v['api_operations_implemented'],[])
        self.assertEqual(v['repository_runtime_activation'],'not-observed')

    def test_readable_definitions_shows_status_sources(self):
        text=readable(self.view.definitions(limit=1))
        self.assertIn('admitted-current',text);self.assertIn('SHA256:',text);self.assertIn('Decision:',text)

    def test_readable_review_shows_diff_effects(self):
        text=readable(self.view.review());self.assertIn('Structural diff:',text)
        self.assertIn('Recorded local effects:',text);self.assertIn('Final owner review: absent',text)

    def test_readable_receipt_why_path(self):
        text=readable(self.view.receipt());self.assertIn('Why-path:',text)
        self.assertIn('verified-local-signature',text)

    def test_inspection_has_no_effect_or_pilot_claim(self):
        for r in [self.view.status(),self.view.definitions(),self.view.inspect(self.project),self.view.review(),self.view.receipt()]:
            self.assertEqual(r['authority_effect'],'none');self.assertIsNone(r['actual_owner_outcome'])

    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):op.source_selection('/tmp/private-store')

    def test_substituted_selection_pin_rejected(self):
        with patch.object(op,'SELECTION_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'selection pin'):op.source_selection('engineering')

    def test_substituted_archive_pin_rejected(self):
        row=copy.deepcopy(self.view.selected);row['archive_binding']['sha256']='0'*64
        with patch.object(op,'source_selection',return_value=row):
            with self.assertRaises(ValueError):
                with op.replay_source('engineering'):pass

    def test_substituted_configuration_pin_rejected(self):
        row=copy.deepcopy(self.view.selected);row['config_sha256']='0'*64
        with patch.object(op,'source_selection',return_value=row):
            with self.assertRaises(ValueError):
                with op.replay_source('engineering'):pass

    def test_duplicate_json_and_nonfinite_rejected(self):
        for raw in [b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":Infinity}']:
            with self.assertRaises(ValueError):op.parse(raw)

    def test_read_methods_do_not_change_projection(self):
        before=op.encoded(self.view.data)
        self.view.definitions();self.view.inspect(self.project);self.view.connections(self.project);self.view.review();self.view.receipt()
        self.assertEqual(op.encoded(self.view.data),before)


class ColdAndCliGuards(unittest.TestCase):
    def test_missing_current_materials_report_stale_historical_read(self):
        with tempfile.TemporaryDirectory(prefix='cal-R03-stale-inspection-') as temp:
            with op.replay_source('engineering',source_repo=Path(temp)) as view:
                self.assertEqual(view.status()['currentness']['status'],'stale')
                self.assertTrue(view.status()['currentness']['changed'])
                self.assertIn('Changed source bindings:',readable(view.status()))
                self.assertEqual(view.inspect('project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1')['artifact']['status_facets']['admission'],'local-admitted-current')

    def test_product_source_fresh_replay_connections(self):
        with op.replay_source('product') as view:
            r=view.connections('product:cyberalchemy-lab@2.0.0-foundation.1')
            row=next(x for x in r['connections'] if x['connection']['identity_ref']=='typed-relation:R03:capability-product-membership')
            self.assertEqual(row['endpoint_views'][1]['represented_endpoint_kind'],'product')
            self.assertEqual(row['endpoint_views'][1]['carrier_kind'],'product-identity')

    def test_research_source_fresh_replay_connections(self):
        with op.replay_source('research') as view:
            r=view.connections('project:cyberalchemy-v2-to-lab-migration@1.0.0-candidate.1')
            row=next(x for x in r['connections'] if x['connection']['identity_ref']=='typed-relation:lab-research:experiment-project')
            self.assertEqual(row['source']['kind'],'experiment-run')
            self.assertEqual(row['validation_posture'],'validated-selected-cut')

    def test_cli_status_fresh_process(self):
        p=subprocess.run([sys.executable,str(op.HERE/'lab_operator.py'),'--json','status'],capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr.decode());v=op.parse(p.stdout)
        self.assertEqual(v['definition_counts'],{'admitted-current':183,'admitted-historical':6})

    def test_cli_oversized_output_rejected_without_partial_body(self):
        p=subprocess.run([sys.executable,str(op.HERE/'lab_operator.py'),'--json','--max-output-bytes','4096','definitions','--limit','1000'],capture_output=True)
        self.assertEqual(p.returncode,2);self.assertEqual(p.stdout,b'')
        self.assertIn(b'output budget exceeded',p.stderr)

    def test_cli_unknown_revision_rejected_without_traceback(self):
        p=subprocess.run([sys.executable,str(op.HERE/'lab_operator.py'),'inspect','unknown@none'],capture_output=True)
        self.assertEqual(p.returncode,2);self.assertEqual(p.stdout,b'')
        self.assertNotIn(b'Traceback',p.stderr)


from collections import Counter
if __name__=='__main__':unittest.main(verbosity=2)
