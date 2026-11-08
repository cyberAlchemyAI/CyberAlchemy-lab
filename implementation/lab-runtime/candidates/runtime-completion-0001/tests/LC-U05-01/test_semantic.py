"""Port all original semantic cases onto the independently reviewed reader."""
import bootstrap
from bootstrap import E, checked
from semantic_fixture import *
import argparse, tempfile, unittest
RUN=E
OWNED=[]

# Inherited cases preserve the original causal mutations. Public diagnostics are
# use a finite code catalogue; assertions test refusal and positive peers.

class GraphCases(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-graph-', dir=RUN)
        self.f = VariedFixture(Path(self.temp.name)); OWNED.append(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def base(self):
        self.f.original('definition', 'authority/artifact-types/definition/v2/fixtures/valid/definition.json', 'cal.artifact-type.definition/v2', 'definition')
        self.f.original('owners', 'authority/owners/foundation-01/v1/owners.json', 'cal.artifact-type.owner-registry/v1')
        self.f.original('registered', 'authority/artifact-types/artifact-type/v3/artifact.json', 'cal.artifact-type.artifact-type/v3', 'artifact-type', True, '/registered_types/0')
        self.f.all_embedded_declarations()

    def check(self, reader, anchor, edges=None):
        return G.verify_graph(reader, 'policy', self.f.edges if edges is None else edges, list(self.f.current), anchor, policy_schema_raw=checked(HERE / 'semantic-policy.schema.json', G.POLICY_SCHEMA_SHA))

    def test_original_varied_carriers_and_seven_original_fragments(self):
        self.base()
        r, a = self.f.finish()
        result = self.check(r, a)
        self.assertEqual(result['nodes'], 3)
        self.assertEqual(result['profiles'], 3)
        self.assertEqual(result['declarations'], 7)
        self.assertNotIn('kind', json.loads(self.f.payloads['definition']))
        self.assertEqual(self.f.subjects[self.f.current['cal.artifact-type.owner-registry/v1']]['identity'], 'cal.artifact-type.owner-registry/v1')
        self.assertFalse(result['admission_or_owner_authority'])

    def test_closed_published_semantic_policy_schema(self):
        from jsonschema import Draft202012Validator
        self.typed()
        r, a = self.f.finish()
        schema = json.loads((HERE / 'semantic-policy.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        policy = json.loads(self.f.payloads['policy'])
        validator.validate(policy)
        policy['profiles'][0]['unselected_extra'] = True
        self.assertFalse(validator.is_valid(policy))

    def test_original_foundation_empty_roles_and_allof_ref_items_coverage(self):
        self.base()
        r, a = self.f.finish()
        result = self.check(r, a)
        p = next((p for p in self.f.profiles if 'owner-registry' in p['carrier_ref']))
        self.assertTrue(any((f['instance_pointer'] == '/source_direction/generator_ref' for f in p['fields'])))
        self.assertEqual(result['nodes'], 3)
        definition = next((p for p in self.f.profiles if p['carrier_ref'] == 'cal.artifact-type.definition/v2'))
        self.assertTrue(any((f['instance_pointer'] == '/source_refs/*/source_ref' for f in definition['fields'])))

    def test_missing_nested_ref_disposition_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['profiles'][0]['fields'].pop())
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_wrong_fragment_selector_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['profiles'][1].update(descriptor_pointer='/registered_types/3'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_fragment_as_node_without_native_category_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['nodes'][2].update(category='artifact-instance'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_native_carrier_category_substitution_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['nodes'][0].update(category='artifact-instance'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_native_version_identity_mismatch_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['nodes'][0].update(version_ref='different-identity@1'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_wrong_type_registry_selector_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['profiles'][0].update(registry_pointer='/admitted_contracts/0'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_historical_carrier_refused(self):
        self.f.original('historical-definition', 'authority/artifact-types/definition/v1/fixtures/valid/definition.json', 'cal.artifact-type.definition/v1', 'definition')
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_exact_current_version_changed_refused(self):
        self.base()
        r, a = self.f.finish(eligibility_edit=lambda e: e['current_by_identity'].update({'CAL-FIXTURE-DEF-001': 'CAL-FIXTURE-DEF-001@wrong'}))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_withdrawn_subject_refused(self):
        self.base()
        r, a = self.f.finish(eligibility_edit=lambda e: next(iter(e['subjects'].values())).update(effective_state='withdrawn'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_exact_body_provenance_kind_spoof_refused(self):
        self.base()
        r, a = self.f.finish(eligibility_edit=lambda e: next(iter(e['subjects'].values())).update(kind='method'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_wrong_independent_graph_pin_refused(self):
        self.base()
        r, a = self.f.finish()
        a.policy_binding['sha256'] = '0' * 64
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_body_kind_discriminator_spoof_refused(self):
        self.base()
        value = json.loads(self.f.payloads['definition'])
        value['schema_version'] = 'cyberalchemy-lab-definition/v1'
        self.f.add('definition', 'governed-record', P.canonical(value))
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_invalid_protected_instance_is_not_in_public_refusal(self):
        self.base()
        value = json.loads(self.f.payloads['definition'])
        sentinel = 'owned-private-sentinel-DO-NOT-EXPORT'
        value['unexpected_private_field'] = sentinel
        self.f.add('definition', 'governed-record', P.canonical(value))
        r, a = self.f.finish()
        try:
            self.check(r, a)
        except P.Refusal as exc:
            self.assertNotIn(sentinel, str(exc))
            self.assertIsNone(exc.__cause__)
        else:
            self.fail('original closed schema must refuse private extra field')

    def typed(self):
        self.base()
        p = 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json'
        value = json.loads(original_bytes(p).decode())
        value['node_id'] = 'technical:typed-carries-definition'
        source = 'cal.artifact-type.artifact-type'
        target = 'CAL-FIXTURE-DEF-001'
        value['payload']['relation_kind_ref'] = 'relation.carries-definition'
        value['payload']['source'] = {'ref': source, 'kind': 'artifact-type', 'version_ref': self.f.current[source]}
        value['payload']['target'] = {'ref': target, 'kind': 'definition', 'version_ref': self.f.current[target]}
        value['payload']['qualifiers'] = {'definition_version_ref': self.f.current[target], 'definition_sha256': P.digest(self.f.payloads['definition'])}
        self.f.node('typed', P.canonical(value), 'cal.artifact-type.typed-relation/v3', 'typed-relation')
        self.f.edges = [{'source': 'technical:typed-carries-definition', 'dependency': source}, {'source': 'technical:typed-carries-definition', 'dependency': target}]
        self.f.relation('relation.carries-definition')

    def test_original_typed_sample_schema_and_honest_unresolved_endpoints(self):
        p = 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json'
        self.f.original('original-typed', p, 'cal.artifact-type.typed-relation/v3', 'typed-relation')
        self.f.relation('relation.successor-of')
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_actual_native_typed_qualifier_version_refs(self):
        self.typed()
        r, a = self.f.finish()
        result = self.check(r, a)
        self.assertEqual(result['edges'], 2)
        self.assertEqual(result['nodes'], 4)
        p = next((p for p in self.f.profiles if p['carrier_ref'] == 'cal.artifact-type.typed-relation/v3'))
        self.assertTrue(any((f['instance_pointer'] == '/payload/source/ref' for f in p['fields'])))

    def test_qualifier_ref_classification_omitted_refused(self):
        self.typed()
        r, a = self.f.finish(edit=lambda p: p['relation_contracts'][0]['qualifier_fields'].clear())
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_invalid_protected_qualifier_is_not_in_public_refusal(self):
        self.typed()
        v = json.loads(self.f.payloads['typed'])
        sentinel = 'owned-qualifier-private-sentinel'
        v['payload']['qualifiers']['unexpected_private_axis'] = sentinel
        self.f.add('typed', 'governed-record', P.canonical(v))
        self.f.subjects[self.f.current[v['node_id']]]['source']['sha256'] = P.digest(self.f.payloads['typed'])
        r, a = self.f.finish()
        try:
            self.check(r, a)
        except P.Refusal as exc:
            self.assertIn(str(exc), set(G.REFUSAL_CODES.values()) | {'SEMANTIC_DEPENDENCY_REFUSED','SEMANTIC_UNEXPECTED_REFUSAL'})
            self.assertNotIn(sentinel, str(exc))
            self.assertIsNone(exc.__cause__)
        else:
            self.fail('original qualifier contract must refuse unknown private axis')

    def test_typed_endpoint_version_substitution_refused(self):
        self.typed()
        v = json.loads(self.f.payloads['typed'])
        v['payload']['target']['version_ref'] = 'CAL-FIXTURE-DEF-001@wrong'
        self.f.add('typed', 'governed-record', P.canonical(v))
        self.f.subjects[self.f.current[v['node_id']]]['source']['sha256'] = P.digest(self.f.payloads['typed'])
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_omitted_semantic_edge_refused(self):
        self.typed()
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a, [])

    def test_duplicate_semantic_edge_refused(self):
        self.typed()
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a, self.f.edges + self.f.edges[:1])

    def governance_pair(self, cycle=False):
        original = json.loads(original_bytes('authority/artifact-types/governed-model/v1/fixtures/valid/record.json').decode())
        for ident, other, direction in [('technical:A', 'technical:B', 'source'), ('technical:B', 'technical:A', 'source' if cycle else 'target')]:
            value = json.loads(json.dumps(original))
            value['node_id'] = ident
            value['payload']['version_ref'] = ident + '@technical.1'
            value['successor_refs'] = []
            value['relation_refs'] = [{'relation_kind_ref': 'relation.successor-of', 'direction': direction, 'counterpart_kind': 'governed-model', 'counterpart_ref': other}]
            self.f.node(ident.replace(':', '-'), P.canonical(value), 'cal.artifact-type.governed-model/v1')
        self.f.relation('relation.successor-of')
        self.f.edges = [{'source': 'technical:A', 'dependency': 'technical:B'}] + ([{'source': 'technical:B', 'dependency': 'technical:A'}] if cycle else [])

    def test_real_original_role_pair_semantic_cycle_refused(self):
        self.governance_pair(True)
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_actual_original_descriptor_direction_pair_positive(self):
        self.governance_pair()
        r, a = self.f.finish()
        self.assertEqual(self.check(r, a)['edges'], 1)

    def test_duplicate_node_identity_refused(self):
        self.base()
        n = self.f.nodes[0]
        raw = self.f.payloads[n['file_id']]
        self.f.add('duplicate', 'governed-record', raw)
        self.f.nodes.append(dict(n, file_id='duplicate'))
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_semantic_record_misclassified_as_proof_refused(self):
        self.base()
        self.f.kinds['definition'] = 'history-proof'
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_original_declaration_omission_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['declarations'].pop())
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_original_declaration_substitution_refused(self):
        self.base()
        r, a = self.f.finish(edit=lambda p: p['declarations'][0].update(pointer='/registered_types/0'))
        with self.assertRaises(P.Refusal):
            self.check(r, a)

    def test_disconnected_original_node_refused(self):
        self.base()
        r, a = self.f.finish()
        with self.assertRaises(P.Refusal):
            G.verify_graph(r, 'policy', [], [next(iter(self.f.current))], a, policy_schema_raw=checked(HERE / 'semantic-policy.schema.json', G.POLICY_SCHEMA_SHA))

    def test_full_policy_binding_root_cannot_be_replaced_by_same_digest(self):
        self.base();r,a=self.f.finish();a.policy_binding['root_id']='different-root'
        with self.assertRaises(Refusal):self.check(r,a)

    def test_full_eligibility_binding_kind_is_preserved(self):
        self.base();r,a=self.f.finish();a.eligibility_binding['kind']='public-package'
        with self.assertRaises(Refusal):self.check(r,a)

    def test_wrong_selected_policy_schema_bytes_refuse(self):
        self.base();r,a=self.f.finish()
        with self.assertRaises(Refusal):
            G.verify_graph(r,'policy',self.f.edges,list(self.f.current),a,policy_schema_raw=b'{}')

    def test_graph_source_cut_independent_of_candidate_policy(self):
        self.base();r,a=self.f.finish();a.source_cut['commit_sequence']+=1
        with self.assertRaises(Refusal):self.check(r,a)

    def test_wrong_schema_uri_never_becomes_external_retrieval(self):
        self.f.add('external-schema','governed-schema',P.canonical({'$ref':'https://unselected.invalid/schema'}))
        with self.assertRaises(Refusal):
            G.Schemas(self.f.reader(),[{'path':'schema.json','file_id':'external-schema'}])

    def test_semantic_error_traceback_contains_no_private_instance(self):
        import traceback
        self.base();marker='INERT_'+'SEMANTIC_PRIVATE_INSTANCE'
        value=json.loads(self.f.payloads['definition']);value['extra']=marker
        self.f.add('definition','governed-record',P.canonical(value));r,a=self.f.finish()
        try:self.check(r,a)
        except Refusal as error:
            self.assertIn(str(error),set(G.REFUSAL_CODES.values())|{'SEMANTIC_DEPENDENCY_REFUSED','SEMANTIC_UNEXPECTED_REFUSAL'})
            self.assertNotIn(marker,''.join(traceback.format_exception(error)))
        else:self.fail('private invalid schema instance must refuse')

    def test_public_refusal_meaning_catalogue_distinguishes_cycle_and_anchor(self):
        self.assertNotEqual(G.REFUSAL_CODES['actual semantic dependency cycle'],G.REFUSAL_CODES['POLICY_FULL_BINDING'])
        self.base();r,a=self.f.finish();a.policy_binding['root_id']='different-root'
        with self.assertRaisesRegex(Refusal,'^'+G.REFUSAL_CODES['POLICY_FULL_BINDING']+'$'):self.check(r,a)

    def test_consumer_suppresses_provider_exception_and_absolute_private_path(self):
        import traceback
        from unittest.mock import patch
        self.base();r,a=self.f.finish();marker='/inert/private/'+'VALUE_NOT_PUBLIC'
        with patch.object(G.RoleReader,'read',side_effect=RuntimeError(marker)):
            try:self.check(r,a)
            except Refusal as error:
                rendered=''.join(traceback.format_exception(error))
                self.assertEqual(str(error),'SEMANTIC_UNEXPECTED_REFUSAL');self.assertNotIn(marker,rendered)
            else:self.fail('provider failure must refuse')

    def test_consumer_suppresses_malformed_json_marker(self):
        import traceback
        self.base();marker='INERT_'+'BAD_JSON_VALUE'
        self.f.add('definition','governed-record',b'{"private":"'+marker.encode()+b'",}')
        r,a=self.f.finish()
        try:self.check(r,a)
        except Refusal as error:
            self.assertEqual(str(error),'SEMANTIC_DEPENDENCY_REFUSED')
            self.assertNotIn(marker,''.join(traceback.format_exception(error)))
        else:self.fail('malformed selected body must refuse')

    def test_consumer_suppresses_fragment_and_role_marker(self):
        import traceback
        self.base();marker='INERT_'+'UNSELECTED_FRAGMENT_OR_ROLE'
        r,a=self.f.finish(edit=lambda p:p['profiles'][0].update(descriptor_pointer='/'+marker))
        try:self.check(r,a)
        except Refusal as error:
            self.assertNotIn(marker,''.join(traceback.format_exception(error)))
            self.assertIn(str(error),G.REFUSAL_CODES.values())
        else:self.fail('unselected fragment must refuse')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);p.add_argument('--report',type=Path);args=p.parse_args()
    RUN=args.temp_root
    if RUN!=E or not RUN.is_dir():raise ValueError('owned unit evidence root required')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GraphCases))
    final_original_guard()
    clean=not any(path.exists() for path in OWNED)
    if args.report:
        if args.report.parent!=E or not args.report.name.startswith('semantic-observation-'):raise ValueError('owned report path')
        from semantic_fixture import READ_SET,SOURCE_SELECTION,SOURCE_SELECTION_SHA
        observation={'schema_version':'lab-u0501-semantic-fixture-observation/v1',
            'original_selection':{'relative_path':str(SOURCE_SELECTION.relative_to(ROOT)),'sha256':SOURCE_SELECTION_SHA},
            'original_read_bindings':[{'kind':'evidence','root_id':'repository','relative_path':path,
                'sha256':row['sha256'],'size_bytes':row['size']} for path,row in sorted(READ_SET.items())],
            'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'cleanup':'clean' if clean else 'retained-owned',
            'actual_protected_reads':0,'fixture_original_copy_reads':len(READ_SET),'authority_effect':'none'}
        with args.report.open('x') as stream:
            json.dump(observation,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
