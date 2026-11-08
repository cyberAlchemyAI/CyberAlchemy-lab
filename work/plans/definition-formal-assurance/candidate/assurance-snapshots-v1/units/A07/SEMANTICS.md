# Independent record semantics for the source-backed pilot successor

This is a candidate semantics contract for conditional finite record interpretation. It precedes the search checker planned in A08. The definitions below describe the intended meaning independently of a Python function returning true. It is a partial interpretation of seven exact current definition identities, with source fidelity and semantic dependency closure pending.

## Subjects, types and scopes

A state s contains one governed object identity, one snapshot revision, an exact query context q, seven posture components, provenance information, asserted claims, independent permit-grant and responsibility-assignment pools, authority boundaries and principal-role bindings. A state revision identifies a snapshot; distinct revision labels do not prove a historical ordering.

The query q names scope, principal, authority surface, object, operation and effect. These are distinct nominal fields, even if a person acts under several roles. A visible label, file location, successful validation or shared source ancestor supplies no implicit substitution between them. The modeled objects are hypothetical named records, without an assertion that every Artifact or Governance Decision requirement is fulfilled.

A claim c names a position kind, an assignment reference and scope, owner role, principal, surface, object, operation, basis, effect and challenge route. A field can be explicitly unavailable in a candidate assertion. The added principal field supports the separately selected Authority Boundary conditions; it does not overwrite the source's inherited eight-field claim tuple.

A permit grant g is an independently supplied hypothetical owner act with complete fields and selected boundary and role-binding references. A duty assignment d independently names its responsible role/principal, bounded scope, object, operation, intended outcome, basis, owner route and role binding. Neither pool is constructed from the presence of a claim or a source trail.

## Rights, responsibilities and assertions

Let B be the selected boundary records and H the selected principal-role bindings. Qual(g,q,B,H) holds precisely when g matches all fields of q, its referenced binding assigns its principal to its owner role, and its referenced boundary has that principal, role and scope, contains the governed object and allowed effect, excludes no such effect, and has the matching challenge route. Exclusion takes precedence over inclusion.

Right(s,q) holds when some grant in the selected pool satisfies Qual. Its denotation does not require a separate assertion record. The pool's legitimacy and H are explicitly selected conditional premises, not authenticated external facts. An empty matching set means no right is established in this selected model; it does not prove absence of all possible external grants.

Duty(s,q) holds when an independently supplied assignment matches q's principal, scope, object, operation and intended outcome and its selected role binding matches the responsible role/principal. The owner route and basis remain explicit. Duty does not imply Right. A duty can exist without a separate assertion, and its presence does not prove the outcome was achieved or that someone can cause it.

AuthorityPosition(s,q) is a tagged union of qualified right grants and qualified duty assignments. This follows Authority's target-specific right-or-responsibility formulation while preserving Responsibility's explicit separation from permission. It is not an identification of the distinct definition IDs and is not a proof of whole-source correspondence.

An explicit claim has all its inherited fields named. A supported right claim additionally identifies a qualified grant with identical fields. A supported responsibility claim identifies a qualified duty with the same responsible role/principal, scope, object, operation, basis, intended outcome and selected answering/challenge route. Using the duty's owner route for this latter record slot is a candidate profile interpretation, subject to owner review. Claims with unavailable fields or no matching assignment remain expressible as unsupported assertions.

## Provenance and information

The seven posture axes are kind, status, evidence, commitment, provenance, owner and residue. Each has an explicit information state: known, unknown, deferred or source-local. Known values are explicit tokens; unknown/deferred values are unavailable, and source-local values retain their scope. This is information about a component, rather than a change to classical truth semantics or a complete universal status taxonomy.

Known provenance is a finite sequence of typed steps and, where applicable, explicitly recorded gaps. A typed step has identity, source reference, relation reference, operation reference, owner reference and posture reference. A gap has its own identity, residue reference and owner route. Step identities are distinct. A complete trail is nonempty and has no gaps; an incomplete trail is nonempty and contains at least one explicitly routed gap. Known empty provenance has a zero-length sequence. Unknown or deferred provenance has unavailable steps rather than an empty sequence. Source-local provenance retains the scope in which its declarations can be used.

The zero-length representation preserves the source's star operator. It does not itself establish a useful origin explanation, no historical transformations or an absence of hidden lineage. Those questions remain in FID-PROV-EMPTY-001. A record with malformed or unrouted gaps is outside this selected well-formed record interpretation, rather than being converted into a known negative statement about historical origin.

Traceable(s,q) is the selected nonempty typed-trail condition, with all declared gaps routed and a matching scope for source-local declarations. Its meaning here is conditional declaration shape and scope, not authentication of source references, admitted relation kinds, truthful history or permission.

## Local admission-use coupling

A supported right claim is usable without a provenance requirement in the uncoupled candidate profile. In the explicitly selected admission-use profile, its usability additionally requires Traceable(s,q). The profile is bound to scope:pilot-local-use, surface:pilot-rules, operation count-as-local-rule and effect permitted-local-use. Invoking it for a different scope, surface, operation or effect is rejected; it cannot silently become a global policy. Known empty, unknown, deferred or differently scoped local declarations do not meet that selected use condition.

This condition applies to usability of a supported claim for one selected operation, rather than global existence of AuthorityPosition. A qualified grant can exist with unknown provenance. Recording a better trail cannot create that grant, and withholding use under the local trace policy cannot remove it. An assigned duty is neither a permission nor automatically a supported right claim.

The admission-use policy is a candidate owner-review choice. It is not inferred as a universal implication from the general Provenance definition or from registry admission of its source artifact. No actual admission, promotion or external effect occurs.

## Exact transition frame

A move m names the exact object, q, before and after revisions and canonical digests of complete states. Its intent names nonempty actual changed components. A recorded additional change names a component, exact before and after component digests, and an explicit decision basis. The provenance component includes its posture information and actual trail together; a posture label alone cannot stand in for changed records.

Let Delta(s,t) be all changed posture and record-pool components. Frame(m,s,t) requires matching subject/context/state bindings, distinct snapshots, every intended component actually changed, and every changed component either intended or explicitly recorded with the correct component bytes. Additional change records cannot name unchanged or duplicate components.

Grant and duty pools have separate exact assignment identities. Every addition, removal or revision requires its own before/after digest pair, using an unavailable side for addition or removal, plus an explicit basis. A changed pool's axis label or a provenance-only intent does not substitute for these records. Retaining an old complete-state digest while changing a claim or assignment fails binding before frame evaluation.

Boundary or principal-role binding mutation is outside this pilot even if move metadata announces it. A user preference, workflow setting or recorded coupling cannot widen an authority boundary. Recording a permitted grant delta checks a candidate description of an act; it does not authenticate the act or authorize an operator to execute it. All mutations are hypothetical records in candidate storage.

## Logic and proof boundaries

These are explicit finite record predicates and one-step frame conditions. They do not constitute full deontic logic, proof of obligation fulfillment, unbounded temporal liveness, arbitrary delegated authority, revocation/challenge resolution, complete lineage graph semantics or generic checker correctness. Those extensions need their own reviewed contracts and evidence.

The source review packets account for all 166 selected meaning-text units. Their clauses remain explicitly unresolved for whole-definition translation. The separate source-rule map binds candidate record rules to exact normative, formal and boundary spans. Neither character accounting nor a passing record example proves natural-language fidelity, complete semantic closure or all-183 joint consistency.
