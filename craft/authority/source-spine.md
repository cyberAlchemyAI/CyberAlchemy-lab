<!-- MINT-ACT OUTPUT (L1) for domainspec-v2. Cast from templates/source-spine.md. INTERNAL/private.
     INHERITS the Source-Families FORMAT, source-kind labels, harvested-controls demotion shape.
     LOCALIZES the families. Obs-B: framework rows are citation/provenance ONLY, forbidden on any
     resolution path. -->

# Source Spine

Status: active
Owner: DomainSpec v2 owner

## Source Families

| Family | Current source | Allowed use | Blocked use |
| --- | --- | --- | --- |
| DomainSpec language (primary) | `authority/AXIOMS.{md,yml}`, `authority/constitutions/domainspec-v2-CONSTITUTION.md`, root `definitions/`, remaining `impl/spec/` contract/import surfaces (TAXONOMY, TEST-PIPELINE, DRIFT-CONVERGENCE, CONSTITUTION), and research `DEFINITIONS.md` | Official claims about the DomainSpec language and its derivation discipline. | Inferring unstated policy; treating local synthesis as the spec's declaration. |
| Feature packs (primary) | `docs/features/<f>/` DFDS aspect docs (when authored) | What a specific feature's spec says about itself. | Treating one feature's reading as a general rule. |
| **DomainSpec v1** *(harvested precedent)* | `implementation/domainspec/` @ `33859b5` (frozen; see `IMPORT-MANIFEST.md`) | **Harvested precedent (supporting source) — citation/provenance ONLY**: the as-built source v2 imported + reformulated. | **Treating v1 as authority over v2 design, or on ANY resolution path** (validation/layering/drift decisions resolve to *this repo's own* `authority/`, never to v1). |
| **CyberAlchemy v2** *(harvested precedent)* | `cyberAlchemy-v2/authority/` | **Harvested precedent (supporting source) — citation/provenance ONLY**: how the authority-spine shape was cast. | **Treating cav2 as authority over v2 design, or on ANY resolution path.** |
| Formal precedent | `domainspec-lean-formalization/` (sorry-free kernel) | Supporting/analogy precedent for formal claims — the amplifier. | Claiming a result the Lean kernel does not locally prove; resolution-path use. |
| Engine fixtures / evidence | `impl/test-derivation-engine/` self-tests; the import triage (`research/2026-06-29-v1-import-triage/`) | Related evidence; witnessed examples. | Treating one fixture as general proof. |

## Source-Kind Labels

Use these labels in claims and synthesis:

- `primary-source`
- `supporting-source`  *(this is what harvested v1 / cav2 / Lean precedent gets — never `authority`)*
- `related-source`
- `analogy`
- `local-inference`
- `operator-reading`
- `open-residue`

## Harvested Local Controls

The domainspec-v2 harvest of DomainSpec v1 and CyberAlchemy v2 closed as a set of
**bridge-labeled v2 controls — citation only, not authority**. Reuse local citations first and
preserve the demotions:

- a drift signal is not a correction, and detecting drift is not converging;
- a passing derived test is not runtime conformance;
- harvested v1/cav2 precedent supports credibility, it is not v2 correctness;
- **authority moves only by domainspec-v2's OWN owner route — never by a framework edge;**
- **a framework return/adopt-back package is at most a DEFERRED candidate evidence package; no
  cyclic citation chain can promote authority in either repo** (Obs-B at the harvest level).

## Authority / Lifecycle Boundary

The CyberAlchemy v2 and DomainSpec v1 authority/lifecycle material is **locally cited as harvested
method/provenance precedent (supporting source), NOT v2 proof**. Local statuses
(`domainspec-v2-pass/flag/block`) create no validation proof, policy effect, implementation
readiness, or **authority effect**. Downstream use needs exact local citations and **v2's own
owner-route selection** — the framework is never the deciding authority.
