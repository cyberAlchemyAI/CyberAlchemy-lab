# Craft views through Ontology Lifecycle

The existing shared v4 source consumer imports the exact Craft input manifest into a fresh temporary store, replays its events and exports source-bound records. The Craft adapter reads that export to derive eight named outputs. Temporary stores are removed after each request; existing ontology stores are unchanged.

```sh
node craft/implementation/run.mjs views product
node craft/implementation/run.mjs views project-work
node craft/implementation/run.mjs views business
node craft/implementation/run.mjs views system
node craft/implementation/run.mjs views bridge
```

Other outputs are `authority`, `identity` and `verification-requirements`; omitting the name returns all eight. Nine declared input views supply them. Product includes 37 capability candidates; Work includes 114 source task definitions. Business and system branches remain distinct; the bridge reader preserves package-qualified identities and endpoint closure.

The adapter checks exact source bytes, native record digests/selectors/identities, document bindings and both local/shared semantic source pins. Missing, duplicate, forged or stale exports fail. Acceptance requirements remain separate from observed results: the verification-requirements reader does not load the selected test reports.

- [Native source manifest](source-manifest.json)
- [Application binding](binding.json)
- [Reader implementation](derive.mjs)
- [Reader checks](derive.test.mjs)
- [Source reconciliation](../sources/reconciliation.json)

Review external lineage and explicitly refresh local representation pins after an intentional source edit:

```sh
python3 craft/ontology/application/reconcile.py --write --refresh-manifest
```

This updates representation pins and the current reconciliation record. Original source-registry expected hashes remain intact. Running `views` never silently refreshes a stale pin.

## Open questions

Current source selections follow the approved claim review. The namespace errors and stale source bindings are corrected; historical evidence and old generated-projection dependencies are removed. Body War remains a source-present reference application with runtime qualification separate. Future source changes fail rather than inheriting the current result. Product adoption, the authored technical construction chain, broader application tests and runtime commissioning remain outside reader qualification.
