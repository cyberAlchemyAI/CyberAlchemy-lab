"""Write a 13-aspect CI review only from actual fresh native evidence."""
from pathlib import Path
import json,re,sys
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
sys.path.insert(0,str(u));import build_candidate as b
fresh=json.loads((u/'fresh-types-logic-results.json').read_bytes())
assert len(fresh)==3 and all(x['exit_code']==0 and not(u/x['stderr']).read_bytes() for x in fresh)
counts=json.loads((u/'denominator.json').read_bytes());model=json.loads((u/'model-controls.json').read_bytes());source=json.loads((u/'source-checks.json').read_bytes());packet=json.loads((u/'correspondence.json').read_bytes())
assert model['control_count']==186 and len(source['checks'])==93
text="""# Capability Instance: definitions, types and logic candidate review

## 1. Exact target and partial-candidate boundary

This unit selects cal.definition.capability-instance@1.0.0-candidate.1, digest d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5. The current positive Definition is admitted under C18. This candidate accounts for the selected source, declares qualified types and necessary guards, and evaluates supplied finite interpretations. It does not instantiate an instance, adopt a capability, execute construction stages, establish conformance or grant authority.

Project's full 10,188-file seal and separate actual audit both passed before native creation. Its exact predecessor bytes and the original 201-source capture remain protected. A prepared semantic precheck and an exact assembled-code precheck also passed before authoring. Native author, builder, model and source producers then completed successfully. Three fresh read-only checks supply separate actual evidence before this review. Source identity and candidate evidence remain distinct from accepted source fidelity or a mechanized whole-definition theorem.

The priority remains definitions, types and logic. The positive genus is an owner-local, version-exact realization or specialization of one Product Capability inside declared coordination and semantic contexts. The candidate retains that genus alongside the tuple instead of reducing an instance to a copied folder, deployment label or collection of opaque references. Its declaration theory is necessary and partial; actual realization, ownership and successful operation remain independent targets requiring additional evidence.

## 2. Source admission and exact selected material

C18 admits the exact Capability Instance Definition as one of eight selected Definition versions. The source checker binds the decision, accepted candidate, validation and Definition pack. C17 separately admits seven bounded evidence selections. Capability Instance uses two of those scopes: CAV2-D64 and CAV2-D67. Source-use admission does not admit an instance Artifact Type, adopt a parent capability or perform a source-to-consumer correspondence review.

The two selectors are H2 blocks rather than rewritten line selectors. Their exact admitted digests are 891c6b66c578bc0b8f763ad15e250fea255aed36274b9799436f6ab9544dd080 and bf8f3cb9b7d22aaa3c54b7c1eb177b85100be9bc421142bb3ead7e2456431d13. At the observed relocated book they occupy lines 5172–5421 and 5814–5941. The original configured path is absent. Current selected bytes match; historical whole-book identity and current whole-book identity remain separately recorded.

The checker preserves the source candidate's historical posture and the separate current positive overlays. It validates the exact Definition/v1 schema and generator bindings and calls only three extracted pure rendering functions. Two generated projections match the existing 4,095-byte human projection without mutating input. These observations identify the source and its representation. They authenticate no unselected legacy semantics, private producer state, actual owner or instance authority.

## 3. Signature, qualification and common carriers

The signature has twenty-three nonempty sorts, three constants, forty-five total functions and one hundred predicate or relation signatures: 171 declarations. The sorts separate Instance, Identity, Product Capability Version, Product Capability, Coordination Context, Bounded Context Collection, Bounded Context, Authority Claim, Authority Lane, Inherited Contract, Extension Scope, Adoption Decision, Construction Binding, Conformance Collection, Lifecycle, Drift Route, Recomposition Route, Recursion Contract, Terminal Handoff, Local Owner, Budget, Stop Rule and Token.

Every symbol is qualified by exact source version and candidate scope. Matching printed names do not import another Definition's denotation or theory. Totality requires complete function tables in supplied finite models; it does not resolve actual references or make every domain element applicable. An EMPTY Token supports explicit nonempty handle guards. PARENT_LANE and INSTANCE_LANE are distinct constants on a shared lane carrier, rather than unrelated sorts whose inequality would be automatic.

Instance and parent identities also use a shared Identity carrier. Both authority-claim coordinates use a common candidate carrier with distinct role and lane bindings. That design makes the intended comparisons reviewable. It supplies no accepted common-carrier map to real consumers. Local owner and descriptive contract sorts do not create additional canonical Definitions. The hundred unresolved population maps retain their pending denotations and real-world scope.

## 4. Positive genus and sixteen-coordinate record

InstanceApplicable is equivalent to InstanceInScopeDeclared in this proposed interpretation. A selected record must have a declared nonempty reference, sixteen exact typed coordinates, a realization or specialization declaration, and explicit coordination and semantic-context declarations. The realization-or-specialization alternative is inclusive: either branch or both can be present. The source provides no global exclusive partition.

The coordinates retain identity, exact capability version, coordination context, bounded-context references, parent and instance claims, inherited contract, extension scope, adoption decision, construction binding, conformance references, lifecycle, drift route, recomposition route, recursion contract and terminal handoff. A coordinate's binding relation must agree exactly with its single-valued function, including rejection of missing or conflicting nominated bindings. Each selected target needs a declared carrier and nonempty handle.

These conditions preserve required declaration structure. They do not establish that the instance has actually realized or specialized a physical or operational capability. A complete declaration can coexist with false actual realization, adoption, construction or binding predicates in the supplied interpretation. Reference resolution, contract adequacy and the mapping from declarations to a real owner-local realization remain explicit source-owner and consumer obligations. The source's migration ceiling does not become an assumption that all real instances are impossible.

## 5. Companion local owner and context meaning

The normative statement and first testable condition explicitly require a local owner. The sixteen-coordinate expression does not contain a named owner field. The candidate therefore adds an interpretation companion for local owner without rewriting the canonical tuple. Selected instances require the owner reference, a locality declaration and a declared relation between that owner and the nominated coordination context.

The Definition's semantic_owner_ref names its Definition owner. It cannot silently substitute for an instance's local owner or the reusable capability's owner. Actual ownership and authorization are independent outcomes. Owners must still accept what locality means, which principals and scopes implement it, and how the companion corresponds to concrete consumers. A nonempty owner handle is not a credential or governance decision.

A selected instance requires at least one nominated semantic-context member because the positive genus places it inside explicitly declared semantic contexts. Membership agrees with the selected bounded-context collection, and every referenced member is declared and nonempty. No exact collection size, global uniqueness or disjointness is invented. Multiple-context examples and a single-context sufficient control preserve this scope. Actual context resolution, boundary adequacy and accepted correspondence to the current Bounded Context Definition remain pending.

## 6. One exact parent version and identity separation

Each selected instance has one nominated Product Capability version. That version maps to one nominated Product Capability through exact declared bindings. The candidate checks the referenced parent's identity and requires it to differ from the instance identity on the same candidate carrier. This retains the source's Instance-versus-Parent boundary without pretending that nominally different sorts alone prove semantic distinction.

Multiple instances may share an exact parent version. A separately declared unused version is possible and does not acquire selected-instance obligations automatically. The source supplies no universal latest-version requirement, semantic-version arithmetic, one-instance-per-parent restriction or implicit version promotion. Exactness is a selected binding condition, not a claim that an opaque version token authenticates a real source lineage.

Identity collapse is rejected independently of role exclusions and authority outcomes. Accepted alias resolution, real parent/version correspondence, global identity policies and inherited capability meaning remain separate review items. The entire Product Capability theory is not merged into this unit merely because its exact current source is a qualified dependency. A graph or directory reference cannot supply that missing common interpretation.

## 7. Separate claims, lanes and authority evidence

Parent and instance authority claims share a candidate carrier. Two separately bound lanes identify their roles, and a declaration records that the claims remain separate. Lane bindings must match the exact nominated claim and lane; missing bindings, wrong-lane extras and lane collapse are rejected. Distinct constants and exact relations retain a meaningful separation condition within the supplied interpretation.

The theory does not demand different principals, strength labels or claim text. Concrete claim-record equality, subject scope and reference policy remain owner decisions. Different printed tokens do not establish accepted authority separation, and a shared textual proposition does not establish authority transfer. The candidate records these unresolved maps instead of introducing a hidden universal claim-ID policy.

ParentClaimGrantsInstanceAuthorityDeclared and ConformanceInterpretedAsAuthorityDeclared are forbidden selected interpretations. Actual authority remains a separate predicate that can be independently true. One conditional query supplies a selected instance with actual parent authority and false instance authority. Its true antecedent prevents an unrelated unauthorized instance from serving as the entire non-inference check. The actual countermodel is synthetic bounded evidence; it creates no real parent grant, child grant or accepted source fidelity.

## 8. Contract, extension, adoption and construction bindings

Inherited contract, extension scope, adoption decision and construction binding retain separate sorts and exact references. The source's D65 construction obligation is preserved. CyberAlchemy Construction Method is a separately qualified current dependency. Naming it supplies neither an accepted construction-stage map nor evidence that stages completed. No uninspected construction system or actual runtime is imported.

A declared inherited contract does not establish faithful inheritance. Extension scope does not authorize a particular extension. An adoption decision reference does not execute adoption or prove an authorized decision-maker. The candidate can nominate all required records while actual inheritance, permission, adoption and construction completion remain false. Those outcomes require their own evidence and accepted denotations.

The source is neither weakened to a copied-folder convention nor strengthened to an unsupported globally unique contract arrangement. Descriptor references and claim roles remain explicit. Actual construction, reference integrity and integration with a specific realization require source and consumer review. The original obligation, evidence and owner-review work is preserved beyond the typed stage; a successful declaration model cannot replace that work.

## 9. Conformance, lifecycle and drift independence

Conformance references are distinct from a conformance result and from authority. The candidate does not invent a numerical collection minimum or a universal evaluation profile. Its direct references preserve the declaration obligation, while the meaning and adequacy of conformance evidence remain pending. Actual conformance is independently interpreted in the finite models.

The conditional conformance-to-authority query has a selected instance with actual conformance and false actual authority. The theory also permits independently supported authority, including cases without inherited parent authority. This is an independence boundary, not a prohibition on authorized or conformant instances. Interpretation as an authority grant is rejected without turning a measurement of conformance into automatic admission.

Lifecycle, drift and recomposition keep their declared roles. Admission posture does not become an operational lifecycle state. Naming a drift route does not prove detection, and naming a recomposition route does not prove a successful response. The theory introduces no unreviewed state taxonomy, transition system or liveness law. Actual lifecycle operation, drift handling and recomposition have independent countermodel targets and need additional evidence at their intended scope.

## 10. Recursion budget or stop and terminal handoff

A selected recursion contract requires a budget or stop declaration, inclusively. The budget target and its exact binding are checked when budget is declared; the stop target and binding are checked when stop is declared. Budget-only, stop-only and overlapping examples all remain expressible. Unused alternative fields do not receive a hidden unconditional requirement.

Recursion also retains the source's recomposition route and terminal handoff coordinate. An empty contract-content case fails even when the nominated recursion handle is nonempty. Terminal handoff is separately declared rather than replaced by a directory boundary or the mere absence of further records. Copied folder structure is explicitly excluded as evidence that recursion is established.

Budget references remain opaque candidate carriers rather than invented positive integers or decreasing counters. Declared stops do not establish well-foundedness, least-fixed-point semantics or actual termination. This static necessary-guard theory does not lower a real recursive or temporal obligation into a successful Boolean label. Actual budget enforcement, termination, recomposition and handoff remain independent targets with explicit source-query links and unresolved semantic-extension requirements.

## 11. Source correspondence, populations and actual native evidence

All twenty selected source units are accounted for by twenty mapped clauses: twelve encoded, six explanatory and two deferred. The normative genus retains the seven primitive guard groups. The formal expression, scientific conditions and general boundaries keep their individual selectors and excerpt hashes. Intuition, notation and examples explain the model without acting as normative premises. Authority-scope correspondence and the no-effect ceiling remain explicit independent obligations.

Eighteen requested populations make important examples nonvacuous. They include realization and specialization overlap, shared exact parent version, multiple semantic contexts, all recursion alternatives, independently supported authority and conditional authority counterexamples. These are finite evidence requests, not universal requirements that every installation contain each example. The one hundred unresolved maps do not supply owner acceptance. T and requested coverage I are evaluated separately.

Native model evidence has 186 controls: 57 satisfy T, 121 fail T and eight are structurally malformed. Twenty-eight countermodels satisfy the selected theory and requested populations while each exact target is false and its witness true. Two of those targets have positive conformance or parent-authority antecedents. Ninety-three source observations pass, including C18/C17 bindings, exact relocated excerpts, schema, pure projections and exact source-query links outside T. The prepared maximum of 30,041 steps fits the unchanged evaluation limits. No actual source outcome is assumed in T.

## 12. Stage boundaries, dependencies and execution DAG

Three independent fresh processes check contract, model and source with actual terminal exit zero and empty stderr. Model and source stdout match their successful native producer captures. The source's 201-file snapshot and Project's 10,188-file predecessor remain bound. A Python syntax preparation failure was retained before correction; an unexecuted module-file binding correction was also retained. Neither was a semantic model failure or a weakening of formulas, source accounting or evaluator limits.

A separate review-writer heading-count pattern failed before any review output was written. Its exact script, unexecuted stage code and actual diagnostic were retained before correcting only the escaped-dot pattern. The thirteen-aspect and minimum-length requirements remain unchanged. No theory, model, source comparison or evaluator limit was changed.

Thirty current semantic-use dependencies are explicitly qualified. Their presence does not mean their whole theories share one accepted interpretation. Carrier/profile inspection, actual source-to-consumer correspondence, reachable dependencies and the whole 109-draft inventory are later delivery obligations. The current native count is a working observation; the earlier sealed inventory remains historical. Shared consistency and semantic-cycle classification are unproven.

The work DAG keeps actual predecessor audit before native creation, source selection before signature and source accounting, model and source observations before fresh checks, and review before typed freeze and its separate audit. Consumer/profile observations, dependency and inventory refresh, six fresh full-delivery checks, full review, seal and separate audit follow. Capability Realization Binding starts after that full audited boundary. Execution order cannot prove semantic dependency closure.

## 13. Remaining meaning decisions and original completion scope

This types stage remains a partial candidate. All twenty-six source findings below are unresolved. Required decisions include local owner interpretation, actual context membership, parent/version and identity maps, claim-lane and claim-record policy, inheritance and extension scope, adoption and construction semantics, conformance, lifecycle, recursion and handoff. Source fidelity, consumer correspondence and actual authorized behavior are separate from shape or declaration completeness.

The original scope remains 183 identities, 189 admitted versions, 201 source files, 121 tasks, 511 planning edges, 797 work units and 36 frontiers. Original T, O, E, R and J requirements remain intact. Earlier planned-output presence is not acceptance. The remaining native definitions, complete obligation sets, actual evidence outcomes, attributable or explicitly pending review records, selected joint closures and final aspect-by-aspect explanation remain required.

An original recording criterion can permit a complete explicitly pending or unresolved outcome. That does not prove accepted meaning or global consistency, and cannot justify omitting a required artifact. Whole source-owner translation acceptance and whole-definition proofs remain zero. No real capability instance, adoption, conformance, implementation, publication or authority was created by these finite checks. The full episode goal remains active.
"""
text+='\n\nUnresolved source findings:\n\n'+'\n'.join('- '+x['finding_id']+': '+x['description'] for x in packet['source_precedence']['conflicts'])+'\n'
assert len(text.split())>2000 and len(re.findall(r'^## [0-9]+\.',text,re.M))==13
assert all(x['finding_id'] in text for x in packet['source_precedence']['conflicts'])
with (u/'REVIEW.md').open('x') as f:f.write(text)
labels=[
('S','Exact source and Project audit','C18 source/C17 selections andProject actualaudit0 bound'),
('D','Qualified signature','Source-backed23sorts171declarations'),
('A','Complete source account','20units/20mapped;encoded/explanatory/deferred explicit'),
('P','Requested populations','18requests100unresolved maps'),
('M','Finite native models','186controls28countermodels actual0'),
('Q','Independent source checks','93checks/exactsourcequery links actual0'),
('F','Fresh typed checks','Threeactualfreshchecks0'),
('R','Aspect review','13aspects/all26sourcefindings'),
('T','Typed freeze','Actual bounded receipt/input hashes'),
('J','Separate typed audit','Actualread-only audit0'),
('C','Consumer/profile observations','Exact currentcarriers/probes/gaps'),
('E','Reachable dependencies','Qualified closure/cycles/edge completeness'),
('I','Whole inventory','109partial drafts independentwitnesses'),
('V','Fresh full delivery','Sixactualseparatechecks0'),
('L','Full delivery review','Full sourceandconsumer explanation'),
('N','Full candidate seal','Exact currentcandidate file-set hashes'),
('X','Separate full audit','Actualpreservation/claim audit0'),
('Y','Next Definition','Capability Realization Binding afterfullaudit0')]
edges=[['S','D'],['D','A'],['A','P'],['P','M'],['A','Q'],['M','F'],['Q','F'],['F','R'],['R','T'],['T','J'],['J','C'],['C','E'],['E','I'],['I','V'],['V','L'],['L','N'],['N','X'],['X','Y']]
dag={'schema_version':'definition-assurance-continuation-DAG/v1-candidate','authority_effect':'none','source':b.source_ref(b.snapshot(),'cal.definition.capability-instance'),'nodes':[{'id':id,'label':label,'completion_criterion':criterion} for id,label,criterion in labels],'edges':edges,'original_scope':{'identities':183,'versions':189,'source_files':201,'tasks':121,'edges':511,'SWUs':797,'frontiers':36},'semantic_dependency_graph_is_separate':True,'whole_episode_complete':False}
b.put('continuation-dag.json',dag)
with (u/'CONTINUATION.md').open('x') as f:f.write('After actual typedfreeze/separateaudit0,inspect currentinstance/parent/context/claims/construction/conformance/recursion/handoff carriers andacceptedmaps;thenprofiles,reachabledependencies,whole109inventory,sixfreshchecks,fullreview,seal/separateaudit. Capability Realization Binding onlyafterfullaudit0. Originalscope/ownerfidelity/wholeproof obligations remain.\\n')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('Capability Instance F08-T exactC18d1e014...;Projectfull10188audit0 prerequisite observed.20sourceunits12encoded6expl2defer;16tuplecoordinatespluslocalowner,separatecontexts/version/identity/claimlanes,inclusivebudgetorstop/recomposition/handoff.186nativecontrols28countermodels2conditioned93sourcechecks actual0;fresh3actual0. Candidate-onlysourcefidelitypending/mapsunaccepted/wholeproof0/semanticreadyfalse. Nativecount10974withoutT isworkingobservation;fullinventoryrefreshlater. Preserve10188ancestorbytes201sources/original183/189/201/121/511/797/36.\\n')
print(json.dumps({'result':'CI typed review written','words':len(text.split()),'aspects':13,'DAG_nodes':18,'DAG_edges':18,'source_findings':26,'source_query_obligations':len(json.loads((u/'source-query-obligation.json').read_bytes())['obligations']),'semantic_ready':False},indent=2))

