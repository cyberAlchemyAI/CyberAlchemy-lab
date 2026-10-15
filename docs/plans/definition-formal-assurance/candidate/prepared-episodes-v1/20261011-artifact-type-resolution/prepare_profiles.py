from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions';u=base/'cal.definition.artifact-type-resolution';prev=base/'cal.definition.artifact-type-request'
x=json.loads((u/'carrier-consumer-inspection.json').read_bytes());assert x['check_count']==40 and x['pure_lookup_probe_count']==12
review='''# Artifact Type Resolution: consumer correspondence review

This follows the separately audited sixteen-input typed stage. It records exact current source and consumer bindings, then isolates the two pure functions `pointer_get` and `resolve` from the bound shared validator using their syntax trees. No imports or main entry point from that module, package validator, writer, operational resolver, registry adapter, or admission command was executed. The twelve fixture results are auxiliary candidate observations; no canonical result artifact was created. Forty exact checks passed with authority effect none.

## Selected contracts and input domains

The current143-contract registry has two admitted-current types directly bound to current Resolution candidate.2: Artifact Type Registry/v2 under C68 and Artifact Type Request/v1 under C70. Their artifact and schema bytes, six exact semantic bindings, and owner-admitted decision overlays were checked against the snapshot and current files. The embedded type bodies still carry candidate-unadmitted and none-effect postures. A current carrier admission decision is not acceptance of this sorted translation or product activation of the resolver.

The isolated helper consumes the historical candidate-postimage registry with25entries:22admitted-current and3admitted-historical. Its exact v1 schema validates the fixture and limits entry lifecycle states to admitted-current or admitted-historical. The current Request wrapper explicitly points to this legacy registry. The current v2 registry has admitted_contracts and descriptors instead of entries. Passing a copy of that raw current registry to the exact helper raises KeyError entries, without mutating the input. No invented adapter was substituted to hide this result.

## Matching and result observations

Unknown and unregistered explicit references produce zero matches. A registered explicit current reference resolves to its exact type. An explicit historical reference resolves and retains admitted-historical in the matched entry; its discriminator alone does not produce a current match. Current discriminator evidence resolves exactly. Explicit and discriminator routes to the same type deduplicate to one type identity while retaining both evidence items. A historical explicit reference combined with a different current discriminator produces an ambiguous two-type match set. Repeated execution on identical fixture bytes produces the same structured observation, with the exact registry_id, match_count, sorted matches, matched entries, exclusions, and authority_effect none.

Moving the same carrier to another directory, filename, and extension changes artifact_path only. The relevant result projection, including match set and recorded lifecycle state, remains equal. Full byte equality across movement is not claimed because the result records the supplied path. A deliberately invalid-looking subject still resolves by its declared exact type/discriminator; that observation confirms that resolution itself does not execute subject schema validation or grant type admission. Input carrier authenticity and schema conformance remain separately mapped obligations.

## RES-CONSUMER-FINDING-001: registry representation and route

The exact helper expects entries while the current operational registry provides admitted_contracts/descriptors. The current Request wrapper retains the legacy route. A future implementation decision must select an exact input registry representation and accepted mapping of identity, admitted-current versus admitted-historical state, discriminator, schema/carrier bindings, and admission decision. Retaining a candidate proposal or translating fields in memory would not itself establish currentness, canonical resolution, or activation. The remediation target is the shared validator and Request route, subject to their enclosing product and owner decisions. Status unresolved;accepted semantic-map references empty.

## RES-CONSUMER-FINDING-002: admission eligibility and schema responsibility

The explicit-reference branch checks matching identifiers among entries without rechecking lifecycle admission. The declared legacy input schema already excludes candidate entries. A copied registry with an injected candidate entry fails that schema, and the pure helper on that invalid fixture nevertheless resolves the candidate identifier with none effect. This is an out-of-schema robustness observation. It establishes neither a compliant-input violation of Resolution nor an admission grant. The pending source-to-consumer map must say where exact registry validation is required, which inputs the executable operation accepts, and how the candidate exclusion is preserved under any v2 route. Do not broaden the typed input domain silently or report this negative probe as a current production defect. Status unresolved;accepted semantic-map references empty.

## RES-CONSUMER-FINDING-003: structured output classification

The helper emits schema_version cyberalchemy-lab-artifact-type-resolution-result/v1. None of the143current registry contracts registers that discriminator. A structured local result can still be an auxiliary observation. If it is intended to become a governed canonical machine artifact, its type, result identity, exact registry relationship, matched entry/state mapping, provenance, and lifecycle must be explicitly selected. The absence alone is not a malformed-artifact or admission finding, and this analysis does not author a new type. The remediation target is an accepted classification and ownership decision for resolver results before any broader output claim. Status unresolved;accepted semantic-map references empty.

## RES-CONSUMER-FINDING-004: admission overlays and product activation

Current Registry-v2 and Request-v1 carrier meanings bind the current Resolution source, but retain candidate body posture. Source residue explicitly keeps the resolver as candidate product code until the enclosing product candidate is approved and separately admitted or activated. C68 and C70 carrier overlays do not discharge that product obligation or accept this formalization. Preserve the current source/admission observations and the embedded historical posture separately. The remediation target is owner-reviewed source, carrier, and product claim ceilings with exact acceptance references. No shared code, source, carrier, admission record, or operational registry was edited. Status unresolved;accepted semantic-map references empty.

## Qualified map obligations and completion ceiling

Operation, carrier, registry, type, state, result, path and discriminator identities need accepted denotations. The union, evidence eligibility, deduplication, zero/single/multiple result partition, selected type/state guard, none-effect projection, and movement equivalence require explicit field maps. Schema responsibility, candidate exclusion, registry-version mapping, and product activation remain open. Hypothetical frames can expose missing or invented mappings; they cannot authenticate the mapping, source fidelity, consumer execution, or owner acceptance. Each of the four findings remains unresolved. Whole-definition proof, joint semantic consistency, accepted source precedence, and semantic_ready remain pending or false. The frozen typed inputs and all7611prior candidate files remain byte preserved.
'''
with (u/'CONSUMER-REVIEW.md').open('x') as f:f.write(review)
s=(prev/'verify_authority_profile.py').read_text().replace('Request','Resolution').replace('request','resolution')
a=s.index('AXES=');z=s.index('\ndef envelope',a)
s=s[:a]+"AXES=list(b.FACETS)+['operation_identity_key','carrier_identity_key','registry_identity_key','type_identity_key','state_identity_key','result_identity_key','discriminator_path_key','discriminator_value_key','explicit_admitted_current_or_historical','current_only_discriminator','exact_union','deduplication','zero_single_multiple_outcomes','recorded_lifecycle_state','none_effect','movement_result_projection','candidate_exclusion','schema_validation_responsibility','product_activation_residue','legacy_and_current_registry_map']\nFORBIDDEN=['path_proves_identity','filename_proves_type','extension_proves_type','nearest_name_is_evidence','candidate_explicit_is_admitted','historical_discriminator_is_current','both_routes_count_as_two_types','unknown_reference_is_nearest_type','same_input_changes_match_set','path_projection_difference_changes_type','resolution_is_schema_validation','resolution_is_type_admission','declared_none_effect_grants_authority','out_of_schema_probe_is_compliant_violation','legacy_entries_are_current_v2_without_map','result_discriminator_absence_is_admission_defect','carrier_admission_activates_resolver','hypothetical_map_is_owner_acceptance']"+s[z:]
s=s.replace("'candidate-unmatched-intake'","'candidate-exact-match-union'").replace('requestOwner','operationRegistry').replace('resolutionOwner','operationRegistry')
s=s.replace("MAP_FIELDS=AXES+['three_current_meaning_bindings','carrier_body_vs_current_overlay','operational_intake_route','concrete_discriminator_matching','compatibility_analysis_correctness','owner_acceptance_and_claim_ceiling']","MAP_FIELDS=AXES+['six_current_meaning_bindings','carrier_body_vs_current_overlay','structured_result_classification','concrete_discriminator_matching','schema_input_domain_correctness','owner_acceptance_and_claim_ceiling']")
s=s.replace("observation['real_resolution_subject_type_or_authority_created']","observation['real_subject_type_result_or_authority_created']")
s=s.replace("'isolated_pure_resolution_helper_executed':True","'isolated_pure_resolver_functions_executed':True").replace("'actual_resolution_subject_type_or_admission_created':False","'actual_subject_type_result_or_admission_created':False")
s=s.replace('hyp:Resolution-v1-legacy-route','hyp:Request-v1-legacy-route').replace('Identity,dependency,owner-selection,registry-version,lifecycle and operational intake routes remain unaccepted.','Identity,registry-version,input domain,result lifecycle and product activation maps remain unaccepted.')
ast.parse(s)
with (u/'verify_authority_profile.py').open('x') as f:f.write(s)
for name in ['static_snapshot_reuse.py','verify_static_snapshot_reuse.py','verify_dependencies.py','replay.py']:
 s=(prev/name).read_text();ast.parse(s)
 with (u/name).open('x') as f:f.write(s)
s=(prev/'verify_current_inventory.py').read_text().replace('eighty-six','eighty-seven').replace('!=86','!=87').replace('cal.definition.artifact-type-registry/','cal.definition.artifact-type-request/').replace("'F04-T.cal.definition.artifact-type-resolution'","'F04-T.cal.definition.canonical-package-home'");ast.parse(s)
with (u/'verify_current_inventory.py').open('x') as f:f.write(s)
s=(p.parent/'20261011-artifact-type-request/capture_delivery_checks.py').read_text().replace('cal.definition.artifact-type-request','cal.definition.artifact-type-resolution');ast.parse(s)
with (p/'capture_delivery_checks.py').open('x') as f:f.write(s)
print('Prepared Resolution qualified frames,source maps,static-reuse,dependency,inventory and fresh replay helpers.')
