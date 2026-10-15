# Invocation-owned qualification APIs

`QualificationContext(run_root, resource_policy)` owns the source catalog, compiler callback, policy, unique run allocation and in-memory replay events. Each fresh run writes beneath a new directory. The context checks prerequisite receipts and pinned compiler identity before stages. Pure modules use private import names. Legacy normalization and saved inspection each run in a dedicated interpreter.

`qualify_fresh(request, context)` validates the exact versioned request, normalizes the selected source proposal, checks the actual projection, evaluates the finite positive closure, compiles the actual witness layout and performs fresh replay of the exact general theorem bundle. A qualified result contains all 20 rule-only obligations. The same pipeline is consumed by the Python API, CLI and `qualify_for_shadow`; P08 supplies the publication protocol.

`inspect_saved(request, result, context)` verifies recorded currentness and exact witness correlation. It creates no fresh replay event and grants no application authority. Current bytes do not establish a fresh invocation.

The two witness layouts have identical declaration bodies. Combined mode emits one actual witness module. Staged mode links data, typed certificate, closure and model expansion modules in that order. Cached dependencies require exact source and compiled bytes; actual proposal witnesses and general replay are fresh in either mode.

At P03 the memory policy is advisory. Required memory enforcement returns `unsupported-policy` until the P06 supervisor is used. Stage timeouts return `unknown-resource`, with no complete closure, absence or application claim. Whole-run enforcement, cancellation and aggregate descendant memory are P06 obligations.

The first CLI integration probe reached the existing 60-second general replay limit. Its failure record is retained in `observed-timeout.json`; it is not counted as a successful qualification or a replay event. The same policy is used for subsequent validation.

No same-kernel replay is called independent verification, no supplied truth is authenticated by hash comparison, and no saved inspection authorizes application.
