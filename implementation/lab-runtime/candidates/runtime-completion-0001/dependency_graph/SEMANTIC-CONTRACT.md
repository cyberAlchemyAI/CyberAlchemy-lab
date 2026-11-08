# Selected original semantic adapter

The supported public consumer is `verify_graph(reader, policy_file_id,
declared_edges, root_refs, anchor, policy_schema_raw=...)`. Its `RoleReader`
must come from the independently reviewed reader checkpoint0003. The caller
independently selects the complete `GraphAnchor`: full C01 policy, eligibility,
source and profile bindings, exact source cut and allowed lifecycle states.
The adapter compares those selections with the reader and the exact selected
member identities. A matching hash does not replace a binding's kind, root,
path or length. Fixture permission remains tied to the same selected reader,
provider and root domain. Actual protected custody remains gated.

The implementation ports the original `release-proof-inputs-v2-completion-0001`
semantic verifier. It preserves the original registry/catalog joins, native
identity function AST digest, original operation source digest, carrier and
embedded fragment selection, schema URI closure, descriptor role lists,
reference slots, relation endpoint pairs, typed qualifiers, current eligibility,
exact declared edge set, semantic acyclicity and reachability from selected roots.
Schema references describe execution dependencies. Proof declarations retain
their evidence role and never become semantic instances by having a path or hash.

The exact original semantic policy schema has SHA-256
`6c21294529c01bc86014aa400f230d718e9ddc69e45f1e937e00cbd44ae7db8e`.
Schemas resolve only in the selected `https://lab.invalid/` namespace and local
selected documents/fragments; no network retriever is installed. Recursive
schema reference coverage requires the original explicit bounded successor
policy and refuses rather than silently truncating. Every input body is bounded
by the reader's 64 MiB maximum; the original JSON parser adds a depth64 bound.
No source bytes are rewritten or normalized to obtain a source identity.
Original finite-number body semantics are distinct from signed-control i64 JSON.

`SEMANTIC-REFUSALS.md` records the finite code mapping for original rejection
meanings. The public boundary never renders arbitrary exceptions, body values,
schema excerpts, locator values or exception chains. Semantic failures are held
until the reader completes its post-read currentness checks; a failed reader
post-check supersedes a semantic result. Ordinary rendered traceback containment
does not claim isolation from hostile Python exception-object introspection.
`Schemas`, pointer helpers and `_verify_graph` are implementation internals, not
separate protected-consumer entry points.

The owned semantic tests port all30 original causal cases using copies of exact
selected public fixtures, plus full-binding, source-cut, schema-origin and
private diagnostic negatives. Their source selection is the immutable original
T08 revision0002 attempt0006 manifest. Only files explicitly listed there can be
copied, and every read input is checked again at completion. Fixture eligibility
and permission are technical test inputs and cannot select actual host trust.

The full inventory integration separately compares all22 selected original
metadata tables and241598 ordered occurrences through `RoleReader.inventory`
against the accepted public projection. It retains all17 historical tables and
172533 occurrences, complete row fields, repeated identities and exact original
selectors. Every occurrence's role is checked against the selected public role
policy; all23486 protected dependency rows remain metadata only. The complete
metadata fixture cut is explicitly synthetic and grants no actual source-cut
status. The projection's empty semantic instance set means no protected body
selection was supplied; it is not proof that the actual Artifact graph is empty.

The checkpoint is a technical T08 adapter dependency for later T09 construction.
It does not accept original T08/T09, establish actual current protected records,
run the original engine, install an environment, publish a package or grant any
effect authority. Whole-unit acceptance still requires CompositeEnvironment and
dynamic-origin adapters, final selected dispatch and independent review.
