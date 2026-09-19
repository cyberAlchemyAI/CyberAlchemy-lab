# Verified Patch Candidates — checked, successor required

Exact request -> bounded proposal -> exact action approval -> independent verification -> candidate or explicit failure.

The business model contains ten concepts and six relationships. Capability, profile and output contract identities close. All 22 offline fixture tests pass on the current coding-agent implementation, including approval gating, independently verified changes, malformed output, model transport failure, base drift and injected session lifecycle behavior. These tests do not invoke a live model canary.

Import remains pending. Four source-registry entries representing three distinct pinned versions remain unresolved: definitions (in both registries), L2 wrapper exports and L2 repository profile. Eleven implementation, dependency or compiled-system bindings in the frozen candidate differ from current files. The referenced L2 product-test and validation receipts were not found at their expected locations; the product-test receipt was also absent from the checked local filename search.

The provided runtime validators write candidates and receipts and invoke a live gateway canary. They were inspected but not executed against the source. Offline evidence does not validate the profile's historical live-canary claim. Existing conformance remains `not_evaluable`.

`repair-plan.json` records exact drift and missing receipts. `evidence-recovery.json` separates recovered versions from unresolved entries. `test-run.json`, `tested-inputs.json` and `offline-tests.tap` bind the current offline test evidence. Seven preparation checks pass, without marking the full runtime package or context import complete.

Next: create an isolated successor scoped to the tested fixture behavior, retain unverified live claims as unresolved evidence, rebuild generated models and validate before importing. Original source files and prior imports remain unchanged.
