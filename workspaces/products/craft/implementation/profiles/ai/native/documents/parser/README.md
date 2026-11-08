# Bounded native document parser

`index.mjs` exports `createDocumentParser`, `chunkParsedDocument`,
`parserArtifactIdentity`, `PARSER_IDENTITY` and `DEFAULT_LIMITS`.
ABI: `craft.document-parser/v1`; parser `craft-document-parser/1.0.0`;
chunker `craft-page-chunker/1.0.0`. This is the new parser portion of
`craft.document-processing`; the existing transaction/source owners retain
persistence, access, activation, retention and deletion. No second store exists.

```js
const parser = createDocumentParser({nodePath: trustedPinnedNodeExecutable});
const result = await parser.parse({
  bytes: pdfBytes,
  mediaType: 'application/pdf', // also text/plain and text/markdown
  source: {tenant: 'tenant-a', sourceId: 'invoice-123', version: 'immutable-v1'}
});
if (result.status === 'parsed') {
  const chunks = chunkParsedDocument(result, {maxChars: 2000});
}
```

The result binds the SHA-256 of the exact copied input bytes, parser/chunker
versions and supplied source identity. Pages are numbered from 1. Span and chunk
offsets use UTF-16 code units relative to the extracted page text; PDF spans also
retain the library's transform/width/height. Page concatenation uses `\n\f\n`.
Text/Markdown is literal UTF-8, without markup execution or normalization.
Overlarge bytes reject before hashing/copying and have `sourceSha256: null`.
Typed `review`/`quarantine` results have no partial extracted pages. Invalid
programmatic source/configuration arguments throw before dispatch.

## Setup and exact dependency

Supported host: Linux x86-64 with working unprivileged user/mount/PID/network
namespaces, bubblewrap, prlimit and Node **26.12.1**. The current host runs
bubblewrap 0.11.1. Default Node is `process.execPath`; callers must use that
qualified runtime or explicitly provide its executable. No account or credential
is required. From this directory run the pinned runtime's npm CLI with
`npm ci --ignore-scripts --omit=optional` and use the same Node for tests.
The isolated worker resolves the pinned dependency from this package or its
containing installed package; parent modules, source files and credentials are
never mounted into the parser sandbox.

PDF.js is **pdfjs-dist 6.4.299**, Apache-2.0; `package-lock.json` pins all npm
resolutions/integrities including omitted optional platform packages. No optional
canvas/native package is installed or required for qualified text extraction.
Installed registry integrity:
`sha512-AVl138zALtfaAPvADulE0PZThbYzCBS79nL4pOSL/6Sm/4AH5A21BD9VHt97OlCuzJuCpmeZtAtkinisF4Vb1g==`.
`dependency-lock.json` is a shipped, byte-identical snapshot of that actual npm
lock; npm archives normally exclude the package-lock filename. The focused test
checks snapshot equality, and dependency updates must refresh both in one change.
`parserArtifactIdentity()` hashes actual entry/worker/isolation/shipped-lock/dependency
bytes and returns the runtime closure identity; it does not invent a package lock.

The current primary [Mozilla scripting advisory](https://github.com/mozilla/pdf.js/security/advisories/GHSA-hq66-cqwq-w95j)
names the 6.2.108 fix and disabling scripting. The [official API](https://mozilla.github.io/pdf.js/api/draft/api.js.html)
documents data-only loading and extraction controls. This module never creates
the viewer/scripting manager, passes scripting/eval false, disables XFA/Wasm/font
rendering/fetch/range/streaming, and starts Node with code generation disabled.
The consulted [advisory index](https://github.com/mozilla/pdf.js/security/advisories)
also includes the historical 2024 eval issue. The selected installed production
closure returned zero known npm audit vulnerabilities during this local run;
that result is not a guarantee about undisclosed flaws.

## Enforced boundary and finite limits

Every parse executes in a fresh bubblewrap process with separate user, mount,
PID, IPC, UTS, cgroup and network namespaces. Only the Node executable, its seven
dynamic libraries/loader, the worker and PDF.js directory are mounted read-only.
The root, private device mount and private proc mount are read-only. Environment
variables and Linux capabilities are cleared. No host home/project tree, sockets,
credentials or arbitrary programs are visible. A classic BPF seccomp filter
rejects new sockets/connections, process forks, non-thread clone, clone3 (ENOSYS
to permit checked thread-clone fallback), namespace/mount changes, ptrace, BPF,
io_uring, perf and related kernel control calls. Existing bounded stdio Unix
socketpair I/O remains available. No worker-thread-only sandbox claim is made.

Before parsing, a real worker probe verifies host reads and writes fail,
network creation fails with EPERM/EACCES, process creation and eval fail,
PID 1/capability state is isolated, and Seccomp=2/NoNewPrivs=1 and hard limits
are installed. Unsupported/unavailable isolation fails closed without fallback.
The parent kills the process group at the wall deadline; bubblewrap also kills
the sandbox when its parent dies. Fork denial prevents orphan process escape.

Default ceilings (configuration may tighten, never raise): 8 MiB input,
100 pages, 10 seconds per isolated invocation, 1 GiB virtual address space,
128 MiB V8 heap, 4 MiB serialized output, 500000 extracted text code units and
20000 spans. Kernel CPU time is rounded up from the invocation deadline;
file/core output limits are zero, open descriptors 64. An initial cached
isolation probe is a separate invocation with the default ceiling. At most two
parse requests execute concurrently in this module; excess requests return
`review/PARSER_BUSY`. The kernel address-space cap also bounds native/ArrayBuffer
allocations. Parent capture enforces total output and a separate finite stderr cap.

## Failure, lifecycle and compatibility

Text-bearing PDFs and UTF-8 text/Markdown are supported. Image-only/no-text and
encrypted PDFs enter review. Malformed bytes, invalid UTF-8, resource exhaustion,
protocol violation and hard-limit overflow enter quarantine. OCR, rendering,
remote URL loading, password entry, external font/CMap retrieval and arbitrary
document formats are unsupported. There is no provider/format/OCR fallback,
delivery, paid effect, implicit retry or network synchronization. The source
owner may choose an explicit bounded same-input retry after resource review;
the parser cannot activate source/index state or repeat an external effect.
Final startxref/EOF bounds are required, and detected PDF.js xref repair enters
quarantine instead of silently promoting repaired extraction as valid input.

Source/version changes require reparse/rechunk/reindex under the source owner's
transactional activation. Chunk identities bind source hash/version, parser and
chunker versions, page and offsets; an old parser version cannot be passed to
this chunker as current. On any parser/chunker upgrade, run the actual old and
new versions over the same licensed/synthetic compatibility corpus, compare
text/pages/spans/chunk identities and explicitly invalidate dependent chunks,
vectors, snapshots and derived caches. No upgrade compatibility is claimed by
the initial v1 implementation. Old indexes remain source-owned until replacement
activation; retirement/deletion uses that owner's lifecycle. The parser stores
no source payload on disk and logs no document content.

Focused test command: pinned Node `--test parser.test.mjs`. Eight local tests
exercise genuine locally authored multi-page/scripted/encrypted/image PDFs,
literal text/Markdown, typed failures, every extraction cap, OS isolation,
actual memory/time exhaustion, output flood and exact dependency identity.
An additional existing authored 389648-byte repository PDF parsed as 16 pages
and 32382 extracted code units. These are local parser checks, separate from
provider/model quality or publication qualification; root owns the consolidated
objective result and registry updates.

## Open Questions

Broader font/layout extraction fidelity, OCR, other operating systems and
future parser-version migration require separate qualification. Current source
access/index integration and objective completion are owned by the
[reference application design](../../../../../../work/plans/ai-reference-applications/DESIGN.md#open-questions).
