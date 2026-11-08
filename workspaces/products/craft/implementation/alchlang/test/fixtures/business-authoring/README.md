# B10.1 independent business fixtures

Status: independently authored fixture inputs and expectations, authority effect none. No renderer result supplied these oracles. AlchLang's `test/fixtures/business-authoring/` is the canonical fixture owner; Core's `test/profile-engine/fixtures/business-authoring/` is an exact byte mirror, checked by the independent harness. Both directories intentionally contain only business sources, oracle/intent data and this README; there are no handwritten generated semantic/project/request companions.

`delivery-acknowledgement/business.alch` models a supplied delivery verification flag; the separate recipient confirmation flag cannot override it. `publication-consent/business.alch` checks a submitter's consent to release a notice without publishing anything. Both use an actual Boolean predicate, not identity reflexivity. Formal sort/predicate names differ from Entity/definition names and explicitly link them. Each source contains context, actor, examples, counterexamples and claim/boundary ceilings.

Each `oracle.json` contains independent whole-body values, exact decimal-string UInt64 boundaries (zero, above JavaScript's exact integer range, maximum and overflow), true/false guard expectations, verbatim extra String retention and invalid value types. Returned values preserve every declared field. Rejections name the authored continuation and contain no return value. Runtime settlement envelope and HTTP status conventions remain a later-owner concern. No oracle asserts native execution, accepted meaning, formal proof or live readiness.

`composition-intent.json` reuses six local declaration names across two distinct model/source identities and names distinct routes. It is a test descriptor, not a generated project companion. `profile-selection-intent.json` describes future tool-created local/shared/API-prefix selections; no successor archive, complete package or fabricated profile asset is supplied. `decision-intent.json` is explicitly synthetic intent, never an accepted record or handle. B04 remains unimplemented; B10.2/B10.4 must later use its real tested recorder with the exact current subject and definition closure.

`negative-mutations.json` assigns source, review/decision drift, exposure, collision, profile substitution, custody, destination and forgery controls to their owning later gate. Each case is unexecuted until that owner runs it. Source replacements are checked for unique anchors; mutation recipes preserve prose for selected definition/guard/audience drift cases. Malformed edits may reject in B02 before review. Broad `BUSINESS_` families are intentional where later APIs have not fixed a finer code. Cases naming request/output owner rejections must retain those real owner diagnostics when implemented.

Run the repository-local structural checker:

```sh
node research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan/harness/oracles/verify-fixtures.mjs --self-test
```

It checks captured fixture digests, exact Core mirror bytes, explicit source joins, scenario completeness, independent value outcomes, mutation anchors, distinct composition identity and honest pending state. It is independent of the B02 parser and generator. Root must separately join these exact sources to B02 parse/resolve after both workers finish. The manifest captures authored input/expectation bytes; refreshing a manifest does not bless renderer output as an oracle.

## Open Questions

- B04/B06.2: record and verify a genuine explicit matching synthetic test-owner decision; no authentication is established by the owner token.
- B07/B10.2: execute these values through the real checked Mapping/request chain; pin concrete settlement/type-error response checks without weakening the authored value/guard outcomes.
- B09.2/B10.4: qualify native behavior across local/shared/API-prefix profiles, actual shared module consumption and two-model composition using isolated installed successor packages.
- B10.2: execute the staged negative corpus and replace pending exact diagnostic names only with real owner evidence; do not mark this fixture inventory as rejection evidence.
