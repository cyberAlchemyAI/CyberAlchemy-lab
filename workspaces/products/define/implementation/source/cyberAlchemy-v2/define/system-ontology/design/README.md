# Define Runtime Discovery Design

Status: private discovery candidate; not an admitted governed Design result; authority effect none.

This subpackage converts the expanded DomainSpec v2 system ontology into a
technology-neutral runtime architecture. It is intentionally inside the Define
system-ontology package so the product meaning, DomainSpec semantic graph, and
design projections stay under the same private runtime owner.

Start with:

- [`DESIGN-CANDIDATE.json`](DESIGN-CANDIDATE.json) for the typed design registry;
- [`ARCHITECTURE.md`](ARCHITECTURE.md) for the six Design views;
- [`GAPS.json`](GAPS.json) for choices that still belong to named owners; and
- [`PLANNED-WITNESSES.json`](PLANNED-WITNESSES.json) for tests that a later Plan
  must materialize and execute.

## DomainSpec v2 reuse

The design reuses four bounded precedents without importing their authority:

1. the Define CLI modeling experiment supplies a semantic-closure workflow
   precedent;
2. the architecture ontology experiment separates ontology, profile,
   observation, and evaluation, and makes interface/event/operation/workflow
   obligations explicit;
3. the BTE Design demonstrates six projections over one design, exact contracts,
   failure precedence, and independent replay; and
4. the current DomainSpec registries constrain the package-local node kinds,
   formation bodies, and relationship signatures.

It also reuses the private Agent Reasoning Engine semantic-judgment evaluator as
a fifth, narrower feasibility witness: frozen inputs can reduce
deterministically to a typed outcome with residue and a non-authorizing receipt.
The witness is not yet a Define context-sufficiency adapter and does not supply
the owner-adopted requirement catalog for any Define job.

Those packages are evidence only. Their implementation choices do not become
CyberAlchemy decisions.

## Canonical Invoke boundary

The repository-level Invoke resolver exposes the current Design W1-W3 chain,
but normal activation requires an exact target-owner input boundary and a
current admitted Define v3 result. Neither exists for this candidate. Therefore
this directory does not manufacture `DESIGN.json`, a selection receipt, a
coherence receipt, a bundle, or admission. Its next route is owner-bound Design
input approval or resolution of the named design gaps.

## Claim ceiling

This package makes the minimum runtime contracts and unresolved selections
visible. It does not select a storage product, transport, process topology,
identity provider, retention duration, numeric SLO, deployment environment, or
public Arcanum migration. It does not prove implementation, witness execution,
DomainSpec conformance, Plan readiness, acceptance, publication, release, or
deployment.
