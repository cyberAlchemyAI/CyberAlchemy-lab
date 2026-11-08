# Local pattern validation

Status: validated local candidate. Authority effect: none. Product approval and
activation are not granted. Open questions: [README.md](README.md#open-questions).

The reviewed pattern was implemented through existing Alch/DomainSpec builders.
The Define scripted result contains three candidate meanings and passes structural
validation; this is not canonical definition promotion.

205 tests passed: 13 local pattern, 121 service regression, 38 authentication,
30 custody/TLS, and three compatibility tests. The native responsibility inventory
was rechecked after the launcher compiler-path update. Full Alch TypeScript build
and exact DomainSpec runtime/contract compilation passed. The paired Language
Craft surface validates.

The standalone bundle was relocated in tests. A separately materialized bundle
was launched through start.mjs from outside the checkout on an ephemeral loopback
port; health, generated inference, absence of upstream authentication and clean
SIGTERM shutdown passed. All test listeners were closed.

Coverage includes generated discovery/selection/mapping, explicit aliases,
configuration ranking, replay/conflict, named SSE completion and early EOF,
provider JSON/redirect failures without fallback, a 5.1-second successful response,
tightened cancellation deadlines, closed configuration/context exclusion,
Host/Origin/forwarding boundaries, legacy bearer behavior and v1/v2 limit checks.
Existing suites retain overload, bytes, cancellation, authorization and storage
negative witnesses; an independent authored quote change proves generic reuse.

An initial bundle-builder callback error and a Fetch-based Host-negative witness
were corrected before the successful run. Host rejection is now tested using raw
HTTP because Fetch normalized that header. An initial TypeScript build encountered
unrelated module-configuration errors; those concurrent changes were preserved,
and the subsequent full build was clean. Earlier failed runs are not passing evidence.

The generated reference is at ../generated/local-pattern. Its manifest binds all
865 emitted files. RESULT.json binds that manifest and this source snapshot.
The fixture engines emit deterministic text, not actual model inference. No
third-party protocol compatibility, hardware performance, deployment, Rust
service parity or model-completion recovery is claimed.

LP-01..05 are complete for the reference pattern. LP-06 is exact candidate review.
Optional engine selection, tokenizer bounds, private-network topology and codec
extensions remain operator/product questions. Protected and durable compositions
remain available in their existing packages; the standalone reference uses
public loopback scope and memory custody.
