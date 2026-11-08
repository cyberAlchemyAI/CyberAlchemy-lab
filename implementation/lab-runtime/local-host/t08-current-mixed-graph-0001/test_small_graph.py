"""Fast exact-original graph/host-route controls while the full API suite runs."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import run as R


class OriginalMixedGraph(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory(prefix='cal-t08-small-mixed-', dir='/tmp')
        self.addCleanup(self.context.cleanup)
        self.root = Path(self.context.name)
        self.root.chmod(0o700)
        self.p, self.g, self.tests, self.host, self.content = R.modules()
        self.f = self.tests.VariedFixture(self.root)
        self.f.original('node', R.NODE, 'cal.artifact-type.ontology-node/v2')
        self.f.original('cut', R.CUT, 'cal.artifact-type.ontology-cut/v1')
        for profile in self.f.profiles:
            if profile['carrier_ref'] == 'cal.artifact-type.ontology-cut/v1':
                fields = [v for v in profile['fields'] if v['instance_pointer'] == '/payload/node_refs/*']
                self.assertEqual(len(fields), 1)
                fields[0]['disposition'] = 'semantic-node'
        self.f.edges = [R.EDGE]
        self.reader, self.graph_anchor = self.f.finish()
        self.assertEqual(self.f.payloads['node'], (R.ROOT / R.NODE).read_bytes())
        self.assertEqual(self.f.payloads['cut'], (R.ROOT / R.CUT).read_bytes())
        bindings = {
            'protected_inputs': {'path': R.ORIGINAL + '/protected_inputs.py', 'sha256': R.P_SHA},
            'semantic_graph': {'path': R.ORIGINAL + '/semantic_graph.py', 'sha256': R.G_SHA},
            'private_content': {'path': R.CONTENT, 'sha256': R.CONTENT_SHA}}
        self.bindings = bindings
        self.selection = {
            'custody_anchor': {key: getattr(self.reader.anchor, key) for key in self.host.ANCHOR_FIELDS},
            'control_roots': self.reader.selector['roots'], 'binding_routes': [],
            'semantic_selection': {
                'anchor': {**self.graph_anchor.__dict__,
                           'allowed_states': list(self.graph_anchor.allowed_states)},
                'policy_file_id': 'policy', 'declared_edges': [R.EDGE],
                'root_refs': [R.EDGE['source']]},
            'readiness_version': self.host.REVIEW_VERSION,
            'observation_schema_binding': {
                'path': R.API + '/typed-review-observation.schema.json',
                'sha256': R.sha((R.ROOT / R.API / 'typed-review-observation.schema.json').read_bytes())},
            'historical_original_proof': {
                'status': 'REFUSED',
                'unavailable_binding': {
                    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json',
                    'sha256': '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'},
                'unavailable_count': 25},
            'historical_content': {
                'scope_binding': {'ref': 'technical:owned/eligibility',
                                  'sha256': R.sha(self.f.payloads['eligibility'])},
                'scope_file_id': 'eligibility'}}

    def bridge(self, selection=None, bindings=None):
        return self.host.ProtectedHostBridge(
            selection or self.selection, self.tests.P, self.tests.G,
            bindings or self.bindings, R.ROOT, private_content_module=self.content)

    def test_exact_original_mixed_graph_and_substitution_refusals(self):
        actual = self.bridge().verify_semantics(self.reader)
        self.assertEqual((actual['nodes'], actual['edges'], actual['declarations']), (2, 1, 7))
        self.assertFalse(actual['admission_or_owner_authority'])
        wrong = copy.deepcopy(self.bindings)
        wrong['protected_inputs']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'module origin'):
            self.bridge(bindings=wrong)
        substitute = copy.deepcopy(self.selection)
        substitute['semantic_selection']['policy_file_id'] = 'source'
        with self.assertRaises(self.tests.P.Refusal):
            self.bridge(selection=substitute).verify_semantics(self.reader)
        path = self.root / 'policy'
        raw = path.read_bytes()
        path.write_bytes(raw[:-1] + b' ')
        with self.assertRaises(self.tests.P.Refusal):
            self.bridge().verify_semantics(self.reader)

    def test_edge_omission_refused_by_original_graph(self):
        substitute = copy.deepcopy(self.selection)
        substitute['semantic_selection']['declared_edges'] = []
        with self.assertRaisesRegex(self.tests.P.Refusal, 'edges'):
            self.bridge(selection=substitute).verify_semantics(self.reader)


if __name__ == '__main__':
    unittest.main()
