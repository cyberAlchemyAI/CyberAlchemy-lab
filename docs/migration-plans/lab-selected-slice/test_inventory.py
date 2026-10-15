"""Hostile metadata checks; no external source file is changed."""
import tempfile
import unittest

from check_inventory import *
from represented_subjects import RepresentationFault


class InventoryGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=parse(TARGET.read_bytes())

    def setUp(self):self.value=copy.deepcopy(self.original)

    def item(self,kind):return next(r for r in self.value['items'] if r['item_kind']==kind)

    def reject(self):
        with self.assertRaises(RepresentationFault):validate_selection(self.value)

    def test_actual_inventory(self):
        result=validate_selection(self.value,True)
        self.assertEqual(result['items_checked'],140);self.assertEqual(result['blocked_dependencies'],9)

    def test_private_body_export_rejected(self):self.value['scope']['private_body_export_allowed']=True;self.reject()
    def test_raw_source_body_copy_rejected(self):self.value['scope']['raw_source_bodies_copied']=True;self.reject()
    def test_unknown_top_level_body_field_rejected(self):self.value['raw_source_files']={'private':'body'};self.reject()
    def test_unknown_item_body_field_rejected(self):self.item('node')['text']='private body';self.reject()
    def test_whole_tree_import_rejected(self):self.value['scope']['whole_legacy_tree_selected']=True;self.reject()
    def test_transitive_closure_claim_rejected(self):self.value['scope']['transitive_closure_claimed']=True;self.reject()
    def test_source_execution_rejected(self):self.value['scope']['source_execution_allowed']=True;self.reject()
    def test_source_mutation_rejected(self):self.value['scope']['source_mutation_allowed']=True;self.reject()
    def test_source_authority_transfer_rejected(self):self.value['scope']['source_authority_transferred']=True;self.reject()
    def test_actual_owner_response_cannot_be_fabricated(self):self.value['actual_owner_outcome']='approved';self.reject()
    def test_unknown_package_rejected(self):self.value['selected_package_keys'].append('other-package');self.reject()
    def test_unknown_root_rejected(self):self.value['root_bindings']['unselected']={};self.reject()
    def test_standalone_root_cannot_replace_historical_package(self):self.value['root_bindings']['historical-cav2']['material_root']=str(STANDALONE_ROOT);self.reject()
    def test_root_relocation_is_not_an_identity_alias(self):self.value['root_relocation']['identity_alias_inferred']=True;self.reject()
    def test_namespace_cannot_collapse_into_governed_subjects(self):self.item('node')['namespace']='lab.governed-subject';self.reject()
    def test_duplicate_item_rejected(self):self.value['items'].append(copy.deepcopy(self.item('node')));self.reject()
    def test_selected_item_cannot_be_dropped(self):self.value['items'].pop();self.reject()
    def test_accounting_rejected(self):self.value['counts']['node']+=1;self.reject()
    def test_selected_original_digest_rejected(self):self.item('file')['source_binding']['sha256']='0'*64;self.reject()
    def test_unselected_source_file_rejected(self):self.item('file')['source_binding']['path']='private/key.pem';self.reject()
    def test_row_selector_is_exact(self):self.item('node')['source_binding']['selector']='/nodes/37';self.reject()
    def test_source_record_digest_is_exact(self):self.item('node')['record_structure_sha256']='0'*64;self.reject()
    def test_source_role_does_not_establish_domain_conformance(self):self.item('node')['contract_fit']['domain_conformance']=True;self.reject()
    def test_source_body_is_not_materialized_by_inventory(self):self.item('node')['source_record']={'meaning':'private source'};self.reject()
    def test_private_row_cannot_become_public(self):self.item('node')['privacy']='public-scoped-source';self.reject()
    def test_public_dependency_body_export_still_requires_its_scope(self):self.item('dependency')['public_body_export_allowed']=True;self.reject()

    def test_stale_dependency_cannot_be_referenced_as_current(self):
        item=next(i for i in self.value['items'] if i['disposition']=='block');item['disposition']='reference';self.reject()

    def test_unavailable_dependency_cannot_have_a_fabricated_binding(self):
        item=next(i for i in self.value['items'] if i['disposition']=='block');item['source_binding']={'path':'invented'};self.reject()

    def test_node_dependency_gaps_cannot_be_dropped(self):
        item=next(i for i in self.value['items'] if i.get('unresolved_dependency_ids'));item['unresolved_dependency_ids']=[];self.reject()

    def test_legacy_edge_cannot_be_global_projection(self):self.item('relation')['edge_mode']='global-projection';self.reject()
    def test_legacy_predicate_cannot_select_global_axis(self):self.item('relation')['contract_fit']['source_relation_vocabulary_is_global_axis']=True;self.reject()
    def test_global_typed_relation_cannot_be_invented(self):self.item('relation')['global_typed_relation_ref']='relation.member-of';self.reject()
    def test_original_relation_direction_is_preserved(self):self.item('relation')['direction']='reverse';self.reject()
    def test_original_relation_endpoints_are_closed(self):self.item('relation')['target_endpoint_id']='unknown';self.reject()
    def test_source_residue_cannot_become_challenge_event(self):self.item('residue')['intended_carrier_ref']='cal.artifact-type.challenge-event/v1';self.reject()
    def test_excluded_packages_accounted(self):self.value['excluded_packages'].pop();self.reject()
    def test_standalone_successor_cannot_replace_historical_epoch(self):self.value['standalone_product_successor']['disposition']='import';self.reject()
    def test_unlisted_observation_path_rejected(self):self.value['external_observations'][0]['material_path']='/tmp/secret';self.reject()
    def test_unlisted_external_binding_rejected(self):self.value['external_source_bindings'].append({'path':'/tmp/key','sha256':'0'*64});self.reject()

    def test_external_observation_drift_rejected(self):
        self.value['external_observations'][0]['observed_sha256']='0'*64
        with self.assertRaises(RepresentationFault):verify_observations(self.value)

    def test_source_path_traversal_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix='cal-O04-path-guard-') as temp:
            root=Path(temp);(root/'link').symlink_to('/tmp')
            for path in ('../outside','/absolute','link/data.json','./file.json'):
                with self.subTest(path=path),self.assertRaises(RepresentationFault):safe(root,path)


if __name__=='__main__':unittest.main()
