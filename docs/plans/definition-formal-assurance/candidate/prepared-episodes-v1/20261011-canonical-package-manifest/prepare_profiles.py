from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions';prev=base/'cal.definition.canonical-package-home';u=base/'cal.definition.canonical-package-manifest'
observation=json.loads((u/'carrier-consumer-inspection.json').read_bytes());assert (observation['check_count'],observation['shape_probe_count'],observation['shape_acceptances'])==(31,40,11)
typed=json.loads((u/'types-logic-receipt.json').read_bytes());assert len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False and json.loads((p/'typed-stage-audit-command-result.json').read_bytes())['exit_code']==0
s=(prev/'verify_authority_profile.py').read_text().replace('CanonicalPackageHome','CanonicalPackageManifest').replace('cal.definition.canonical-package-home','cal.definition.canonical-package-manifest')
a=s.index('AXES=');z=s.index('\ndef envelope',a)
s=s[:a]+"AXES=list(b.FACETS)+['governed_surface_universe','unique_entry_surface','unique_entry_path','exact_self_entry','surface_role_map','canonical_carrier_identity','admitted_resolution_relation','declared_count_vs_actual','current_registry_route','nested_own_manifest','parent_relation_endpoints','nearest_package_correspondence','membership_identity_type_preservation','schema_domain_authenticity','consumer_migration_route']\nFORBIDDEN=['directory_defines_membership','nonempty_owner_string_authenticates_owner','single_nominee_hides_duplicate_rows','schema_count_is_computed_resolution','unregistered_type_ref_is_admitted','candidate_result_is_admitted','schema_PASS_proves_theory','schema_helper_authenticates_owner','same_sort_names_prove_shared_meaning','omitted_surface_proves_empty_governed_set','surface_role_is_CPH_facet_kind','opaque_child_manifest_ref_proves_existence','true_lifecycle_bool_proves_recovery','duplicate_nested_rows_prove_unique_relation','declared_nearest_proves_physical_nearest','membership_changes_artifact_identity_or_type','C70_admission_accepts_formalization','absent_example_root_authorizes_migration','hypothetical_map_is_owner_acceptance']"+s[z:]
s=s.replace('candidate-owner-unit-carrier-home','candidate-manifest-membership-nesting').replace('declared_and_actual_home_routes_separate','declared_and_actual_manifest_routes_separate').replace('exact-unaccepted-resolution-profile','exact-unaccepted-manifest-profile')
a=s.index('MAP_FIELDS=');z=s.index('\ndef valid_frame',a)
s=s[:a]+"MAP_FIELDS=AXES+['four_current_meaning_bindings','carrier_body_vs_current_overlay','governed_file_evidence','typed_result_provenance','nested_carrier_existence','owner_acceptance_and_claim_ceiling']"+s[z:]
s=s.replace("['hyp:CPH-C43-owner-unit-meaning','hyp:Manifest-C70-executable-carrier','hyp:Capability-v2-independent-successor']","['hyp:CPM-C53-membership-nesting-meaning','hyp:Manifest-C70-executable-carrier','hyp:Resolution-current-registry-input-result-map']").replace('changed-resolution-owner-field','changed-manifest-owner-field').replace('aggregateOwner','manifestOwner')
s=s.replace('Owner/unit/home,carrier uniqueness,facet,typed-edge,index,movement,computed resolution,migration and successor maps remain unaccepted.','Manifest/home/owner,governed membership,self-entry,roles,admitted results,current registry,nested carrier,parent relation,nearest package,membership preservation and migration maps remain unaccepted.')
ast.parse(s)
with (u/'verify_authority_profile.py').open('x') as f:f.write(s)
for name in ['static_snapshot_reuse.py','verify_static_snapshot_reuse.py','verify_dependencies.py','replay.py']:
 s=(prev/name).read_text();ast.parse(s)
 with (u/name).open('x') as f:f.write(s)
s=(prev/'verify_current_inventory.py').read_text().replace('eighty-eight','eighty-nine').replace('Eighty-six-draft','Eighty-nine-draft').replace('!=88','!=89').replace('cal.definition.artifact-type-resolution/','cal.definition.canonical-package-home/').replace("'F04-T.cal.definition.canonical-package-manifest'","'F04-T.cal.definition.canonical-representation-invariant'");ast.parse(s)
with (u/'verify_current_inventory.py').open('x') as f:f.write(s)
s=(p.parent/'20261011-canonical-package-home/capture_delivery_checks.py').read_text().replace('cal.definition.canonical-package-home','cal.definition.canonical-package-manifest');ast.parse(s)
with (p/'capture_delivery_checks.py').open('x') as f:f.write(s)
print('Prepared CPM profiles,static reuse,dependencies and current inventory;frozen16 unchanged.')
