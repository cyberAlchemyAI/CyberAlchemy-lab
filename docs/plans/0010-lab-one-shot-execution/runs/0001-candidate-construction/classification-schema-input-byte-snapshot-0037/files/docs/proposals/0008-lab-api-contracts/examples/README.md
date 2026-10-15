# Illustrative API messages

For each of 34 operations, request.json is the wire call, message.json is its separately serialized domain payload, response.json is a typed result reply and error-response.json is an application error reply. Wire and inner-message digests are computed from their respective example bytes and must not be substituted for each other.

Identity, scope, authorization, source-cut and handler bindings are placeholders. The trusted-context example is a shape example, not authenticated context. Returning a shape-valid result does not prove that a handler ran; candidate/blocked/denied dispositions are preferred where the source schema permits them.

The example fingerprint encoder handles only ASCII object keys and small exact integers. It is not a general RFC 8785 implementation or codec conformance evidence. Original artifact bytes are never normalized for these fingerprints.

[index.json](index.json) links all examples and exact illustrative wire/message hashes. See [workflow descriptions](../WORKFLOWS.md) for coherent proposed sequences.
