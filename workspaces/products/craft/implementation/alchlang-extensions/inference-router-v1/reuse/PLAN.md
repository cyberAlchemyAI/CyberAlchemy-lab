# ISB-08 generated service migration and reuse

Completed owner-directed local candidate. Authority effect: none. This bounded witness
reuses [ISB-02 Define-backed meanings](../service-contracts-v1/README.md) and
[D65 business/product scaffolds](../service-contracts-v1/scaffolds.json).
No new canonical meanings or compiler profile are introduced.

## Construction chain

1. Reuse the service, mapping, operation, error and runtime dependency meanings.
2. Author a minimal parcel quote fixture with inline meanings: quantities one
   through five cost 1000 cents; six through ten cost 2000 cents, in USD.
3. Bind generated request/receipt schemas to CalculateQuote; compile the pricing
   module, health route, POST route and error policy through the existing compiler.
4. Invoke the generated service through the same Node host adapter. Prove HTTP,
   invalid input/output, cancellation, artifact integrity and authored price changes.
5. Move the remaining inference strategy/model admission decisions into an
   authored pure module. Keep operator provisioning and estimates behind bindings.
6. Inventory every physical line of the active hand-authored service/runtime
   sources, run preceding regressions, and record paired Craft evidence.

## Boundaries

The quote fixture proves reusable Node route/function/operation generation. It
does not independently prove every outbound/stream/custody combination; those
contracts retain their focused conformance suites and inference integration
witnesses. No Rust service parity or production-readiness claim is made.

## Open Questions

Owned by [README](README.md#open-questions). Tenant identity and authorization
remain the final unit; no security implementation is included here.
