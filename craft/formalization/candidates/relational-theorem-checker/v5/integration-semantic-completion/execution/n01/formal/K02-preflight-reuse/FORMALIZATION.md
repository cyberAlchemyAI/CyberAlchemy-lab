Certified preflight reuse before implementation

The retained guarded entrypoint parses and hashes each original capture during
preflight, then repeats those operations during typed profile/authority preparation.
The reusable implementation must retain the exact same prepared-data meaning and
refusals; it must not weaken source or authenticity requirements to avoid work.

Define a data Input and a CertifiedInput subtype indexed by exact digest Profile, per-capture budget and
NumericLimits. It retains the complete original Envelope and scalar AST plus proof
of EnvelopeMeaning, VerifiedDigestMeaning, ScalarByteDocumentMeaning and
NumericTreeMeaning. A raw Input alone is insufficient for the cached typed adapter: only the
CertifiedInput subtype carrying this independently specified proof is accepted.
No public caller Boolean supplies this certificate. Lean proof
fields are erased in runtime code, but constructing the certificate requires proof
of its exact independently specified constraints.

Certified preflight performs the same envelope/digest/scalar/numeric checks as the
registered preflight, preserving its refusal reason. Prove diagnostic equivalence
and exact original capture retention. A successful certificate's AST is the unique
scalar document for those original bytes; replacing it by a different AST cannot
satisfy the required parser meaning.

Typed preparation uses the retained AST with the existing complete binding-record
AST decoder and frame guard. It does not call a byte parser or digest evaluator.
Prove equivalence to DigestPreparedMeaning and equality to the legacy byte preparer
under the certificate. Ordered list preparation retains every input occurrence,
including duplicates, and is equivalent to legacy ordered digest preparation.

Then prepare the selected profile and authority data from these certified inputs,
using the original profile selection, authority header/coherence and evidence-join
checks. Prove equivalence to the previously defined stage meanings and exact final
bounded outcome. Combined budgets still precede preflight; every original capture
still passes numeric checks before typed decoding. Authenticity, schema/review,
full-source policies, consumers, operational measurements and independent checking
remain required separately.

Controls must compare actual retained original fixtures and refusals, including
huge exponents only through guarded paths. Keep the registered packages immutable.
New modules require fresh pinned compilation/replay, per-theorem axiom inspection
and exact import audits. Unchanged dependency outputs may be reused only with exact
source/output bindings to their verified compile/replay phases; disclose that reuse
and do not call it a fresh dependency rebuild or independent checking.

The full 41-kind/550-pair/seven-extension/263-obligation plan remains active. K04
and global policies remain pending; no inherited discharge or actual provider is
inferred. The consumer inventory currently finds only candidate APIs/proofs/tests,
so this package cannot claim a live application cutover.
