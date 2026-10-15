"""Source-first design notes; does not create the next native interpretation."""
from pathlib import Path
import hashlib,json,re
root=Path.cwd();out=Path(__file__).resolve().parent
source_path='authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/capability-instance/v1/definition.json'
raw=(root/source_path).read_bytes();source=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5'
assert not(root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance').exists()
expression=source['voices']['scientific_formal']['formal_expression']
fields=[s.strip() for s in re.search(r'CapabilityInstance = \(([^)]+)\)',expression).group(1).split(',')]
types=['IdentityRef','ProductCapabilityVersionRef','CoordinationContextRef','BoundedContextCollectionRef','ParentAuthorityClaimRef','InstanceAuthorityClaimRef','InheritedContractRef','ExtensionScopeRef','AdoptionDecisionRef','ConstructionBindingRef','ConformanceCollectionRef','LifecycleRef','DriftRouteRef','RecompositionRouteRef','RecursionContractRef','TerminalHandoffRef']
assert len(fields)==len(types)==16
registry=json.loads((root/'authority/definitions/registry.json').read_bytes())
wanted={'Capability Instance','Product Capability','Bounded Context','Coordination Context','Conformance','CyberAlchemy Construction Method','Parent-Instance Authority Separation Invariant'}
selected=[]
for row in registry['entries']:
 if row.get('term') in wanted and registry['current_lookup'].get(row['definition_id'])==row['definition_id']+'@'+row['version']:
  assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
  selected.append(row)
assert len(selected)==7
design={'schema_version':'capability-instance-source-first-design/v1-candidate','source':{'definition_id':source['definition_id'],'version_ref':source['definition_id']+'@'+source['version'],'path':source_path,'sha256':hashlib.sha256(raw).hexdigest()},'tuple_fields':[{'field':field,'proposed_sort':sort} for field,sort in zip(fields,types)],'additional_source_obligation':{'name':'owner locality','proposed_sort':'LocalOwnerRef','source_selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/testable_conditions/0'],'changes_canonical_tuple':False},'exact_current_reference_observations':selected,'native_creation_requires_Project_full_separate_audit0':True,'native_interpretation_created':False,'compiled_theory_or_models_created':False,'proposed_denotations_accepted':False,'actual_instantiation_adoption_binding_conformance_or_authority':False,'source_fidelity':'pending','semantic_ready':False,'authority_effect':'none','claim_ceiling':'Unexecuted source-first design notes, not accepted interpretation, source precedence review, conformance, implementation or proof.'}
with (out/'next-CapabilityInstance-type-design.json').open('x') as f:json.dump(design,f,indent=2,sort_keys=True);f.write('\n')
table='\n'.join(f'| {field} | {sort} |' for field,sort in zip(fields,types))
text="""# Capability Instance: next source-first type and logic design

These notes prepare the next Definition while Project's full-delivery checks run. Native authoring still requires Project's actual full seal and separate audit. No next-unit theory, model, compiled interpretation, operational instance or authority effect is created here. The proposed sorts and guards require source-owner fidelity review.

## Exact source and its positive genus

Select cal.definition.capability-instance@1.0.0-candidate.1, digest d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5, under C18. Preserve C17's separate admitted evidence-use scopes for CAV2-D64 and CAV2-D67. The existing source preparation records twenty units, twenty-seven checks and a 4,095-byte projection. Those are observed source bindings, not accepted interpretation.

The positive genus is an owner-local, version-exact realization or specialization of one Product Capability inside explicitly declared coordination and semantic contexts. The genus must remain represented alongside its tuple. Preserve the inclusive realization-or-specialization alternative, including overlapping declarations where justified, instead of silently selecting only one branch. A directory, component, deployment or conformance result cannot stand in for the instance identity. Actual realization is an independent evidence target rather than a consequence of naming the required references.

## Tuple and companion owner obligation

| Source coordinate | Proposed distinct sort |
|---|---|
"""+table+"""

The sixteen coordinate names and order come directly from the source. Local owner is also explicit in the normative statement and first testable condition, although absent as a named tuple coordinate. The candidate should therefore carry a separate owner-locality interpretation obligation. Omitting it would lose source meaning; adding it to the canonical tuple would change the source. An owner reference and a locality declaration need accepted denotations before establishing actual ownership or authorization. The Definition's semantic_owner_ref identifies its Definition owner; it cannot silently substitute for an instance's local owner or its parent's owner.

Distinct sorts prevent an adoption decision, a conformance collection, a lifecycle value and a construction binding from collapsing into interchangeable opaque tokens. Reference-handle guards should select declared carriers and preserve their exact bindings. A nonempty collection handle does not alone establish that its contents have the intended meaning. The source does not give numerical extension or conformance cardinalities, so those must not be invented. Semantic-context presence must be accounted for explicitly, with any proposed collection interpretation left reviewable.

## Identity and version logic

One selected Instance nominates exactly one Product Capability version. The candidate needs a version-to-parent reference map and a shared identity carrier for the required Instance-versus-Parent inequality. Comparing elements of unrelated sorts would make that boundary trivially true. Conversely, equal printed reference strings cannot establish an accepted cross-definition identity relation.

Version exactness is a binding condition. It does not impose a universal latest-version rule, semantic-version ordering or promotion authority. A complete finite witness should include a selected instance, its exact parent version, declared contexts and every tuple component. Another instance may share the same parent version if the source permits it. No unsupported global one-instance-per-parent rule should be introduced.

## Parent and instance authority lanes

ParentAuthorityClaim and InstanceAuthorityClaim need separately qualified roles or lane maps. Separation does not require different principals, different strength labels or different textual claim contents. The source requires separate claims and identity, while actual authority must remain independently supported.

Inherited contract, extension scope and adoption decision are declared bindings. A parent claim, copied folder, inherited contract or conformance reference does not execute adoption or confer an instance authority. A model with independent legitimate authority remains possible. The theory must not turn this independence into a universal prohibition on authorized instances.

The Parent-Instance Authority Separation Invariant is a separately qualified dependency. Its current Definition bytes were observed; its complete theory is not silently merged. Accepted shared interpretation and concrete source-to-consumer maps remain later assurance work.

## Construction, recursion and terminal handoff

ConstructionBinding refers to the source's D65 construction obligation. CyberAlchemy Construction Method is the exact current Definition reference observed for follow-up selection. These notes do not infer an accepted D65 stage map from the similar name or import an uninspected external construction system. Actual completion of construction stages remains distinct from a declared binding.

Recursion includes a budget or stop and a recomposition route. Preserve the inclusive alternative, with witnesses for budget-only, stop-only and overlapping declarations where an accepted interpretation permits them. The recursion_stop coordinate can nominate the declared recursion contract without rewriting the tuple to force a second field. A bare nonempty token must not replace the budget-or-stop meaning.

Drift route, recomposition route and terminal handoff retain separate roles. Their presence does not prove actual bounded termination, successful handoff, drift detection or recomposition. Lifecycle likewise requires an explicit declared carrier without inventing activation transitions or interpreting admission posture as runtime state.

## Conformance and outcomes

Conformance is separate from authority. A proposed guard can reject interpreting a conformance result as an authority grant, while actual conformance and actual authority remain independent targets. Include a conformant-but-unauthorized witness and an independently authorized witness; do not assert that conformance can never coexist with justified authority.

The actual targets should account for realization, local ownership, context resolution, correct parent binding, contract inheritance, extension permission, adoption, construction completion, conformance, lifecycle operation, drift handling, recomposition, budget enforcement or termination, terminal handoff, source fidelity and consumer alignment. Their final denotations and source-query obligations require exact clause accounting, not generic outcomes borrowed from a preceding Definition.

## Native sequence and decisive controls

After Project's actual full audit, select the exact next source and prerequisites, create a qualified signature, account for all source spans, author necessary guards and requested populations, and evaluate supplied finite controls. Keep encoded, explanatory and deferred text explicit. Do not use complete character accounting as proof of semantic fidelity.

Negative cases should independently remove local owner, exact parent version, each context binding, each source tuple coordinate, authority-lane separation, recursion alternatives, recomposition and handoff. Identity-collapse and conformance-as-authority cases must preserve all other guards. Structural malformed cases separately exercise sort errors, incomplete total functions and bad reference tuples.

Source observations and pure projections precede the types-stage freeze. Actual carrier/profile observations, qualified dependency and whole-inventory refresh, six fresh delivery checks, full aspect review, seal and separate audit follow. These are execution dependencies; an acyclic plan does not prove semantic consistency. Original T/O/E/R/J obligations, owner acceptance and whole-definition proofs remain intact.
"""
with (out/'NEXT-CapabilityInstance-TYPES-LOGIC.md').open('x') as f:f.write(text)
print(json.dumps({'result':'Source-first next-unit design prepared','tuple_coordinates':16,'companion_owner_obligation':True,'current_exact_reference_observations':7,'review_words':len(text.split()),'native_interpretation_created':False,'authority_effect':'none'}))

