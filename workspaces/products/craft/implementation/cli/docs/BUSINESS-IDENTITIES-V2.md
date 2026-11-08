# Versioned business identities and original custody

C02 implements finite data contracts, canonical projections and schema checks. It does not implement selection/review/decision/input registries, a native model exporter, a solver or runtime generation. K01/Q01/L02 implement and check those original owner joins after the shared contract gate. A matching digest, a TypeScript interface or a serialized object never supplies original custody.

Core owns the identity protocol and fixed capture/review/decision/lock schemas. The new original input is named `AuthoringBusinessInputV2`; the existing public `BusinessInputV2` continues to name the older application-carrier contract. Alch has a checked data-only protocol mirror and independently implemented projection functions; it imports no private Core runtime source. `validateBusinessAuthoringContractV2` accepts only fixed owner schema names and captures inert data before checking it. Captured data is not admitted or registered.

## Canonical fields and ordering

All identities use UTF-8 SHA256 over compact JSON with recursively sorted object keys. No whitespace, locale collation, numeric truncation or Unicode normalization is introduced. Valid Unicode scalar strings preserve their exact spelling. Declaration lists sort by exact ID; Entity fields and claim signature declarations sort by exact name. Claim subject references sort lexically. Positional argument lists, predicate parameter sorts, field paths, guard sequences, scenarios, requirements' actor/applicability/boundary sequences retain their authored order. These rules are versioned, not retroactive changes to v1.

| Identity | Included fields | Excluded fields and meaning |
|---|---|---|
| Direct executable projection | Projection/contract versions; model identity; requirements with context/actors/examples/counterexamples/boundaries; Entities and typed fields/identity; Rule ID/requirement/input/actual condition; Operations with guards/result/rejection/effects; logical entries with inline permission | Definitions, claims, source spans/obligations, physical paths, Rule explanatory prose, profile/tools/native bytes and later owner handles. This is normalized business meaning, not a fully realized native application |
| Optional assurance projection | Version, complete definitions and claims, including declared subjects, signatures, proposition and ceiling | Does not supply the executable condition, generation permission or proof |
| Review subject | Both projections and their digests, original complete authored Rules including prose, model ID/owner/version and contract versions | No decision, accepted flag, original selection handle or generated graph can be inserted into this inspectable data |
| Source capture | Exact logical source key/bytes/digest, exact profile IDs/versions/bytes, exact tool identities/bytes and recipe version | Does not include future generated code; physical roots/inode custody remain with the actual source/file owner, not a portable digest |
| Native basis reference | Actual later SDK/basis/configuration digests with exact ABI/descriptor | Actual assets are resolved by J01; this is not the generated callable/handler/application subject |
| Early authoring lock | Source/executable/assurance/basis/selection/review/decision-file/entry-intent identities and its own digest | Callable/handler/request-graph/final application digests are unavailable before G01/U08 and reject as fields |
| Native realized subject | Actual callable, native-bound request graph, codec/handler/configuration/runtime closure plus source/business meaning | Produced only by U08 after actual emission and genuine late binding; not by C02 |
| Observation | Actual observed subject, producer, environment and outcome | Never a substitute for requirement resolution, proof, product approval or operational authority |

The early lock's digest is computed over the exact lock body excluding `lock_sha256`. It remains data until its actual owning loader constructs and checks the current source/profile/tool/decision chain. Shape validation does not verify original file bytes or grant acceptance.

The selected native ABI and descriptor are exactly C03's `craft.u0.pure-submission/v1-candidate` and `node-http-entry-u0-v4`. Behavior-affecting configuration/native/recipe edits change the native basis or realized subject even when the direct executable projection is unchanged. No fixed hash of future codec/handler/application bytes exists at C02.

## Source recapture and private owner checks

Changing a claim or its ceiling preserves the direct executable projection when the business behavior is unchanged. It changes assurance, review and exact source capture. Changing only Rule explanatory prose preserves the direct executable projection but changes the review and source capture. A condition, result, rejection, entry/access or type edit changes/rejects the executable subject as appropriate. Byte/comment/source-location edits recapture source even when projected meaning remains equal.

Every source-bound handle retires after source/profile/tool/module changes, decision-file replacement/drift, disposal or ownership mismatch. A preserved executable digest cannot retag an old source-bound object into a new epoch. K01/L02 must use original private registries and independently reconstruct/check subjects. JSON clones, object/proxy wrappers, foreign selections, stale decisions and copied accepted flags fail at those owners. C02 declares the exact surfaces and reasons; its pure projection tests do not claim those runtime checks already exist.

The protocol makes the producer order explicit: actual SDK/native basis → genuine selection → original early entry/Mapping requests and genuine review/recorded decision → original accepted input → actual compiled graph/callable → late native binding/final realized subject. The early request does not require a future callable or final request graph. Public tuple/type fields are descriptive; only the named owning implementation can produce a genuine original handle.

## Legacy and future formal models

V1 keeps its existing claim-derived executable condition and exact original meaning/definition/decision reconstruction. This implementation does not reinterpret v1 sources or convert missing claims into true conditions. The explicit v2 source header selects the new contract later at U01; existing v1 modules/pins remain unchanged.

`OptionalBaseModelIdentityV2` reserves the first U1 TPTP TFF0 AST/symbol/coverage comparison contract with an exact selected native profile identity. It produces no AST/model/export/parser/proof now. Whole bundle equality is not inferred from unchanged executable meaning. Optional claims never make code-only generation depend on a native formal parser, TDE or EVF.

## Open Questions

K01/Q01/L02 implement real original registry/currentness/decision-file checks. J00 owns schema/export/package wiring and cross-owner signature integration. J01/G01/U08 produce actual native/bound subjects. U1's exporter/parser and AST correspondence remain a separate unselected branch. C02 qualification covers data/canonical/configuration contracts only; hosting, TDE, EVF, live activation and publication remain deferred.
