# Exact original R06/G4 review packet

This packet asks whether the original relational checker gives the intended meanings and useful diagnostics, and whether its measured limits support bounded local shadow use. It is a versioned review of original R06/G4. Your earlier v3 P11 answer remains valid for that earlier packet; it is not copied as acceptance here.

Machine preparation is complete. R06 and G4 remain pending actual human assessment. The current source audit verified **9,178 files**. The original plan has 35 tasks, 40 working units and 56 dependencies: 33 historical acceptances remain current. The successor has 19 accepted units, 19 complete final-source extension witnesses and 277 extension control records. These are scoped checks, not 277 distinct theorems. Existing proof executions were re-audited; the nine new gate theorems were actually compiled and replayed.

## 1. What the relations mean

The model is a typed versioned graph. A relation assertion has exact endpoint revisions, an allowed ordered kind pair, explicit qualifiers and source-bound evidence. A reversed pair or evidence about another revision cannot silently establish the same claim.

**Conforms-to** means an accepted supplied assessment concerns this exact subject, target revision and scope. The captured example is `capability:reviewer@v1 → contract:review@v1`, scope `static`, with one opaque evidence token. Changing the target-version qualifier to another revision breaks that meaning. Acceptance proves consistency with the supplied assessment; it does not authenticate the assessor or grant permission.

**Declares-effect-on** records a decision's declared effect on an exact target revision. It describes the intended effect. It does not execute the effect or make a successor eligible.

**Materializes-consequence** requires a supplied accepted receipt matching the exact transaction, output, consequence role and output digest; the digest must equal the output node's supplied content identity. It proves consistency of those supplied records, not actual execution, cryptographic computation or transaction authorization.

The additional semantic stress profile distinguishes a recorded `acts-for` edge from effective representation at an exact snapshot: scope, action, interval, revocation and required assessments must hold. The logic stress profile propagates inherited contract norms with their origin. Potential obligation, active obligation, fulfilled obligation and authorization are separate meanings.

The seven later extensions add expressions, evidence collections, bounded chains, criterion fulfillment, lifecycle transitions, canonical IR and one independent-checker sample. Their complete explanation and remaining gaps are in the [separate extension annex](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/reviews/2026-10-10-r06-g4-v4/extensions-annex.md). Original gate completion does not automatically approve their composition.

## 2. What the theorems establish

For the typed supported graph, `checkGraph(G) = true ↔ Inv(G)`: successful checking matches the independently defined graph invariant. `checkAddition(G,e) = true → Inv(applyAddition(G,e))`: the whole resulting graph satisfies it. Adding a conformance edge cannot manufacture an admission root.

For positive Horn logic, derivations preserve the required premises/origins and the checked finite least closure is exact. A cycle `Review → Ready → Review` propagates a seed fact if one exists. With no seed, the least closure contains neither fact. This conclusion is about derivability from the captured facts/rules; it is not a claim that the predicates are false in all conceivable models.

The original rule-change integration is narrower than the generic engine: unchanged graph/registry, empty prior rule set, fresh ordinary unary heads and old-predicate positive bodies. An exact submitted proof, checked model and independently complete obligation inventory are needed. A valid proof of a weaker statement cannot satisfy the intended obligation. Selected-data compatibility, universal invariant preservation and expansion of every old model are distinct checks.

The new gate model proves exact review binding checks, scope separation, rejection of revisions/undecided feedback, G4's accepted-R06 prerequisite and preservation of predecessor evidence. It does not prove that a JSON quote came from a human; the operator must capture the observed direct response faithfully.

## 3. Actual worked inputs and diagnostics

The [worked-example inventory](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/reviews/2026-10-10-r06-g4-v4/worked-examples.json) links complete raw inputs, command arguments, exact outcomes, obligations and diagnostics. The examples below are actual bound executions, not hypothetical success labels.

| Actual case | Exit | Interpretation |
|---|---:|---|
| [f0-instance](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/cli/cases/f0-instance-outcome.json) | 0 | Exact supported graph/addition accepted. |
| [f0-semantic-failure](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/cli/cases/f0-semantic-failure-outcome.json) | 1 | Wrong literal target-version qualifier refused. |
| [extension-semantic-failure](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/cli/cases/extension-semantic-failure-outcome.json) | 1 | Selected-data compatibility failure names the assertion and correction. |
| [replay-fresh-kind](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/workflow/cli/cases/replay-fresh-kind-outcome.json) | 0 | Complete supported fresh-kind evidence replayed. |
| [endpoint-extension-unsupported](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/cases/endpoint-extension-unsupported-outcome.json) | 3 | Existing endpoint widening is outside the preservation profile. |
| [complete-rule-change](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/cases/complete-rule-change-outcome.json) | 0 | All 15 independently required obligations satisfied. |
| [protected-head-unsupported](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/cases/protected-head-unsupported-outcome.json) | 3 | A new old/protected head is outside this integration profile. |
| [search-without-checked-witness](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/cases/search-without-checked-witness-outcome.json) | 4 | 14 obligations satisfied; exactly one required witness remains unknown. |

The semantic diagnostic says:

```text
Code: wrong-target-version
Message: relation.conforms-to / relation:conforms: exact_version_ref must equal the literal target version
Location: after.graph.assertions[relation:conforms]
Required obligation: c0c08fb87f597bcd52e5cc3dde06328e2104ac8dd560403daff6078d5d6fe16f:selected-data-compatibility
Next action: Set the exact-version qualifier to the literal target version, then recheck.
```

This tells you which assertion is inconsistent and what to correct. Correcting a qualifier only helps when the assessment actually supports that exact target/scope. A rejected submitted proof means invalid evidence; it does not automatically refute the theorem. A resource refusal supplies no completed semantic conclusion. A completed bounded-search request without its checked witness stays unresolved even when 14 other obligations passed.

## 4. Supported use and measured limits

The exact [supported-use matrix](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/reviews/2026-10-10-r06-g4-v4/supported-use-matrix.json) names seven original profiles. Their meanings are bounded to their versioned sources. The 41-kind registry has structural coverage across 550 ordered pairs and 109 node kinds; **263 inherited source-semantic obligations remain outside the supported meanings**. Seven extension receipts do not automatically discharge those obligations.

The original captured unary `Conforms(subject)` projection is existential: it loses target/scope detail, and the original integration epoch is 0. Do not use its unary fact to infer conformance to another contract/scope, current real-world authority or fulfillment. Existing endpoint widening, changed qualifiers/meanings, old/protected heads and unsupported mixed changes cannot borrow a preservation guarantee from this profile.

Actual original pilot costs:

| Execution | Elapsed time | Observed peak process RSS |
|---|---:|---:|
| Complete 15-obligation rule change | 818.83 s | 1.30 GiB |
| 14 satisfied plus one unresolved search witness | 1273.83 s | 1.30 GiB |

These are measured captured runs, not throughput promises or hard memory caps. The successor has different operator policies and measured examples; its IR batch completed in 125.951 s with 991.5 MiB observed aggregate RSS, while earlier representations timed out. Static input ceilings do not guarantee completion. Default RSS observation is advisory; hard enforcement requires an actual delegated host backend. A timeout stays unknown/refused.

Remaining trust includes supplied evidence/root/action truth; selected source meaning; JSON/parser/emitter/hash behavior; the pinned Lean kernel; Python/host/filesystem behavior; and cooperating local application callers. E06 independently checks one 18-declaration theorem sample and cannot establish whole-core independent validation. Its valid-proof-under-substituted-definition control shows why exact meanings must be anchored too.

## 5. Layer alignment and closure behavior

The [layer alignment audit](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/gates/l4/reviews/2026-10-10-r06-g4-v4/alignment-and-layering-audit.json) maps all original tasks and criteria to evidence or the pending actual gate assessment. L0 keeps independent meanings/checker soundness; L1 keeps structure/source guarantees; L2 distinguishes compatibility/preservation/model expansion; L3 keeps exact inference/absence/protected lineage; L4 keeps exact proof identities, complete obligations, diagnostic distinctions and recaptured candidate application.

The closure implementation has 32 passing evidence/feedback controls and 43 passing controls including actual concurrent writers and crashes immediately before/after authoritative log publication. Fixtures are marked synthetic and cannot supply actual human approval. Recovery recognizes committed state and never creates a fresh event.

Later gate acceptance is recorded in a checked append-only overlay. The original captured plan stays at its historical 33/35 state so its bound provenance remains valid. The status reader validates original criteria, outputs, current source identities and actual review before counting R06 or G4. A new `accepted` label without checked receipts is insufficient. The [API explanation](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v4/gate-closure/API.md) describes capture, acceptance and recovery.

## 6. Exactly what you need to review

For **R06**, assess whether the relation meanings above match your intent, and whether the actual diagnostics give clear causes and useful corrections. Machine proof validity is a separate completed check. State accepted, revisions needed or undecided; describe any meaning or diagnostic you want changed.

For **G4**, read the layer audit and [proposed bounded-use recommendation](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/gates/l4/reviews/2026-10-10-r06-g4-v4/bounded-use-recommendation.md). Assess whether the retained guarantees and exclusions support using this as a bounded local shadow review aid. G4 acceptance additionally requires accepted R06 and a fresh check of the same bound artifacts. It does not authorize deployment, organizational admission or authority publication.

The extension annex is explanatory context with its own scope. Its owned-definition, criterion-universe, eligibility-composition, transport and independent-checking gaps remain explicit successor work. You can recommend the original bounded use while requesting those broader improvements separately.

The exact review identities are in `review-manifest.json` next to this packet and the G4 directory. Feedback is bound to those hashes, the actual direct question/answer and the named scope. No historical approval is relabeled and no gate is accepted by merely preparing this packet.
