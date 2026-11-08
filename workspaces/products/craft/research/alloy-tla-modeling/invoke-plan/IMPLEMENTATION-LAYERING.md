---
module: alloy-tla-modeling-toolchain
version: current
status: draft
updatedAt: 2026-06-16T20:51:08Z
docType: implementation-layering
observedCapability: invoke
invokeMode: plan
---

# Implementation Layering: Alloy/TLA Modeling Toolchain

## Purpose

Define the smallest safe path from research-tower feasibility to a runnable local formal-modeling surface for Alloy and TLA+/PlusCal.

This plan does not install tools or execute model checks. It makes the next `task-session` executable.

## Source Contract

- Tower: `projects/domainspec-v2/research/alloy-tla-modeling/README.md`
- Bridge decisions: `projects/domainspec-v2/research/alloy-tla-modeling/BRIDGE-DECISIONS.md`
- Closure plan: `projects/domainspec-v2/research/alloy-tla-modeling/levels/L2-closure-plan.md`
- Examples: `projects/domainspec-v2/research/alloy-tla-modeling/examples/`
- Official Alloy release source: Alloy 6.2.0, 2025-01-09.
- Official TLA+ tools source: TLA+ v1.7.4, `tla2tools.jar`, Java 11+ required.

## Target And Scope

- Target: DomainSpec v2 Alloy/TLA modeling surface.
- Scope: research tooling and validation harness.
- Current state: tower exists; example `.alloy` and `.tla` files are unvalidated; local machine has WSL/Linux, `apt`, `curl`, `wget`, `sha1sum`, but no `java`, `alloy`, `tlc`, or downloaded jars.

## Layer Boundary Rule

```text
After this layer, we know whether the next formal-modeling claim is runnable, validated, governed, or ready to package.
```

## Layer Decision Table

| Layer | Decision Question | Minimum Working Unit | Included Scope | Deferred Scope | Exit Evidence | Promotion Decision |
| --- | --- | --- | --- | --- | --- | --- |
| L0 (POC) | After this layer, we know whether Alloy and TLA+ can be installed and invoked locally without committing third-party binaries. | Install Java plus repo-local, ignored Alloy/TLA tool downloads and smoke-test their CLIs. | Java runtime check, pinned Alloy/TLA download instructions, checksum policy, `.gitignore` or local-exclude decision, smoke commands. | Model correctness, fixture generation, CI packaging. | `java -version`, `java -jar tla2tools.jar -help`, `java -jar org.alloytools.alloy.dist.jar help` or equivalent Alloy CLI help. | Continue if both tools can be invoked. |
| L1 | After this layer, we know whether the existing example models are syntactically and operationally checkable. | Run SANY/TLC against the TLA+ sketch and Alloy CLI/Analyzer against the Alloy sketch with captured receipts. | Add/adjust `.cfg`, command wrappers, run-result receipts, syntax fixes to examples only. | Generated fixtures and DCB acceptance receipts. | Parse/check receipts under `run-results/`, with tool versions, commands, and scope/model config. | Harden if both example lanes produce honest results. |
| L2 | After this layer, we know whether the formal runs can be repeated from the TypeScript saga witness contract. | Define a TypeScript `SagaSpec` export shape and one generated or manually synchronized fixture consumed by both Alloy and TLA. | Fixture JSON contract, generator design or manual sync rule, deterministic/non-rerunnable fact split. | Canonical DomainSpec validators, taxonomy mutations, broader model library. | Fixture contract plus validation that examples align to the fixture. | Prepare integration task if fixture contract holds. |
| L3 | After this layer, we know whether the surface can be packaged as a reusable DomainSpec v2 research harness. | Package wrapper scripts, receipts, docs, and optional CI/local commands without binaries. | Tooling README, receipts schema, repeatable commands, optional local CI recipe. | Public package, canonical validator integration, TLAPS proof lane. | Clean verification report and updated `LEARNING-PACK.md`/`gates/closure-gates.md`. | Pilot as research harness; defer canonical promotion. |

## Non Regression Guardrails

- Do not commit downloaded jars, tarballs, OS packages, or extracted third-party binaries.
- Do not mutate `arcanum/definitions/TAXONOMY.md` or `arcanum/definitions/RELATIONSHIPS.md`.
- Preserve the current proof vocabulary: TypeScript bounded witness, Alloy bounded graph check, TLC finite-model check, DCB freshness acceptance.
- Do not claim formal proof unless TLAPS or another theorem prover is actually used.
- Prefer pinned stable releases for the first local surface; record a separate decision before using a TLA+ pre-release.

## Recommended Next Layer

- Next layer: L0
- Key decision unlocked: Can this repo invoke Alloy and TLA+ locally with ignored, reproducible tool downloads?
- Major deferred scope: Syntax/model repair and fixture generation stay out of L0.
