---
node_type: research
subject: drift capability triage — v1 → v2 import
role: scout
persona: Ashby, W. Ross (CODE-TAG DRIFT)
dispatch_id: 2026-06-29-domainspec-v1-import-triage
date: 2026-06-29
---

# Drift-Scout Memo — W. Ross Ashby

## Frame: Drift as a Control Problem

In Ashby's law of requisite variety, a regulator must match the variety of the system it
governs. Applied here: the code surface is the plant; the spec is the reference model; a
drift-detection subsystem is the error signal; convergence is the controlled variable. The
question for each capability is whether v1's mechanism belongs in v2's control loop — or
whether v2 must reformulate it to govern *Ontology A evidence* rather than raw code symbols.

---

## Candidate Rows

### C1 — Tag Extraction

**What it does (cite):** `extract-code-tags.ts` walks TS/JS/Python source trees, parses
docstring YAML blocks, and emits a JSON catalog of `{concept.id, concept.type, edges[], file,
line}` per tagged symbol (SKILL.md lines 6–8; `extract-code-tags.ts` lines 36–78).

**Verdict leaning:** IMPORT

**Why:** This is raw sensing — it converts unstructured code into a machine-readable triple
set. v2 needs exactly this to populate the evidence layer (governed by Ontology A). The
extractor is already multi-language (TS adapter, JS adapter, py adapter) and outputs a typed
schema (`ExtractionOutput`). No spec-level concepts are hardcoded; it is purely structural.

**Leverage:** Zero-cost evidence ingestion for the governed surface. The JSON output feeds
both the validator and the drift comparator — one extraction, two consumers. Portable with
minor CLI-path adaptation.

**Guardrail check:** Extraction reads code; it does not write promotion-status or governance
verdicts. Adapter line is not crossed. Free/moat boundary is safe (extractor is the free
wedge — it is the spec-to-code bridge plumbing, not the attestation governance layer).

---

### C2 — Drift Detection (compare-code-tag-drift)

**What it does (cite):** `compare-code-tag-drift.ts` materializes doc triples from SPEC.md
`Feature Concept Graph` tables and code triples from the extracted tag JSON, then computes
four error sets: docs-only (spec asserts, code missing), code-only (code asserts, spec
silent), direction-mismatch (edge reversed), type-mismatch (concept typed differently in code
vs doc) (lines 66–121). Emits a structured markdown report and exits non-zero in strict mode
when any error set is non-empty.

**Verdict leaning:** REFORMULATE

**Why:** The mechanism — set-difference over typed triples — is correct control theory. The
error signal is exactly the deviation the regulator needs. However, v1's source-of-truth for
spec triples is the `Feature Concept Graph` table inside SPEC.md files. v2's governed surface
is Ontology A evidence (`.arcanum/inventory/entries/ontology-operationalization-in-the-machine-synthesis.md`).
The spec reader must be re-targeted: instead of parsing `docs/features/*/SPEC.md`, it should
parse the ontology evidence surface (catalog entries, attestation records, or equivalent v2
artifacts). The triple-diffing algorithm is importable as-is; the input adapters must be
re-authored.

**Leverage:** The four-error-category schema (docs-only / code-only / direction-mismatch /
type-mismatch) is a clean error taxonomy that maps directly onto Saturn drift surfaces
(build-time fidelity, contract drift). REFORMULATE preserves the error-signal model while
redirecting the sensor inputs.

---

### C3 — Convergence Tracking (DRIFT-CONVERGENCE canonical doc)

**What it does (cite):** `DRIFT-CONVERGENCE.md` defines five drift surfaces (build-time,
runtime, governance, async-learning, closure/progress) and convergence criteria (drift
signals trending down, blockers shrinking, evidence-backed completion). It maps each surface
to a canonical authority document and states the Saturn L-system as the operational loop
acting on the signals (lines 1–166).

**Verdict leaning:** IMPORT

**Why:** The conceptual architecture is the control-loop itself — reference model, error
signal, corrective action, verification. This document correctly separates *what counts as
drift* from *what acts on drift* (Saturn). That separation is a load-bearing architectural
choice. v2 must preserve it: Ontology A governance is still a regulator acting on a plant
(evidence corpus); drift definitions and convergence criteria belong in v2's authority layer.
The five-surface taxonomy may compress (e.g. governance and closure surfaces merge under
Saturn in v2) but the framework imports cleanly.

**Leverage:** Provides the vocabulary layer that prevents Saturn and the drift sensor from
being conflated. In v2, where Ontology A operationalization is the governing objective, the
convergence criteria directly translate to "evidence coverage trends upward, attestation gaps
trend downward."

---

### C4 — Tag Validation (validate-code-tags)

**What it does (cite):** `domainspec-tag-code` SKILL.md step 7: runs
`validate-code-tags.ts --input code-tags.json --waivers code-tag-waivers.yaml --features-root
docs/features/{feature} --mode <mode>` and returns BLOCK on critical/high failures.
`CODE-TAG-SCHEMA.md` defines required fields (`concept.id`, `concept.type`), edge-direction
constraints (`enforces` must be `Rule → Operation`), and taxonomy/relationship label
enforcement.

**Verdict leaning:** REFORMULATE

**Why:** The structural contract (required fields, typed edges, direction semantics) is
exactly what v2 needs for Ontology A enforcement. The waiver mechanism (explicit
code-tag-waivers.yaml) is governance-sound and should be preserved. However, two things must
be re-authored: (a) the taxonomy label set must align with v2's Ontology A concept types (not
the v1 TAXONOMY.md), and (b) the relationship label set must align with v2's typed-edge
vocabulary. The validator's schema-check engine is importable; its dictionaries are
reformulated.

**Leverage:** Waiver registry pattern is reusable verbatim — it externalizes exceptions from
the gate logic, keeping the gate strict without hardcoding every edge case. CI-gate
integration (strict/warn modes) is directly portable.

---

### C5 — Registry Sync (domainspec-sync-registry)

**What it does (cite):** `domainspec-sync-registry` SKILL.md: parses concept tables from
`docs/features/*/SPEC.md`, merges into `docs/registry.md` and `docs/glossary.md` by
meta-type, detects duplicates, and emits drift warnings (lines 1–32).

**Verdict leaning:** REFORMULATE

**Why:** The registry-sync pattern is a write-back from distributed spec sources into a
canonical index — exactly what v2 needs to maintain the Ontology A concept catalog from
distributed evidence entries. But v1's source is `SPEC.md` concept tables; v2's source is
the ontology evidence surface. The sync logic (parse → merge by meta-type → detect
duplicates → emit warnings) is importable; the reader adapters and target paths are
reformulated.

**Leverage:** The duplicate-detection and drift-warning emit pattern prevents catalog
fragmentation silently. That property is critical in v2 where Ontology A authority must
remain singular. The `--all` flag (fan across all features) maps cleanly to a v2
`--all-evidence` fan.

**Note:** Registry sync is a write operation on the catalog, not on attestation or
promotion-status. The write-authority proviso is satisfied (it writes the concept index, not
governance verdicts).

---

## Control-Problem Summary

From Ashby's perspective:

| Capability | Error Signal | Regulator Role | v2 Control Loop Fit |
|---|---|---|---|
| Tag extraction (C1) | Converts plant state to signal | Sensor | IMPORT — sensing layer unchanged |
| Drift detection (C2) | Computes set-difference vs reference | Error computer | REFORMULATE — algorithm stays, reference re-targeted |
| Convergence tracking (C3) | Defines what "improvement" means | Reference model | IMPORT — vocabulary and criteria import cleanly |
| Tag validation (C4) | Checks signal against schema | Gate / enforcer | REFORMULATE — engine imports, dictionaries reformulated |
| Registry sync (C5) | Writes state back to canonical index | State integrator | REFORMULATE — pattern imports, adapters re-authored |

No capability is DROP. Every v1 mechanism provides a control-loop sub-function that v2
requires. The reformulations are adapter-level, not algorithmic — the error-signal models
and convergence criteria are sound and owned.

---

## Free/Moat Boundary Note

The drift-detection stack (C1–C5) is the **free wedge** side: it is observable infrastructure
that keeps code aligned with spec. The **moat** is the attestation layer and governance-data
surface that decides what counts as evidence and promotes claims. Drift detection may be
published; the attestation engine algorithm stays proprietary (per ASSIMILATION-TABLE S3 and
memory).
