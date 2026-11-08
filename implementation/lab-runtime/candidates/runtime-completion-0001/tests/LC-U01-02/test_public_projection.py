"""Actual public-source projection and source-role corruption regressions."""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True  # Keep imported dependencies outside the test write surface.
import tempfile
import unittest

S = Path(__file__).absolute().parents[2]
REPO = S.parents[3]
E = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02'
sys.path[:0] = [str(S / 'contracts'), str(S / 'selectors'), str(Path(__file__).parent)]
import test_contracts  # Select the same pinned jsonschema dependency environment.
from lab_contracts.codec import Refusal, canonical, sha
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity, legacy_json
from lab_selectors.public_projection import build, policy_inputs, pointer, projection_digest, verify_subset_rows

TEMP_ROOT = Path(os.environ.get('LAB_UNIT_TEST_TMP_ROOT', str(E)))
OWNED_TEMP_PATHS = []
EXPECTED_PROJECTION_SHA256 = '6fa0cd021b6fc338ab62209dba88283b9ae1b8396fa429717ccb288494b4a25c'
POLICY_BINDING = {'kind': 'evidence', 'root_id': 'repository',
    'relative_path': 'implementation/lab-runtime/candidates/runtime-completion-0001/selectors/public-source-role-policy.json',
    'sha256': '35129f426ee6048e73366129ae4e9c0bf9ef5cb487717719337ad42dfbd410dc', 'size_bytes': 16873}


class ReadLog:
    def __init__(self, reader):
        self.reader = reader
        self.reads = []

    def read(self, binding):
        self.reads.append(binding)
        return self.reader.read(binding)


class PublicProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_anchor = RootAnchor('repository', str(REPO), identity(os.stat(REPO)))
        cls.policy = legacy_json(AnchoredReader([cls.root_anchor], [POLICY_BINDING]).read(POLICY_BINDING))
        cls.inputs = policy_inputs(cls.policy)
        cls.reader = ReadLog(AnchoredReader([cls.root_anchor], [POLICY_BINDING, *cls.inputs]))
        cls.projection = build(cls.reader, POLICY_BINDING)

    def setUp(self):
        self.assertTrue(TEMP_ROOT.is_dir(), 'existing owned temp root required')
        self.temp = tempfile.TemporaryDirectory(prefix='owned-test-public-projection-', dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        OWNED_TEMP_PATHS.append(self.root)

    def modified_policy(self, mutate):
        policy = copy.deepcopy(self.policy)
        mutate(policy)
        raw = canonical(policy)
        path = self.root / 'policy.json'
        with path.open('xb') as stream:
            stream.write(raw)
        binding = {'kind': 'evidence', 'root_id': 'fixture', 'relative_path': 'policy.json',
                   'sha256': sha(raw), 'size_bytes': len(raw)}
        reader = AnchoredReader([self.root_anchor,
            RootAnchor('fixture', str(self.root), identity(os.stat(self.root)))], [binding, *self.inputs])
        return build(reader, binding)

    def test_complete_actual_tables_and_occurrence_graph_preserve_order_and_rows(self):
        p = self.projection
        self.assertEqual(p['counts'], {'historical_tables': 17, 'historical_occurrences': 172533,
                                      'all_tables': 22, 'all_occurrences': 241598})
        self.assertEqual(p['occurrence_kind_counts'], {'semantic': 0, 'execution': 69064,
                                                     'evidence': 149022, 'host-custody': 23512})
        self.assertEqual(len(p['graph']['occurrence_nodes']), 241598)
        self.assertEqual(len(p['graph']['occurrence_edges']), 241598)
        originals = {d['id']: legacy_json(self.reader.read(d['binding'])) for d in self.policy['documents']}
        offset = 0
        for table in p['tables']:
            rows = pointer(originals[table['document_id']], table['selector'])
            if table['selector'] == '/host_native_binding':
                rows = [rows]
            self.assertEqual(rows, table['rows'])
            for row_index, row in enumerate(rows):
                node = p['graph']['occurrence_nodes'][offset]
                edge = p['graph']['occurrence_edges'][offset]
                expected_selector = table['selector'] if table['selector'] == '/host_native_binding' else f"{table['selector']}/{row_index}"
                self.assertEqual((node['table_id'], node['row_index'], node['original_selector']),
                                 (table['id'], row_index, expected_selector))
                self.assertEqual((edge['from'], edge['to'], edge['kind']),
                                 (table['document_id'], node['id'], table['kind']))
                self.assertEqual(pointer(originals[table['document_id']], expected_selector), row)
                offset += 1

    def test_only_selected_public_documents_read_no_protected_or_member_bodies(self):
        allowed = {canonical(b) for b in [POLICY_BINDING, *self.inputs]}
        self.assertEqual({canonical(b) for b in self.reader.reads}, allowed)
        self.assertEqual(self.projection['member_byte_resolution']['members_read'], 0)
        protected = next(t for t in self.projection['tables'] if t['selector'] == '/protected_dependencies')
        self.assertEqual(len(protected['rows']), 23486)
        self.assertTrue(all(r['public_body_export_allowed'] is False for r in protected['rows']))
        self.assertFalse(self.projection['runtime_eligible'])
        self.assertEqual(self.projection['authority_effect'], 'none')

    def test_actual_public_source_profile_schema_joins_and_semantic_gate(self):
        graph = self.projection['graph']
        self.assertEqual([(j['from'], j['selector'], j['to']) for j in graph['verified_document_joins'][:2]],
            [('current-source', '/profile_binding', 'current-profile'),
             ('current-profile', '/schema_execution_dependency_binding', 'current-schema')])
        self.assertEqual(len(graph['verified_document_joins']), 4)
        self.assertEqual(len(graph['verified_schema_links']), 5)
        self.assertTrue(all(e['kind'] == 'execution' for e in graph['verified_schema_links']))
        self.assertEqual(graph['semantic_artifact_edges'], [])
        semantic = self.projection['semantic_resolution']
        self.assertEqual(semantic['disposition'], 'unresolved-gated')
        self.assertEqual(semantic['selected_instance_bindings'], [])
        self.assertEqual(semantic['verified_schema_declarations'][0]['original'],
                         {'const': 'cal.artifact-type.definition/v1'})
        self.assertIn('typed_relations', semantic['declaration_selectors'][1])

    def test_same_selected_source_projection_is_deterministic(self):
        other_reader = AnchoredReader([self.root_anchor], [POLICY_BINDING, *self.inputs])
        other = build(other_reader, POLICY_BINDING)
        self.assertEqual(projection_digest(self.projection), EXPECTED_PROJECTION_SHA256)
        self.assertEqual(projection_digest(other), EXPECTED_PROJECTION_SHA256)

    def test_coherent_policy_repin_cannot_replace_external_anchor(self):
        raw = (REPO / POLICY_BINDING['relative_path']).read_bytes()
        changed = copy.deepcopy(self.policy); changed['tables'][0]['kind'] = 'semantic'
        target = self.root / 'policy.json'; target.write_bytes(canonical(changed))
        expected = {**POLICY_BINDING, 'root_id': 'fixture', 'relative_path': 'policy.json'}
        anchored = AnchoredReader([RootAnchor('fixture', str(self.root), identity(os.stat(self.root)))], [expected])
        self.assertNotEqual(sha(raw), sha(target.read_bytes()))
        with self.assertRaises(Refusal):
            build(anchored, expected)

    def test_selected_schema_profile_join_preserves_complete_original_rows(self):
        source = next(t['rows'] for t in self.projection['tables'] if t['role'] == 'current-schema-execution')
        target = next(t['rows'] for t in self.projection['tables'] if t['role'] == 'current-profile-declaration')
        verify_subset_rows(source, target)
        for field, value in [('size_bytes', 123), ('unexpected_fixture_field', 'not declared')]:
            changed = {**source[0], field: value}
            self.assertEqual(changed['path'], source[0]['path'])
            self.assertEqual(changed['sha256'], source[0]['sha256'])
            with self.subTest(field=field), self.assertRaisesRegex(Refusal, 'PUBLIC_EXECUTION_OUTSIDE_PROFILE'):
                verify_subset_rows([changed, *source[1:]], target)
        conflicting = {**target[0], 'size_bytes': 321}
        with self.assertRaisesRegex(Refusal, 'PUBLIC_CONFLICTING_DECLARED_PATH'):
            verify_subset_rows(source, [*target, conflicting])
        with self.assertRaisesRegex(Refusal, 'PUBLIC_CONFLICTING_SOURCE_PATH'):
            verify_subset_rows([source[0], {**source[0], 'size_bytes': 321}], target)

    def test_actual_original_row_substitution_refuses_selected_document_digest(self):
        spec = next(d for d in self.policy['documents'] if d['id'] == 'current-schema')
        raw = self.reader.read(spec['binding'])
        original = legacy_json(raw)
        first = original['files'][0]['sha256']
        replacement = ('0' if first[0] != '0' else '1') + first[1:]
        # Replace one original row digest in the exact original byte carrier.
        # Size, table count and all other source bytes remain unchanged.
        changed = raw.replace(first.encode('ascii'), replacement.encode('ascii'), 1)
        self.assertEqual(len(changed), len(raw))
        self.assertNotEqual(changed, raw)
        path = self.root / 'source.json'; path.write_bytes(changed)
        expected = {**spec['binding'], 'root_id': 'fixture', 'relative_path': 'source.json'}
        reader = AnchoredReader([RootAnchor('fixture', str(self.root), identity(os.stat(self.root)))], [expected])
        with self.assertRaisesRegex(Refusal, 'CONTENT_DIGEST'):
            reader.read(expected)

    def test_proof_reference_cannot_be_relabelled_semantic_even_in_new_fixture_policy(self):
        with self.assertRaisesRegex(Refusal, 'PUBLIC_TABLE_ROLE_KIND'):
            self.modified_policy(lambda p: p['tables'][0].update(kind='semantic'))

    def test_historical_table_reorder_is_not_hidden_by_equal_counts(self):
        def reorder(p):
            p['tables'][0], p['tables'][1] = p['tables'][1], p['tables'][0]
        with self.assertRaisesRegex(Refusal, 'PUBLIC_HISTORY_ORDER_OR_OMISSION'):
            self.modified_policy(reorder)

    def test_current_profile_table_omission_refuses_even_with_coherent_count_edit(self):
        def omit(p):
            table = next(t for t in p['tables'] if t['role'] == 'current-profile-declaration')
            p['tables'].remove(table)
            p['expected_counts']['all_tables'] -= 1
            p['expected_counts']['all_occurrences'] -= table['row_count']
        with self.assertRaisesRegex(Refusal, 'PUBLIC_CURRENT_TABLE_CLOSURE'):
            self.modified_policy(omit)

    def test_wrong_declared_document_join_refuses(self):
        with self.assertRaisesRegex(Refusal, 'PUBLIC_DECLARED_JOIN'):
            self.modified_policy(lambda p: p['joins'][0].update(to='current-schema'))

    def test_original_count_corruption_refuses(self):
        with self.assertRaisesRegex(Refusal, 'PUBLIC_TABLE_CARDINALITY'):
            self.modified_policy(lambda p: p['tables'][0].update(row_count=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp-root', type=Path, default=TEMP_ROOT)
    args = parser.parse_args(); TEMP_ROOT = args.temp_root.absolute()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    clean = not any(p.exists() or p.is_symlink() for p in OWNED_TEMP_PATHS)
    passed = result.wasSuccessful() and clean
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS' if passed else 'FAIL',
                      'checks': result.testsRun, 'effect_state': 'owned-inert',
                      'cleanup': 'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if passed else 1)
