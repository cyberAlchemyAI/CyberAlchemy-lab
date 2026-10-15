# Define Client API

`createDefineClient` is the transport-neutral L1 consumer boundary for durable
Define work. It exposes only `startWork`, `resumeWork`, `listStages`,
`nextQuestion`, `submitResponse`, `inspectReadiness`, `confirmArtifact`, and
`exportArtifact`.

CLI and chat wrappers bind an interface identity while sharing the same durable
runtime and immutable ontology-stage port. Consumers cannot obtain the raw
Module Port or adapter from the client. Mutations retain expected revisions,
command idempotency, actor access context, and minimized runtime audit records.

Artifact confirmation accepts the exact canonical candidate bytes returned by
`inspectReadiness`; export requires those same bytes and a matching durable
confirmation. All results are closed, digest-bound candidate evidence with
`authority_effect: none`.

## Open Questions

Definition Pack migration remains core-owned until its built-in stage shape is
selected. Product and Business ontology behavior belongs to later adapters.

