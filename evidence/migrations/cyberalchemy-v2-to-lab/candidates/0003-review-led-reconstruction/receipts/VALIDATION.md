<!-- GENERATED FILE: canonical data is validation.json. -->

# Normalized Reconstruction Validation

- Result: `PASS`
- Checks: `45/45`
- Authority effect: `none`

| Check | Result | Detail |
|---|---|---|
| `no-authority-effect` | `PASS` | Candidate has no authority effect. |
| `no-bulk-copy-artifacts` | `PASS` | No copy allowlist, executor, or migration transport exists. |
| `accepted-normalization-bound` | `PASS` | The selected normalization bytes are exact and current. |
| `owner-decision-bound` | `PASS` | The owner-selected planning baseline is exact. |
| `baseline-source-bound` | `PASS` | The source bytes reviewed by NORMALIZE-01 remain retrievable at the exact Git commit. |
| `current-source-bound` | `PASS` | The current CAV2 definition source is exact. |
| `accepted-decision-closure` | `PASS` | All 69 accepted source-definition decisions are preserved. |
| `focused-source-drift` | `PASS` | Only CAV2-D65 changed after normalization; 68 decisions remain closed. |
| `d65-only-reopened` | `PASS` | The sole semantic reconsideration is D65 source drift. |
| `withdrawal-preserved` | `PASS` | CAV2-D70 through CAV2-D81 remain withdrawal records. |
| `normalized-target-family-closure` | `PASS` | All five normalized target families and all 195 targets are present. |
| `normalized-target-identity-unique` | `PASS` | Each normalized target identity occurs once in the realization ledger. |
| `realization-state-counts` | `PASS` | Realization states close over every normalized target. |
| `admission-not-inferred` | `PASS` | Only exact registry evidence yields a realized state. |
| `lab-definition-digests-current` | `PASS` | All current admitted Definition entries used for matching resolve to exact bytes. |
| `lab-artifact-type-digests-current` | `PASS` | All current admitted Artifact Type entries used for matching resolve to exact bytes. |
| `define-pack-target-closure` | `PASS` | The migration Definition Pack handles every normalized target exactly once. |
| `define-dispositions-valid` | `PASS` | Every target uses one CAV2 Define disposition. |
| `define-axis-orthogonal` | `PASS` | Define dispositions do not replace accepted migration dispositions. |
| `define-registry-not-mutated` | `PASS` | The CAV2 Define handled registry is an exact read-only dependency. |
| `d65-open-scope` | `PASS` | Only the six D65-derived targets are open. |
| `target-prototype-index-closure` | `PASS` | All 176 unresolved non-D65 targets have one indexed prototype scaffold across the five normalized families. |
| `target-prototype-digest-closure` | `PASS` | Every target prototype machine artifact and generated human projection matches its index digest. |
| `target-prototype-four-facet-closure` | `PASS` | Every authored target is explicitly non-authoritative and carries all four artifact facets. |
| `semantic-definition-voice-closure` | `PASS` | All 69 semantic prototypes carry distinct normative, formal, plain-language, domain-context, and boundary voices. |
| `target-human-projections` | `PASS` | Every target human file is an exact projection of its canonical machine artifact. |
| `queue-excludes-settled-decisions` | `PASS` | Settled source-definition decisions are not queued again. |
| `realization-queue-closure` | `PASS` | Every unresolved normalized target has one realization unit. |
| `one-approval-boundary` | `PASS` | The chain accumulates distinct decisions for one final approval boundary. |
| `followup-queue-state` | `PASS` | The queue records 176 authored prototypes, six D65 units pending successor selection, ten authored reviews, and one final token. |
| `ontology-package-closure` | `PASS` | Every ontology package belongs to a downstream review group. |
| `ontology-control-surfaces-included` | `PASS` | Schema bindings, type selection, materialization decision, and residue are inventoried. |
| `domainspec-routes-to-craft` | `PASS` | DomainSpec-v2 lineage routes to Craft under NORM-OQ-5. |
| `ontology-after-realization` | `PASS` | Ontology reviews are authored after the non-D65 target prototype pass and remain non-authoritative pending the final planning decision. |
| `ontology-review-index-closure` | `PASS` | Each of the ten ontology inventory groups has one indexed review. |
| `ontology-review-digest-and-projection-closure` | `PASS` | Every ontology review and generated human view matches its index and renderer. |
| `ontology-type-selection-explicit` | `PASS` | Eight ontology group types come directly from source profiles; two dual-ref governance profiles carry explicit business-system-bridge proposals for the final checkpoint. |
| `domainspec-review-preserves-lineage-conflict` | `PASS` | The DomainSpec lineage review routes to Craft without hiding its competing canonical claims. |
| `d65-successor-proposal-closure` | `PASS` | The D65 successor retains only independently useful carriers and profiles, rejects redundant axes, and remains a proposal. |
| `single-composite-decision-boundary-ready` | `PASS` | One exact token binds three distinct planning decisions without granting admission or operational authority. |
| `candidate-followup-summary-current` | `PASS` | The candidate summarizes the complete authored follow-up chain and final checkpoint exactly. |
| `generated-projections` | `PASS` | Every declared human view is an exact generated projection. |
| `manifest-material-closure` | `PASS` | Every candidate material matches its manifest digest. |
| `manifest-source-closure` | `PASS` | Every repository-relative file and Git-blob source binding is current. |
| `claim-ceiling` | `PASS` | Validation cannot inflate authored prototype scaffolds into refined canonical artifacts, migration completion, or authority. |

## Claim ceiling

PASS proves only that the accepted normalization, focused D65 drift, 195-target realization ledger, 176 non-authoritative prototype scaffolds, ten source-ontology reviews, the D65 successor proposal, the one-token planning request, generated projections, and exact source bindings are internally closed and current. It does not select the proposals, refine or admit artifacts, approve or execute migration, activate runtimes, commit, push, publish, release, or deploy.
