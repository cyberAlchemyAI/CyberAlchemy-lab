# CyberAlchemy Exchange — product intake

Status: candidate intent, awaiting scope answers. Authority effect: none.
Machine record: [intake.json](intake.json). This is intake evidence, not a completed
Definition Pack or an implementation plan.

The user explicitly named **CyberAlchemy Exchange** and requested that the working
inference prototype become a standalone product.

Proposed meaning, awaiting confirmation: CyberAlchemy Exchange lets operators
connect inference engines and lets applications discover and invoke them through
one consistent API. The operator configures access; the caller requests inference;
the engine runs the model. Tenants retain their existing authorization/isolation
meaning where protected hosting is selected.

Exchange would own its product behavior, configuration experience, application
API and distribution. Alch remains its service-authoring language; DomainSpec
validates/compiles its contracts; Auth Foundation supplies identity/authorization
capabilities where required. Standalone operation is proposed to mean that users
can install and run Exchange without the sibling compiler development checkouts.
These product boundaries are proposals for the owner's decision.

The prototype supplies evidence: 228 local regression tests, real Qwen JSON/SSE
checks, and latency measurements. Exact source paths/hashes are recorded in the
machine record. That evidence supports reuse decisions; it does not demonstrate
that a standalone Exchange distribution already exists.

## Open Questions

1. Does Exchange v1 serve operator-managed engines, or connect independent providers
   and consumers as a marketplace? This decides the product's scope and actors.
2. Must the first release have its own repository and installable distribution,
   or can repository separation follow the installable release?

Both questions are pending with the user/product owner. Silence is not acceptance.
After these answers, confirm any remaining first-release hosting/UI distinctions
and present the candidate Definition Pack. Plan and Implement are subsequent
objectives. Existing runtime files, manifests and prototype evidence are preserved.
