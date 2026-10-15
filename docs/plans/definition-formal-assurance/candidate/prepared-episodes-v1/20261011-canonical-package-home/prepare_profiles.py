from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions';prev=base/'cal.definition.artifact-type-resolution';u=base/'cal.definition.canonical-package-home';observation=json.loads((u/'carrier-consumer-inspection.json').read_bytes());assert (observation['check_count'],observation['shape_probe_count'],observation['shape_acceptances'])==(34,37,9)
review='''# Canonical Package Home: current carrier and consumer review

This follows the separately audited sixteen-input typed stage. Thirty-four exact current checks passed. Thirty-seven copied manifest schema probes include nine acceptances;four declared negative manifest witnesses and four ad hoc Definition-package hostile subjects were also evaluated. No package validator entry point,receipt writer,carrier generator writer,operational migration or successor consumer was executed. One pure manifest helper,one pure Definition hostile helper,and two pure projection functions were selected by syntax tree from exact bound source bytes. The frozen typed stage and all7715previous candidate files are preserved.

## Exact current contracts and representations

The current143-contract registry has one admitted-current type directly binding current CPH candidate.1:Canonical Package Manifest/v1 at its executable-surface candidate under C70. Exact artifact and schema digests aredf3d8d8180416271d3dc7659f3fefaa697b15b85fe2dcda059037c39ace3c771and33cf444c265d306d6e6eb75338a4b4cccc609ccf7c736f2f39e2af06d109b930. Four current semantic bindings connect Artifact Type,Canonical Package Home,Canonical Package Manifest candidate.2,and Artifact Surface Classification candidate.2. C70's authorization and admission-bundle digests were verified. Embedded artifact status remains candidate-unadmitted with none effect;current overlay and body posture remain separate observations.

Two pure current artifact projections and two pure current manifest projections match their committed bytes without input mutation. The current positive fixture validates under the exact current schema;the historical positive fixture validates under its historical schema. Historical compatibility observations are retained as actual results,not assumed because the public type reference remains v1. The fixture declares an Ontology Product aggregate and owner,not Registry Context. It creates no accepted package or home-selection instance.

## CPH-CONSUMER-FINDING-001: owner,unit and home selection

The closed manifest schema requires aggregate_ref,lifecycle_owner_ref,unit_of_change and package_root as nonempty strings. The pure helper checks surface declarations rather than authenticating those values. Copied fixtures with arbitrary nonempty aggregate,owner,unit and root values pass both the schema and helper. These facts demonstrate the qualified check ceiling;they are not proof that an operational system has accepted those declarations or that the source is violated on an authenticated instance.

Accepted maps must bind the aggregate identity,governed candidate-home domain,lifecycle owner,change unit,recovery boundary,manifest identity,canonical carrier membership and unique home relations. A string named package_root is descriptive input until the appropriate owner selection is bound. Multiple canonical homes across manifests,real source completeness and recovery cohesion are not established by one fixture's fields. Status unresolved;accepted map references empty. Remediation targets:the exact manifest field map and lifecycle-owner selection/evidence protocol.

## CPH-CONSUMER-FINDING-002: declared classification versus computed resolution

The manifest helper rejects duplicate paths,missing or noncanonical self entries,canonical entries without declared resolution count1,and noncanonical entries claiming a type. Duplicate nonself paths pass the schema but fail this helper. Thus the schema and helper have distinct responsibilities;neither may be described as proving every other check.

A copied canonical entry with an unregistered type reference and count1passes both schema and helper. The helper has no registry argument and does not call resolve. Static inspection of the direct package-validator body also finds no direct resolve call;the wrapper retains the explicit legacy25-entry registry route. No raw-current-v2 incompatibility experiment is claimed for this manifest helper,because it consumes only the subject. Actual admitted type resolution needs an accepted link to exact resolver output,registry identity,lifecycle state and carrier bytes. Status unresolved;accepted map references empty. Remediation targets:canonical-entry resolution provenance and the current-versus-legacy registry route,without silently replacing declared counts with inferred operational results.

## CPH-CONSUMER-FINDING-003: facets,views and movement correspondence

Undeclared top-level recovery boundary,governed home candidates,canonical-at relations,facet identities,facet authority scopes,movement evidence and global index bindings are rejected by the closed schema. Their absence as direct fields does not require stuffing every source obligation into this carrier. Separate governed carriers,typed relations,owner decisions or external evidence may carry these meanings. The formalization needs accepted mappings that identify which representation discharges each obligation and preserves independent identities and authority scopes.

Current surface roles include canonical-instance,declared-component,generated-projection,evidence,fixture and transient-state. They are classification roles,not automatically the seven CPH semantic facet kinds. Nested packages declare package/manifest references,relation_kind and independent_lifecycle true. An unbound nested package declaration passes the schema and helper;authentic independent lifecycle,manifest existence,parent relation and recovery separation remain pending. A generated projection can carry optional count1metadata without claiming a canonical type;that observation must not be promoted into actual resolution or canonical status. Status unresolved;accepted map references empty. Remediation targets:facet/role,typed-edge,global-view,movement/decision and independent nested-package source maps.

## CPH-CONSUMER-FINDING-004: current overlays and retained residue

The current manifest body and typed residue still describe manifest/surface Definitions as unadmitted and the type as inadmissible. Current C43/C53 meanings and C70 carrier overlays are admitted. These roles must be preserved separately:retained body history,current admission facts,and formalization acceptance. Carrier admission alone cannot select a home,implement migration or accept this translation's owner/unit/recovery interpretations. Status unresolved;accepted map references empty. Remediation targets:owner-reviewed carrier claim ceilings and residue/current-overlay correspondence. No body,Definition,admission record or canonical registry was rewritten.

## CPH-CONSUMER-FINDING-005: migration and successor enforcement

The source proposes capabilities/registry-context/v1as a home example. That path is absent in the current worktree. The label migration:registry-context is a declared consumer route requiring concrete implementation evidence;the absence of an illustrative root is not a defect or authorization to create or move it.

Capability Instance/v2 exists as an admitted-current C70 contract with exact artifact8292e9c86e578a4022909aea6886de343f18051a61dfe3465f19db9cd6c1c8a5and schemaaf2c05dd637f6a32427020a4c54d85c8324f87302f98a67edf803918ff74ee01. Its direct meaning binding is Capability Instance candidate.1,not CPH. Existence and current admission of that successor contract do not prove CPH manifest/ownership enforcement or operational migration. Status unresolved;accepted map references empty. Remediation targets:the concrete migration route and successor enforcement field/consumer maps. No new capability instance,home selection,manifest instance or filesystem migration was created.

## Definition-package hostile subjects and source drift

The four pure Definition hostile checks reject declared directory-based home selection,multiple canonical homes,index canonical duplication and collapsed co-location identities. These are ad hoc negative subjects in the Definition candidate pack,not canonical manifests with authenticated lifecycle owners. They support the candidate package's stated collapse checks but do not establish positive operational home-selection behavior.

The typed stage retains five exact external selected-content identities and three current line-range coordinate drifts. A current carrier does not accept coordinate equivalence or broaden C43's admitted-for-exact-use source scope. That source finding remains separate from the five carrier/consumer findings. Whole source fidelity,owner-approved denotations,shared consistency,dependency closure and whole-definition proof remain pending. Qualification profiles and finite map frames may expose missing or invented mappings;all accepted mapping references must remain empty until exact owner decisions are supplied.
'''
with (u/'CONSUMER-REVIEW.md').open('x') as f:f.write(review)
s=(prev/'verify_authority_profile.py').read_text().replace('Resolution','CanonicalPackageHome').replace('cal.definition.artifact-type-resolution','cal.definition.canonical-package-home')
a=s.index('AXES=');z=s.index('\ndef envelope',a)
s=s[:a]+"AXES=list(b.FACETS)+['home_candidate_domain','canonical_carrier_member','canonical_at_unique','recovery_unit_map','manifest_fields','facet_identity_scope','facet_authority_scope','facet_kind_map','facet_aggregate_edge','global_view_nonduplication','movement_projection','decision_guard','external_coordinate_equivalence','consumer_selection_route']\nFORBIDDEN=['path_selects_owner_or_home','nonempty_owner_string_authenticates_owner','unit_text_proves_recovery','selector_hides_second_home','declared_count_is_computed_resolution','unregistered_type_ref_is_admitted','surface_role_is_semantic_facet_kind','same_sort_names_prove_identity_inequality','co_location_grants_authority','manifest_schema_PASS_accepts_source_fidelity','nested_manifest_ref_proves_existence','independent_lifecycle_bool_proves_recovery','projection_count_one_makes_canonical','C70_manifest_admission_selects_home','current_successor_contract_proves_CPH_enforcement','absent_example_root_authorizes_migration','recovered_content_accepts_coordinate_update','hypothetical_map_is_owner_acceptance']"+s[z:]
s=s.replace("'candidate-exact-match-union'","'candidate-owner-unit-carrier-home'").replace('historical_and_current_registry_routes_separate','declared_and_actual_home_routes_separate').replace('four_consumer_findings_retained','five_consumer_findings_retained')
a=s.index('MAP_FIELDS=');z=s.index('\ndef valid_frame',a)
s=s[:a]+"MAP_FIELDS=AXES+['four_current_meaning_bindings','carrier_body_vs_current_overlay','current_surface_role_map','computed_resolution_registry_map','schema_domain_and_authentication','owner_acceptance_and_claim_ceiling']"+s[z:]
s=s.replace("['hyp:Request-v1-legacy-route','hyp:Registry-v2-current-route','hyp:CanonicalPackageHome-candidate2-current-meaning']","['hyp:CPH-C43-owner-unit-meaning','hyp:Manifest-C70-executable-carrier','hyp:Capability-v2-independent-successor']")
s=s.replace('operationRegistry','aggregateOwner').replace("assert len(findings)==4","assert len(findings)==5").replace("observation['real_subject_type_result_or_authority_created']","observation['real_canonical_home_manifest_instance_or_authority_created']")
s=s.replace(" and observation['raw_current_v2_helper_observation']['missing_key']=='entries'"," and observation['manifest_helper_consumes_registry'] is False")
s=s.replace('with-four-unresolved-mappings','with-five-unresolved-mappings').replace("'isolated_pure_resolver_functions_executed':True","'isolated_pure_manifest_and_Definition_helpers_executed':True").replace("'actual_subject_type_result_or_admission_created':False","'actual_home_manifest_instance_or_migration_created':False")
s=s.replace('Identity,registry-version,input domain,result lifecycle and product activation maps remain unaccepted.','Owner/unit/home,carrier uniqueness,facet,typed-edge,index,movement,computed resolution,migration and successor maps remain unaccepted.')
ast.parse(s)
with (u/'verify_authority_profile.py').open('x') as f:f.write(s)
for name in ['static_snapshot_reuse.py','verify_static_snapshot_reuse.py','verify_dependencies.py','replay.py']:
 s=(prev/name).read_text();ast.parse(s)
 with (u/name).open('x') as f:f.write(s)
s=(prev/'verify_current_inventory.py').read_text().replace('eighty-seven','eighty-eight').replace('!=87','!=88').replace('cal.definition.artifact-type-request/','cal.definition.artifact-type-resolution/').replace("'F04-T.cal.definition.canonical-package-home'","'F04-T.cal.definition.canonical-package-manifest'");ast.parse(s)
with (u/'verify_current_inventory.py').open('x') as f:f.write(s)
s=(p.parent/'20261011-artifact-type-resolution/capture_delivery_checks.py').read_text().replace('cal.definition.artifact-type-resolution','cal.definition.canonical-package-home');ast.parse(s)
with (p/'capture_delivery_checks.py').open('x') as f:f.write(s)
print('Prepared CPH qualification profiles and current dependency/inventory refresh;typed16unchanged.')
