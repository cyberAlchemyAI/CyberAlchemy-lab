# Dependency Relevance context import

Work request -> close explicitly selected dependencies -> verify their exact input bytes -> report stale inputs while ignoring unrelated drift.

Imported 16 business concepts, 14 positional source relationships and six generated system concepts using existing migration header contracts. The existing capability Product and owner are preserved. The source package calls this the Governance Dependency Kernel.

The original repository request returned BLOCK for four changed inputs: D65, the development profile, project and generated system ontology. An explicit successor request selects those current bytes as candidate inputs. The business ontology's D65 evidence fingerprint is updated to the current selected definition, and the request binds the resulting business ontology bytes. Construction and conformance evidence are updated to match. The original package is archived separately; `successor-changes.json` records the changes. This is current candidate evidence, not a claim that historical definition or artifact versions are semantically equivalent.

All program admission fingerprints, the owner-selection record, Rust runtime, DomainSpec authored source and generated files remain unchanged. The repaired request returns CANDIDATE with 26 closed dependencies and no problems; it does not return admitted PASS. Removing the new D65 candidate selection or requesting admitted use produces BLOCK. Enforcement without an activation record returns NOT_EVALUABLE.

Thirteen Rust fixture tests pass. Two builds produce identical bytes and reproduce all seven existing generated files; the restored package does so again. Fifteen import checks cover source selections, construction fingerprints, graph identity, policy boundaries, candidate selection and admission refusal. There is no standalone source package validator; the migration validator checks exact source selections and construction coherence, alongside the package's own builder and Rust evaluator. These checks do not establish operational conformance or actual owner approval.

Store: `.local/ontology-context-import-0059/`. Verify with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0059-dependency-relevance-context-import/verify.py`. `snapshot_and_test.py` and `repair.py` record preparation from the repository root; normal restoration uses the frozen archive through `import.py`.

## Open questions

Capability adoption, ontology admission, accepted runtime baseline and enforcement activation remain ungranted. Other contexts included as archived dependencies retain their own evidence; they are not revalidated by this import. The enlarged ontology schema used by 0048 remains unadmitted.

Next: D65 Construction Validation — check evidence for the required construction stages and report missing or inconsistent prerequisites.
