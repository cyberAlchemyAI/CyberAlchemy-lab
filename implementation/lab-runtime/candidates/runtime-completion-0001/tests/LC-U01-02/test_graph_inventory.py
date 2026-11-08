"""Ordered historical metadata and typed-graph regression cases.

Only the six explicitly pinned metadata documents are read. References inside
their tables, including protected dependencies, are never dereferenced. Fixture
writes use exclusive temporary directories beneath the supplied owned root.
"""
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
from test_contracts import value, binding
from lab_contracts.codec import Refusal, canonical, sha
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity, legacy_json
from lab_selectors.chains import consumer_mapping, selected
from lab_selectors.graphs import KINDS, classify_rows, validate_graph
from lab_selectors.source_inventory import compare, retain

TEMP_ROOT = Path(os.environ.get('LAB_UNIT_TEST_TMP_ROOT', str(E)))
OWNED_TEMP_PATHS = []
HISTORY_PATH = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/protected-startup-preparation-0001/HISTORY-CONTRACT.json'
HISTORY_SHA = '0ea34b07d0afe9e32fe22802f5c60292f466fcbea217ed048166adf3f70b5e86'
HISTORY_SIZE = 5032
SOURCE_PATH = 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
SOURCE_SHA = 'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16'
SOURCE_SIZE = 6858334
DOCUMENT_SIZES = {
    'product/lab/release-candidates/v1/interface/api-integration-v16/SCHEMA-EXECUTION-DEPENDENCIES.json': 601975,
    'product/lab/release-candidates/v1/interface/api-integration-v16/contract-profile.json': 5105826,
    'product/lab/release-candidates/v1/interface/api-integration-v16/source-manifest.json': 5128851,
    'product/lab/release-candidates/v1/release-validation/0001/environment-contract.json': 27726282,
    'product/lab/release-candidates/v1/release-validation/0001/runtime16-draft-0276/environment-contract.json': 10465083,
}


def byte_binding(path, digest, size, root='repository'):
    return {'kind': 'evidence', 'root_id': root, 'relative_path': path,
            'sha256': digest, 'size_bytes': size}


class MetadataReader:
    """Cache only selected document bytes; fail before any member/body access."""
    def __init__(self, reader, allowed):
        self.reader = reader
        self.allowed = {AnchoredReader.key(b) for b in allowed}
        self.cache = {}
        self.calls = []

    def read(self, b):
        key = AnchoredReader.key(b)
        if key not in self.allowed:
            raise AssertionError('attempt to dereference unselected metadata/body')
        self.calls.append(key)
        if key not in self.cache:
            self.cache[key] = self.reader.read(b)
        return self.cache[key]


class FullOriginalMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        anchor = RootAnchor('repository', str(REPO), identity(os.stat(REPO)))
        history_binding = byte_binding(HISTORY_PATH, HISTORY_SHA, HISTORY_SIZE)
        history = legacy_json(AnchoredReader([anchor], [history_binding]).read(history_binding))
        if len(history['tables']) != 17 or sum(t['occurrences'] for t in history['tables']) != 172533:
            raise AssertionError('historical table closure differs')
        documents = {
            name: byte_binding(name, digest, DOCUMENT_SIZES[name])
            for name, digest in history['document_pins'].items()
        }
        documents[SOURCE_PATH] = byte_binding(SOURCE_PATH, SOURCE_SHA, SOURCE_SIZE)
        cls.descriptors = []
        for t in history['tables']:
            classification = {'/protected_dependencies': 'protected-dependency-metadata',
                              '/public_payload_file_bindings': 'public-payload-metadata'}.get(
                                  t['row_selector'], 'original-proof-metadata')
            cls.descriptors.append({'document_binding': documents[t['document']],
                'selector': t['row_selector'], 'row_count': t['occurrences'],
                'classification': classification})
        cls.descriptors.append({'document_binding': documents[SOURCE_PATH], 'selector': '/files',
                                'row_count': 32011, 'classification': 'current-execution-metadata'})
        cls.reader = MetadataReader(AnchoredReader([anchor], list(documents.values())), list(documents.values()))
        # The oracle reads the selected original documents independently of retain.
        decoded = {name: legacy_json(cls.reader.read(b)) for name, b in documents.items()}
        original_tables = []
        for d in cls.descriptors:
            rows = decoded[d['document_binding']['relative_path']][d['selector'][1:]]
            if d['selector'] == '/host_native_binding':
                rows = [rows]
            original_tables.append({'document_binding': d['document_binding'],
                'selector': d['selector'], 'classification': d['classification'], 'rows': rows})
        cls.original = {'schema_version': 'lab-completion-original-table-inventory/v1',
                        'tables': original_tables, 'occurrences': 204544,
                        'member_bodies_read': 0, 'authority_effect': 'none'}
        cls.retained = retain(cls.reader, copy.deepcopy(cls.descriptors), cls.descriptors)

    def test_all_original_occurrences_and_current_source_rows_retained(self):
        self.assertEqual(compare(self.original, self.retained), 204544)
        self.assertEqual(len(self.retained['tables']), 18)
        self.assertEqual(sum(len(t['rows']) for t in self.retained['tables'][:17]), 172533)
        self.assertEqual(len(self.retained['tables'][-1]['rows']), 32011)
        self.assertEqual(self.retained['member_bodies_read'], 0)
        self.assertEqual(set(self.reader.calls), self.reader.allowed)
        protected = [t for t in self.retained['tables'] if t['classification'] == 'protected-dependency-metadata']
        self.assertEqual(len(protected), 1)
        self.assertEqual(len(protected[0]['rows']), 23486)
        self.assertTrue(all(r['public_body_export_allowed'] is False for r in protected[0]['rows']))

    def test_full_table_deletion_reorder_and_duplicate_substitution_refuse(self):
        for table_index in (0, 17):
            rows = self.retained['tables'][table_index]['rows']
            different = next(i for i, row in enumerate(rows) if row != rows[0])
            for corruption in ('delete', 'reorder', 'duplicate'):
                with self.subTest(table_index=table_index, corruption=corruption):
                    changed = dict(self.retained)
                    changed['tables'] = list(self.retained['tables'])
                    changed['tables'][table_index] = dict(changed['tables'][table_index])
                    altered = list(rows)
                    if corruption == 'delete':
                        del altered[different]
                    elif corruption == 'reorder':
                        altered[0], altered[different] = altered[different], altered[0]
                    else:
                        altered[different] = altered[0]
                    changed['tables'][table_index]['rows'] = altered
                    with self.assertRaisesRegex(Refusal, 'ORDERED_ORIGINAL_TABLE_DRIFT'):
                        compare(self.original, changed)

    def test_coherent_descriptor_repin_refuses_before_read(self):
        changed = copy.deepcopy(self.descriptors)
        changed[0]['document_binding']['sha256'] = '0' * 64
        before = len(self.reader.calls)
        with self.assertRaisesRegex(Refusal, 'INDEPENDENT_TABLE_SELECTION'):
            retain(self.reader, changed, self.descriptors)
        self.assertEqual(len(self.reader.calls), before)


class GraphTests(unittest.TestCase):
    @staticmethod
    def policy(graph, rows):
        # Independently selected technical fixture policy, not host authority.
        return canonical({'schema_version': 'lab-completion-edge-policy/v1',
                          'nodes': graph['nodes'], 'edges': graph['edges'], 'roots': graph['roots'],
                          'original_rows_sha256': sha(canonical(rows)),
                          'acyclic_kinds': ['semantic', 'execution', 'host-custody']})

    def check_graph(self, graph, rows, policy=None):
        raw = self.policy(graph, rows) if policy is None else policy
        return validate_graph(graph, rows, policy_raw=raw, expected_policy_sha256=sha(raw))

    def graph(self):
        kinds = sorted(KINDS)
        rows = [{'occurrence': n} for n in range(4)]
        nodes = [{'id': f'n{n}', 'kind': kinds[n % 4], 'original_binding': binding(),
                  'selector': f'/rows/{n}'} for n in range(5)]
        edges = [{'from': f'n{n}', 'to': f'n{n + 1}', 'kind': kinds[n], 'original_row': n}
                 for n in range(4)]
        return {'schema_version': 'lab-completion-typed-graph/v1', 'nodes': nodes,
                'edges': edges, 'roots': ['n0'], 'original_rows': rows}, copy.deepcopy(rows)

    def test_all_four_kinds_and_diamond_shared_dependency(self):
        graph, rows = self.graph()
        graph['edges'].append({'from': 'n0', 'to': 'n3', 'kind': 'execution', 'original_row': 0})
        result = self.check_graph(graph, rows)
        self.assertEqual(result['kinds'], sorted(KINDS))
        self.assertEqual((result['nodes'], result['edges']), (5, 5))

    def test_cycle_unknown_kind_bad_endpoint_and_duplicate_edge_refuse(self):
        for mutation, code in [('cycle', 'GRAPH_CYCLE'), ('kind', 'EDGE_KIND_ENDPOINT'),
                               ('endpoint', 'EDGE_KIND_ENDPOINT'), ('duplicate', 'DUPLICATE_EDGE')]:
            graph, rows = self.graph()
            if mutation == 'cycle':
                for edge in graph['edges']:
                    edge['kind'] = 'semantic'
                graph['edges'].append({'from': 'n4', 'to': 'n0', 'kind': 'semantic', 'original_row': 0})
            elif mutation == 'kind':
                graph['edges'][0]['kind'] = 'guessed'
            elif mutation == 'endpoint':
                graph['edges'][0]['to'] = 'missing'
            else:
                graph['edges'].append(copy.deepcopy(graph['edges'][0]))
            with self.subTest(mutation=mutation), self.assertRaisesRegex(Refusal, code):
                self.check_graph(graph, rows)

    def test_wrong_root_disconnected_node_and_original_row_corruption_refuse(self):
        for roots, code in [(['missing'], 'GRAPH_ROOTS'), (['n1'], 'DISCONNECTED_GRAPH'),
                             (['n0', 'n0'], 'GRAPH_ROOTS')]:
            graph, rows = self.graph(); graph['roots'] = roots
            with self.subTest(roots=roots), self.assertRaisesRegex(Refusal, code):
                self.check_graph(graph, rows)
        graph, rows = self.graph(); graph['original_rows'].reverse()
        with self.assertRaisesRegex(Refusal, 'ORIGINAL_ROWS_CHANGED'):
            self.check_graph(graph, rows)

    def test_evidence_backreference_cycle_is_not_semantic_dependency_cycle(self):
        graph, rows = self.graph()
        graph['edges'].append({'from': 'n4', 'to': 'n0', 'kind': 'evidence', 'original_row': 0})
        self.assertEqual(self.check_graph(graph, rows)['edges'], 5)
        graph['nodes'] = graph['nodes'][:2]
        graph['edges'] = [{'from': 'n0', 'to': 'n1', 'kind': 'evidence', 'original_row': 0},
                          {'from': 'n1', 'to': 'n0', 'kind': 'evidence', 'original_row': 1}]
        self.assertEqual(self.check_graph(graph, rows)['edges'], 2)

    def test_policy_pins_role_selector_provenance_and_cannot_coherently_repin(self):
        graph, rows = self.graph()
        policy = self.policy(graph, rows)
        for mutation in ('relabel', 'selector', 'nodebinding', 'provenance'):
            changed = copy.deepcopy(graph)
            if mutation == 'relabel':
                changed['edges'][0]['kind'] = 'semantic'
            elif mutation == 'selector':
                changed['nodes'][0]['selector'] = '/unselected'
            elif mutation == 'nodebinding':
                changed['nodes'][0]['original_binding']['sha256'] = '0' * 64
            else:
                changed['edges'][0]['original_row'] = 1
            with self.subTest(mutation=mutation), self.assertRaisesRegex(Refusal, 'SCHEMA_ROLE_POLICY_DIFFERS'):
                self.check_graph(changed, rows, policy)
        altered_policy = self.policy(changed, rows)
        with self.assertRaisesRegex(Refusal, 'EDGE_POLICY_ANCHOR'):
            validate_graph(changed, rows, policy_raw=altered_policy, expected_policy_sha256=sha(policy))

    def test_each_selected_dependency_kind_cycle_refuses_separately(self):
        for kind in ('semantic', 'execution', 'host-custody'):
            graph, rows = self.graph()
            graph['nodes'] = graph['nodes'][:2]
            graph['edges'] = [{'from': 'n0', 'to': 'n1', 'kind': kind, 'original_row': 0},
                              {'from': 'n1', 'to': 'n0', 'kind': kind, 'original_row': 1}]
            with self.subTest(kind=kind), self.assertRaisesRegex(Refusal, 'GRAPH_CYCLE'):
                self.check_graph(graph, rows)

    def test_repeat_occurrences_preserved_and_missing_extra_kind_refuse(self):
        row = {'same_original_identity': 'repeat'}
        tables = [{'rows': [row, row, {'different': 'row'}]}]
        dispositions = {(0, 0): 'semantic', (0, 1): 'evidence', (0, 2): 'execution'}
        output = classify_rows(tables, dispositions, dict(dispositions))
        self.assertEqual(len(output), 3)
        self.assertEqual([r['row_index'] for r in output], [0, 1, 2])
        self.assertNotEqual(output[0]['kind'], output[1]['kind'])
        for bad in [{(0, 0): 'semantic'}, {**dispositions, (1, 0): 'execution'},
                    {**dispositions, (0, 1): 'unknown'}]:
            with self.assertRaises(Refusal):
                classify_rows(tables, bad, dict(dispositions))
        relabeled = {**dispositions, (0, 1): 'semantic'}
        with self.assertRaisesRegex(Refusal, 'INDEPENDENT_DISPOSITIONS'):
            classify_rows(tables, relabeled, dict(dispositions))

    def test_consumer_missing_reordered_and_duplicate_identity_refuse(self):
        store = value('GenerationStoreSelection')
        first = copy.deepcopy(store['canonical_consumer_inventory'][0]); first['identity'] = 'reader-one'
        second = copy.deepcopy(first); second['identity'] = 'reader-two'; second['relative_path'] = 'other'
        expected = [first, second]
        store['canonical_consumer_inventory'] = copy.deepcopy(expected)
        self.assertEqual(consumer_mapping(store, expected, copy.deepcopy(expected)), 2)
        for observed in [[first], list(reversed(expected)), expected + [first]]:
            with self.assertRaisesRegex(Refusal, 'CONSUMER_INVENTORY'):
                consumer_mapping(store, expected, observed)
        duplicates = [first, {**second, 'identity': first['identity']}]
        store['canonical_consumer_inventory'] = duplicates
        with self.assertRaisesRegex(Refusal, 'DUPLICATE_CONSUMER'):
            consumer_mapping(store, duplicates, duplicates)


class AnchoredSelectionTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TEMP_ROOT.is_dir(), 'existing owned --temp-root required')
        self.temp = tempfile.TemporaryDirectory(prefix='owned-test-graph-', dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        OWNED_TEMP_PATHS.append(self.root)

    def fixture(self, name='selected.json'):
        payload = canonical(value('CodeSelection'))
        path = self.root / name
        with path.open('xb') as stream:
            stream.write(payload)
        b = byte_binding(name, sha(payload), len(payload), 'fixture')
        anchor = RootAnchor('fixture', str(self.root), identity(os.stat(self.root)))
        return b, anchor

    def test_same_bytes_wrong_root_identity_refuses(self):
        b, anchor = self.fixture()
        other = self.root / 'other'; other.mkdir()
        (other / b['relative_path']).write_bytes((self.root / b['relative_path']).read_bytes())
        wrong = RootAnchor('fixture', str(other), anchor.expected)
        with self.assertRaisesRegex(Refusal, 'ROOT_IDENTITY'):
            AnchoredReader([wrong], [b]).read(b)

    def test_coherent_repin_cannot_override_independent_expected_selector(self):
        b, anchor = self.fixture()
        reader = AnchoredReader([anchor], [b])
        self.assertEqual(selected(reader, b, 'CodeSelection', b)['selection_id'], 'x')
        changed = value('CodeSelection'); changed['selection_id'] = 'coherent-replacement'
        raw = canonical(changed)
        (self.root / b['relative_path']).write_bytes(raw)
        repinned = {**b, 'sha256': sha(raw), 'size_bytes': len(raw)}
        with self.assertRaisesRegex(Refusal, 'INDEPENDENT_SELECTION_DIFFERS'):
            selected(AnchoredReader([anchor], [repinned]), repinned, 'CodeSelection', b)
        with self.assertRaisesRegex(Refusal, 'UNSELECTED_BINDING'):
            reader.read(repinned)
        with self.assertRaises(Refusal):
            reader.read(b)

    def test_unknown_root_and_protected_body_cannot_be_silently_read(self):
        b, anchor = self.fixture()
        unknown = {**b, 'root_id': 'unselected'}
        with self.assertRaisesRegex(Refusal, 'UNSELECTED_ROOT'):
            AnchoredReader([anchor], [unknown]).read(unknown)
        protected = {**b, 'kind': 'protected-input'}
        with self.assertRaisesRegex(Refusal, 'PROTECTED_PERMISSION_REQUIRED'):
            AnchoredReader([anchor], [protected]).read(protected)

    def test_symlink_metadata_refuses_and_foreign_target_is_preserved(self):
        b, anchor = self.fixture()
        original = (self.root / b['relative_path']).read_bytes()
        (self.root / 'alias.json').symlink_to(b['relative_path'])
        alias = {**b, 'relative_path': 'alias.json'}
        with self.assertRaisesRegex(Refusal, 'UNSAFE_OR_MISSING_FILE'):
            AnchoredReader([anchor], [alias]).read(alias)
        self.assertEqual((self.root / b['relative_path']).read_bytes(), original)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp-root', type=Path, default=TEMP_ROOT)
    args = parser.parse_args()
    TEMP_ROOT = args.temp_root.absolute()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    clean = not any(p.exists() or p.is_symlink() for p in OWNED_TEMP_PATHS)
    passed = result.wasSuccessful() and clean
    print(json.dumps({'schema_version': 'lab-case-command-result/v1',
                      'result': 'PASS' if passed else 'FAIL',
                      'checks': result.testsRun, 'effect_state': 'owned-inert',
                      'cleanup': 'clean' if clean else 'owned-residue'}))
    raise SystemExit(0 if passed else 1)
