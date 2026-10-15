Nested raw content, typed bodies and full revision digests — candidate review

Previously the complete snapshot decoder preserved Artifact body and content fields,
but never proved that the body came from that content. Coherent typed payloads could
carry arbitrary byte lists and placeholder digests. The new complete entrypoint
rejects that situation: all nested documents must parse to their retained original
bodies and hash to their retained revision digests under the checked selected profile.

The required manifest is derived from the exact captured contexts. It contains every
metadata artifact in records and roots, every payload artifact in records and approval
roots, and every owned resolution/role entry in records and roots. It preserves order,
identical duplicates and unused records. No caller-supplied typed catalogs, ASTs or
expected artifact lists exist at runFull. The submitted manifest must equal the exact
ordered envelope list derived from these complete original catalog artifacts.

Every expected envelope contains the exact original content bytes, their actual
length, the selected profile's complete ref and the artifact's retained digest. The
full parent-plus-nested occurrence and original byte budgets are checked first. Then
the existing selected profile/original relation pipeline runs. After exact catalogs
are obtained, nested manifest equality and all nested scalar/digest/numeric preflights
precede nested typed decoding. Each original artifact occurrence is separately charged,
including identical record/root retries; catalog bytes and submitted nested byte
occurrences are both charged. Failed or missing nested data never yields success.

The document formats are preserved. Metadata content is the full original 14-field
RawRecord, including its five-field payload and companion refs, with exact body/kind
agreement. A generic payload's complete original body type alpha uses its supplied
proved Decoder. The worked body profile is String; this does not implement actual
Project, Intent, Goal or other real source-kind schemas. Actual approved kind-specific
payload decoders remain a separate provider/registry obligation. Owned resolution and
role content uses the existing complete five-field BindingRecord, with exact version,
revision key, kind, token/target/frame body and owner-review reference.

A primary or generic payload document need not contain a full revision key or review
reference. Those remain complete captured catalog bindings, with genuine provider
policies needed to validate their meaning. This component does not add a wrapper to
the primary source or falsely claim to read missing key/review fields from it. Owned
binding headers do contain those fields, so their values are checked against entries.

Twenty general theorems include item and ordered manifest exactness, budget/preflight
coverage, full_run_exact, exact retained original contexts, and the conditional full
original SourceInterpretation. The last theorem uses the exact existing 18-field
RemainingPolicies record; only parsing uses the already proved scalar byte meaning.
It preserves the original source meaning. It does not prove these remaining provider
premises, or allow convenient replacement predicates to discharge inherited IDs.
The complete map lists every missing policy realization in source-policy-realization-map.json.

The coherent worked case has 28 full captures, including 20 nested occurrences. Each
payload content is real JSON for the complete worked body, and owned-binding content
has exact headers/body. Changing raw references propagates into the source projection,
selection, World frame and profile evidence, so the positive fixture uses one actual
coherent frame. All nested full digests and bodies are audited. Controls reject missing,
deduplicated and reordered manifests, wrong nested profile, unused body mismatch,
owned review/key mismatch, numeric resource excess and malformed JSON. The prior
structural selected entry still succeeds on its original example, while the new
entry refuses its placeholder nested digests. Concrete string-to-UTF8 fixture terms
are checked against exact saved bytes; this is not a general serializer theorem.

One implementation cost remains explicit: the new wrapper rereads catalog bytes
already checked by the original entrypoint to retain exact catalogs in its output.
This is covered by the same exact parsing meanings and uniqueness proofs, but adds
work. It must be replaced by retained certified catalog ASTs before resources are
claimed for a mandatory consumer. Full operational time, memory, recursion depth
and decoder work are not measured. Compilation timing is not such a resource limit.

Fresh compilation and same-kernel replay verify the five new modules, all twenty
axiom inspections per phase, exact imports and 21 runtime cases per phase. The 133
unchanged dependencies are reused from their exact registered corresponding phase
outputs and source hashes, not freshly rebuilt. This is not independent checking.

Remaining work includes approved kind-specific payload schemas, actual source/root
providers, authentic complete World/selection/claims, every non-parser source policy,
mandatory consumer integration, all 41 relation adapters, all seven extensions and
whole-theory obligations, independent checking, measured limits and final actual use
assessment. Future provider and World raw captures must extend the shared manifest.
All 263 inherited obligations remain open; 90 original discharges retain scope. This
component does not accept N01 or finish the plan. K04/global reviews remain pending.
