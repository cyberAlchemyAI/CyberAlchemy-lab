# Decision 0001: CyberAlchemy Lab repository foundation

- Status: accepted
- Date: 2026-08-30
- Decision owner: repository owner
- Source of decision: owner selected local/private option 1
- Decision effect: create one local repository foundation only

## Question

How should CyberAlchemy Lab begin while `cyberAlchemy-v2` contains active,
candidate, generated, and evidence material that cannot safely be renamed or
inherited wholesale?

## Considered options

### Option 1 — Local/private clean-history repository

Create `/home/vrondelli/projects/CyberAlchemy-lab` as a new local Git
repository. Admit no existing source material in the foundation commit and
configure no remote.

- Benefit: isolates the new stable line from dirty bytes and historical path or
  identity coupling.
- Cost: useful material must later pass explicit selection and admission.
- Reversibility: high; the repository is local and contains no external effects.
- Hazard class: local reversible mutation.

### Option 2 — Private remote immediately

Create or connect a private remote during foundation.

- Benefit: immediate collaboration and off-machine persistence.
- Cost: introduces an external effect and requires a hosting owner and exact
  visibility decision.
- Reversibility: partial; pushed history and remote metadata persist.
- Hazard class: external publication boundary.

### Option 3 — Defer or stop

Leave the current repositories unchanged and create nothing.

- Benefit: no mutation or premature boundary choice.
- Cost: the clean stable line does not begin.
- Reversibility: complete.
- Hazard class: none.

## Decision

Select Option 1.

The existing `cyberAlchemy-v2` tree remains unchanged as a source and evidence
ledger. CyberAlchemy Lab begins with new history and newly authored foundation
bytes. The first stable release target is `v1.0.0`; the foundation commit does
not claim that stability has already been achieved.

## Remaining gates

- Define and accept the minimal `v1.0.0` product slice.
- Define the source-admission and semantic-identity migration policy.
- Review private/public boundaries before any remote or public derivative.
- Validate and accept exact release candidate bytes before tagging `v1.0.0`.

## Explicitly unauthorized effects

This decision does not authorize copying `cyberAlchemy-v2`, renaming its paths
or identities, configuring a remote, publishing, promoting authority, tagging a
release, or deploying anything.
