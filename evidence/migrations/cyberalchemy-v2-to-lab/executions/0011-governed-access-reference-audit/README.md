# Governed System Building Access: reference audit completed

16 declared references -> 16 missing exact identities -> candidate import remains blocked.

The missing service-request reference is part of a broader mismatch: five input contracts, five output contracts and six policies use CA2-CAP identities that have no exact JSON identity declaration in the scanned source. 9 have local CAA concept descriptions with corresponding suffixes. Those descriptions are candidate meanings, not established aliases or executable request schemas.

The source support and residue files explicitly say KEP has no adopted generic service-exchange capability or admitted request/response extension. Existing encrypted co-ownership must not silently become service invocation. Even after candidate contract authoring, that operational prerequisite remains separate.

[results.json](results.json) lists every search, source binding and review lead. The scan checked non-ignored JSON files throughout the sibling repository and parsed each matching file for actual identity fields. No malformed matching JSON files were skipped. Source files and the current 24 imported candidates are unchanged; 21 declarations remain blocked.

The repair requires a candidate contract bundle with explicit identity mappings and concrete envelope, authorization, containment and receipt requirements. This audit does not fabricate those contracts or mark this Capability imported.

| Requested identity | Local concept with similar name |
|---|---|
| CA2-CAP-CONTRACT-KEP-SERVICE-REQUEST-ENVELOPE | CAA-CONTRACT-KEP-SERVICE-REQUEST-ENVELOPE |
| CA2-CAP-CONTRACT-AGENT-INSTANTIATION-REQUEST | CAA-CONTRACT-AGENT-INSTANTIATION-REQUEST |
| CA2-CAP-CONTRACT-CLI-ACCESS-ENTITLEMENT | None with matching suffix |
| CA2-CAP-CONTRACT-WORKSPACE-AUTHORIZATION | None with matching suffix |
| CA2-CAP-CONTRACT-TYPED-INTENT-PROJECT | CAA-CONTRACT-TYPED-INTENT-PROJECT |
| CA2-CAP-CONTRACT-KEP-SERVICE-RESPONSE-ENVELOPE | CAA-CONTRACT-KEP-SERVICE-RESPONSE-ENVELOPE |
| CA2-CAP-CONTRACT-KEP-SERVICE-FAILURE-ENVELOPE | CAA-CONTRACT-KEP-SERVICE-FAILURE-ENVELOPE |
| CA2-CAP-CONTRACT-GOVERNED-SYSTEM-ARTIFACT | None with matching suffix |
| CA2-CAP-CONTRACT-ONTOLOGY-READ-MODEL | None with matching suffix |
| CA2-CAP-CONTRACT-EVIDENCE-RECEIPT | None with matching suffix |
| CA2-CAP-POLICY-AGENT-REQUEST-NON-AUTHORITY | CAA-POLICY-AGENT-REQUEST-NON-AUTHORITY |
| CA2-CAP-POLICY-CREATE-ONLY-CONTAINED-TARGET | None with matching suffix |
| CA2-CAP-POLICY-CUSTOMER-ARTIFACT-CUSTODY | CAA-POLICY-CUSTOMER-ARTIFACT-CUSTODY |
| CA2-CAP-POLICY-VALIDATION-NON-AUTHORITY | CAA-POLICY-VALIDATION-NON-AUTHORITY |
| CA2-CAP-POLICY-ONTOLOGY-READ-ONLY | CAA-POLICY-ONTOLOGY-READ-ONLY |
| CA2-CAP-POLICY-EXTERNAL-EFFECT-NON-INHERITANCE | None with matching suffix |
