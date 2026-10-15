"""Pure route inventory checks; no transport, grant or owner fixture exists."""
import copy
import unittest
from .selection import SelectionFault, schema_paths, target_metadata


def example(count=1):
    bindings = [{'ref': 'fixture:schema:' + str(i), 'sha256': format(i, '064x')}
                for i in range(count)]
    return {'schema_destinations': [{'schema_binding': b,
            'runtime_schema_path': 'runtime/schemas/candidate-' + str(i) + '.json'}
            for i, b in enumerate(bindings)]}, {'schema_bindings': copy.deepcopy(bindings)}


class SelectionChecks(unittest.TestCase):
    def test_01_complete_exact_inventory(self):
        route, proposal = example(3)
        self.assertEqual(schema_paths(route, proposal),
                         {r['schema_binding']['ref']: r['runtime_schema_path']
                          for r in route['schema_destinations']})

    def test_02_schema_inventory_is_separate_from_target_bound(self):
        route, proposal = example(65)
        self.assertEqual(len(schema_paths(route, proposal)), 65)

    def test_03_original_frame_array_bound(self):
        route, proposal = example(1000)
        self.assertEqual(len(schema_paths(route, proposal)), 1000)

    def test_04_over_original_array_bound_refused(self):
        route, proposal = example(1001)
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_05_empty_exact_inventory(self):
        self.assertEqual(schema_paths(*example(0)), {})

    def test_06_duplicate_reference_refused(self):
        route, proposal = example(2)
        route['schema_destinations'][1]['schema_binding'] = copy.deepcopy(route['schema_destinations'][0]['schema_binding'])
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_07_duplicate_path_refused(self):
        route, proposal = example(2)
        route['schema_destinations'][1]['runtime_schema_path'] = route['schema_destinations'][0]['runtime_schema_path']
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_08_missing_exact_schema_refused(self):
        route, proposal = example(2)
        route['schema_destinations'].pop()
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_09_extra_selected_schema_refused(self):
        route, proposal = example(2)
        proposal['schema_bindings'].pop()
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_10_changed_schema_digest_refused(self):
        route, proposal = example()
        proposal['schema_bindings'][0]['sha256'] = 'f' * 64
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_11_duplicated_proposal_binding_refused(self):
        route, proposal = example()
        proposal['schema_bindings'] *= 2
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_12_undeclared_destination_field_refused(self):
        route, proposal = example()
        route['schema_destinations'][0]['actual_runtime_grant'] = True
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_13_undeclared_binding_field_refused(self):
        route, proposal = example()
        route['schema_destinations'][0]['schema_binding']['authority_effect'] = 'grant'
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)

    def test_14_exact_metadata_selection(self):
        binding = {'ref': 'fixture:metadata:version', 'sha256': 'a' * 64}
        proposal = {'targets': [{'artifact': {'version_ref': 'fixture:type/v2'},
                                 'candidate_binding': copy.deepcopy(binding)}]}
        manifest = {'target_metadata': {'fixture:type/v2': binding}}
        before = copy.deepcopy((proposal, manifest))
        target_metadata(proposal, manifest)
        self.assertEqual((proposal, manifest), before)

    def test_15_missing_metadata_refused(self):
        with self.assertRaises(SelectionFault):
            target_metadata({'targets': [{'artifact': {'version_ref': 'fixture:type/v2'},
                                         'candidate_binding': {'ref': 'fixture:missing', 'sha256': 'a' * 64}}]},
                            {'target_metadata': {}})

    def test_16_changed_metadata_refused(self):
        with self.assertRaises(SelectionFault):
            target_metadata({'targets': [{'artifact': {'version_ref': 'fixture:type/v2'},
                                         'candidate_binding': {'ref': 'fixture:metadata', 'sha256': 'a' * 64}}]},
                            {'target_metadata': {'fixture:type/v2': {'ref': 'fixture:metadata', 'sha256': 'b' * 64}}})

    def test_17_duplicated_revision_refused(self):
        binding = {'ref': 'fixture:metadata', 'sha256': 'a' * 64}
        target = {'artifact': {'version_ref': 'fixture:type/v2'}, 'candidate_binding': binding}
        with self.assertRaises(SelectionFault):
            target_metadata({'targets': [target, copy.deepcopy(target)]},
                            {'target_metadata': {'fixture:type/v2': binding}})

    def test_18_more_than64_targets_refused(self):
        with self.assertRaises(SelectionFault):
            target_metadata({'targets': [{}] * 65}, {'target_metadata': {}})


def unsafe_path(path):
    def check(self):
        route, proposal = example()
        route['schema_destinations'][0]['runtime_schema_path'] = path
        before = copy.deepcopy((route, proposal))
        with self.assertRaises(SelectionFault):
            schema_paths(route, proposal)
        self.assertEqual((route, proposal), before)
    return check


for number, (label, path) in enumerate([
    ('absolute', '/tmp/schema.json'), ('traversal', 'runtime/schemas/../schema.json'),
    ('dot', 'runtime/schemas/./schema.json'), ('double_separator', 'runtime/schemas//schema.json'),
    ('backslash', 'runtime/schemas/sub\\schema.json'), ('wrong_root', 'runtime/other/schema.json'),
    ('wrong_extension', 'runtime/schemas/schema.py'), ('empty_name', 'runtime/schemas/.json'),
], start=19):
    # .json is a valid literal file name under the original path grammar. It
    # is not a dot segment and must not acquire a new unrequested restriction.
    if label == 'empty_name':
        continue
    setattr(SelectionChecks, 'test_' + str(number) + '_' + label + '_refused', unsafe_path(path))
