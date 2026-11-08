# Embedded permissioned hybrid retrieval

R06 adds actual SQLite FTS5 indexing, exact native cosine ranking and reciprocal rank fusion to the original R05 document/generation authority. This is a native technical capability; similarity and fusion scores are not business confidence or a new AlchLang number type. The existing checked capability/request/context owners remain reused. The new delta is executing an owned index and current-source eligible retrieval.

`createRetrievalProfile({embedding:{model,dimensions,preprocessing,space},mode})` keeps representation identity separate from retrieval strategy (`hybrid-rrf60`), index algorithm (`exact-cosine`) and backend (`sqlite-fts5`, tokenizer `unicode61`). The default local reference requires 1536 dimensions. An explicitly labelled fixture profile may use a smaller dimension. Both enforce 100 documents, 2000 active chunks, top 10, 2000 code units per parser chunk and finite vector norms within 1e-12..1e6. These bounds do not promise latency or approximate-index recall.

`createEmbeddedRetrieval({path,documentPort,parser,embeddingPort,profile})` consumes the original document port (`craft.document-authority/v1`), the actual D01 parser/chunker and a selected embedding observation port with the exact representation identity. `parser` defaults to `createDocumentParser()`; supplied native adapters are trusted technical dependencies, never model-selected functions. No network client, business API, ACL mirror, model routing fallback or second spend ledger is created here.

The embedding port has `identity: {model,dimensions,preprocessing,space}` and `embed({observationId,text,source,representation}) -> {vector}`. The selected original model/exposure/source-release owners must govern any provider egress before implementing this method. An interrupted pending vector requires `inspect(sameRequest) -> {status:'confirmed',vector}` or `{status:'definitively-no-effect'}`. Missing/unknown inspection stops with `OutcomeUnknown`; an uncertain embedding is not blindly repeated. The deterministic observation identity preserves same-generation/chunk intent; paid accounting remains the model owner's responsibility.

`await index.build({generation,principal})` consumes an opaque original R05 generation handle. The generation must name the exact parser/chunker, representation and `RETRIEVAL_IDENTITY.indexVersion`. Build reads actual source bytes, invokes the actual parser and chunker, validates current source/version/ACL again after awaits, obtains dimension-checked vectors and persists each indexed chunk plus its observation reference. Checkpoints reuse confirmed vectors on restart. A complete durable index precedes original generation activation. A stale ACL, deletion, content replacement, incomplete chunk set or retired generation cannot activate or revive an old index.

`index.search({tenant,principal,query,vector,topK})` uses the currently active source generation and original document reads before ranking and immediately before content return. The lexical query is tokenized and bound as literal FTS terms. Search builds its FTS ranking corpus from authorized current chunks only; denied documents and other tenants cannot affect BM25 statistics or dense ranks. Full-precision cosine determines dense order, FTS5 BM25 determines lexical order, and fusion is `1/(60+lexicalRank)+1/(60+denseRank)` with absent ranks contributing zero. All ties use canonical UTF-8 document/version/chunk tuples. Results retain source/chunk digests, ACL revision, generation and page/offset provenance with the actual parsed text. An empty authorized corpus returns an empty result. Changed source generations fail closed until rebuilt.

These source checks establish a local authorized retrieval boundary, not a durable egress ticket. Any later model context, answer, cache, export or customer send must use the common R02 source-release owner and preserve every disclosed dependency, including uncited evidence.

`index.retire({tenant,generationId})` retires local index content without editing the authoritative source; `inspect({tenant})` reports generation statuses. `close()` releases SQLite. `retrievalArtifactIdentity()` hashes actual owned module/package bytes and declares dependency ABIs; the parent package/integrator supplies its exact complete artifact/export/dependency closure.

Run the focused checks with the selected Node 26.12.1 runtime:

```sh
.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node --test \
  implementation/craft-ai-profiles/native/retrieval/retrieval.test.mjs
```

Tests execute real text parsing and SQLite FTS5, a labelled synthetic three-topic retrieval corpus, independent cosine/fusion calculations, negative/zero/huge/nonfinite/near-tie vectors, stable top-k ties, current permissions, tenant filtering, revoke/replace/delete, interrupted embedding inspection, restart, retirement, dimensions, document/chunk limits and the 1536-dimensional local reference path. Embeddings are explicitly recorded/deterministic fixtures. These results do not qualify a provider/model or measure broad production retrieval quality.

## Open Questions

Approximate or remote search, larger resource profiles and performance promises remain outside this exact bounded selection. Provider embeddings must be composed through the existing M00/M01/R04/R02 owners and separately qualified. Encrypted stores/key custody and wider identity provisioning stay with their original owners. The parent application design owns later cross-app quality and package qualification; local hosting, publication, deployment, TDE and EVF remain deferred.
