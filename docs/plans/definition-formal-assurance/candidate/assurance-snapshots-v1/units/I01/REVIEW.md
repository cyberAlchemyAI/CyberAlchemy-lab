# I01: preserving assurance when definitions change

I01 adds exact captured input epochs, conservative change classification, transitive invalidation and a freshly checked cache path. Its purpose is to prevent a previous result from silently remaining applicable after its source, interpretation, assumptions, coupling, execution profile, tool or target statement changes. All 34 final validation tests passed in 205.098 seconds. The failed 31-test attempt is preserved with its original code and diagnostics. Actual outcomes are recorded in numbered attempts and the unit receipt. This review explains the implementation and its limits; it does not close the full formalization episode.

The epoch captures the chosen source snapshot, authored interpretation packets and explicit role bindings. Each captured artifact retains its exact path, SHA-256, declared JSON/opaque format, byte count and bytes. Source identities retain definition ID, version reference, path and hash. The compiler reconstructs the dependency graph through the existing C03 correspondence and graph checks. A self-reported graph, readiness tag or fingerprint cannot replace that reconstruction.

## Formalization aspects and change behavior

| Aspect | Representation in I01 | Consequence of change |
|---|---|---|
| Source identity | Exact definition/version/path plus separately bound source bytes | A version or source-location change is a conservative content change. Equal labels never rebind a source automatically. |
| Source content | Hash of the complete parsed JSON value, with exact source bytes retained separately | Any parsed structural change invalidates the node and its consumers. Formatting alone still requires new byte binding. This does not establish source fidelity or mathematical equivalence. |
| Interpretation | Authored source-accounting packet plus any additional selected interpretation artifacts | Changes invalidate dependent evidence. Missing or quarantined interpretations remain explicit rather than becoming zero-dependency complete definitions. |
| Assumptions | Explicit selected artifacts under the assumption role | Changes to premises or their selected context invalidate consumers. The invalidator does not itself prove that the assumption is true or correctly typed. |
| Coupling and carrier mapping | Explicit artifacts under the coupling role | A changed mapping or policy invalidates the affected interpretation and its dependants. Carrier equivalence and permissible inference still require their existing checks. |
| Profiles and tools | Explicit profile/tool artifacts, plus bound invalidation-engine source files | Selected execution changes invalidate affected nodes. Opaque code bytes are never normalized into an asserted equivalent program. An unavailable or changed invalidation engine prevents accepting a prior epoch under a different implementation. |
| Statements and populations | Explicit artifacts under the statement role; exact C03 graph inputs retained | New target formulas require new applicable evidence. Obligation regeneration and whole-theory population checks remain the next units' responsibilities. |
| Dependency uses | Exact validated authored edges compiled by C03 | Invalidation traverses the union of old and new reverse edges. Removing a use cannot remove the old consumer from the affected set. No word matching invents a semantic edge. |
| Cycles | Strongly connected components of the propagation graph | A changed member reaches its mutual peers and downstream consumers. This is change propagation, not a recursive denotation, least fixed point or consistency proof. |
| Global denominator | Current source identity/version/path set and selected node set | Addition, removal, version changes or selection changes require a new global denominator and regression. Local unaffected nodes cannot make the previous global theorem current. |
| Cached evidence | Externally selected epoch, published manifest and independent verifier selection | Unaffected status only permits a fresh check. Exact object/source/input bytes and regenerated obligations must still pass E03. Pending proof and owner gates remain pending. |

## Structural change and representation change

I01 distinguishes two fingerprints. The content fingerprint incorporates complete parsed JSON structure, source identity and scope, each selected role's artifact paths/formats/content hashes, declared outgoing dependencies and relevant cycle policy. It does not discard unknown mathematical conditions or attempt to decide whether two formulas are equivalent. The representation fingerprint binds source references and exact artifact references, including hashes of their actual bytes.

JSON key order and whitespace are serialization differences. If two explicitly declared JSON artifacts parse to the same exact value, their content fingerprints agree while their byte references differ. That produces a representation change. Boolean, integer and floating-point JSON values remain distinct: `true`, `1` and `1.0` cannot collapse through Python equality. Lists retain order. Opaque artifacts use raw-byte hashes for both content and representation treatment.

A representation change still invalidates the affected node and consumers. Existing evidence binds the previous bytes; I01 cannot silently rewrite those bindings and declare the evidence applicable to the new files. The distinction explains the cause and supports later revision workflows. It does not create a cache shortcut or authorize source edits. When an exact source hash is updated inside an authored packet, the packet's parsed structure also changes; that remains a conservative content change even if the source text's JSON formatting was the initial trigger.

## Why both graphs are necessary

Suppose C uses A, and A uses B. A change to B affects B, A and C. If a new version removes A's use of B, traversal of only the new graph would miss A and C. I01 instead preserves both graphs for propagation. The removed edge remains relevant to invalidating evidence based on the prior interpretation. Added edges likewise matter: the new consumer's interpretation changes, and its existing consumers must be rechecked.

The graph uses stable definition identities for propagation while retaining exact versions in the node/source fingerprints. Removed definitions remain in the prior affected set; current affected nodes are listed separately from prior-only nodes. Newly added definitions change the global denominator even when no authored edge connects them to existing definitions. I01 flags global regression rather than inventing an edge to make every old local node appear dependent.

The SCC report describes cycles in that union. A cycle in the union may span two different versions; it is a conservative propagation component. It is not necessarily a simultaneously asserted semantic cycle in the current theory. Actual cycle classifications and pending source correspondence are retained from C03 separately.

## Fresh cache checking

The cache API accepts externally selected old/current epoch references and an explicit list of candidate entries. Each entry names its exact covered definition IDs, a published manifest reference and the independent verifier selection reference. I01 first reconstructs both epochs and derives the invalidation plan. Invalidated entries are marked as such before invoking the verifier; their reported successes cannot override the changed-input boundary.

For an unaffected entry, I01 rehashes the selected manifest and selection, runs the existing independent E03 verifier against the live source root, checks that the theory's exact source denominator matches the covered current nodes, and requires selected role artifacts to be present in the published evidence bindings. E03 regenerates the required logical set and checks native model evidence when available. An envelope with only missing logical results can pass candidate accounting, but all missing logical and administrative/semantic gates remain pending.

I01 also collects and rehashes the verifier's declared input references and published objects at the closing boundary, then compares its active build and provider/runtime bindings. Runtime build records are checked against the active runtime rather than followed as fixture data paths. A changed epoch file, source capture, selected relation, nested input, role artifact or published object after verification clears the entire returned cache support. The output becomes explicitly unresolved with no retained supported entries. Currentness remains a checked boundary, not a promise that files will never change again.

## Trust, coverage and remaining work

Epoch validation reconstructs node fingerprints, graph projection and coverage from captured bytes and independently selected references. Rehashing a forged node or graph does not make it valid. The external epoch reference still matters: a digest identifies the selected bytes, not an accountable owner decision or authenticated real-world fact. The active invalidation/compiler/parser/correspondence source files are bound as engine inputs. Python, the filesystem, those existing components and the independent verifier remain part of the trust boundary.

Reads reject symlink components and non-regular epoch files. The selected-artifact count, captured-byte total and serialized-epoch size have explicit limits. Resource failure is a failed or unresolved execution outcome; it cannot become a negative logical result. I01 creates no files through its public analysis APIs and does not alter canonical sources, admissions, prior bundles or prior receipts.

The actual current baseline binds 183 source nodes and eight source-accounting packets: Hypothesis and the seven later governance pilot packets. It retains 175 nodes without a selected nonquarantined packet, eight pending correspondence/fidelity records, zero validated authored dependency edges and an independently unreviewed edge denominator. All 201 captured source/provenance files were rechecked. The baseline still has incomplete whole-definition translations and source fidelity. An epoch can bind every current source while preserving that incompleteness. An unchanged baseline shows that its selected inputs are unchanged; it does not show that all 183 definitions have been formalized or that a global theory has been proved consistent.

I02 must regenerate obligations for additions and revisions. I03 must compile and check the whole selected theory and required populations despite local cache candidates. The later CLI, revision rehearsal and L1 gate must make these boundaries visible. Wider family translations, global proofs, source-owner fidelity and the complete final episode review remain required. The seven partial governance interpretations and the exact pending owner-review packet retain their previous claim ceilings.
