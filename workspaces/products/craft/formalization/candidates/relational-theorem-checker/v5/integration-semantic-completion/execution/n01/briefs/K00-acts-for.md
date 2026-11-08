K00 — relation.acts-for

Status: candidate meaning; actual owner assessment pending.

Source question: Which Principal is this Agent Instance acting for under one exact Delegation?

Source effect: Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

Proposed claim tier: checked bounded representation.

Independent witness type: `DelegationUse`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K00-acts-for.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- d.agent = s and d.principal = t; d is the exact delegation_ref revision.
- The delegator's independently established delegable envelope contains the proposed action, subject and scope.
- All joined ancestor restrictions, owned gates, effective window and as-of revocation permit this use; unknown is not permit.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| delegation_ref | DelegationRevisionRef | record.delegation: agent=source, principal=target, exact restriction envelope |
| scope_ref | OwnedScopeRevisionRef | record.scope: owned exact scope of this named connection; inclusion/temporal interpretation is kind-specific |
| effective_period | OwnedWindow = EpochInterval / SessionWindow | record.window: exact delegation window, resolved as epoch interval or session window |
| revocation_state | RevocationSnapshot | record.revocation: exact delegation status as-of the frame epoch in its time domain |

**Effect**

Record the agent's bounded representation of the principal through d; preserve identities, ownership and the authority-root set.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Agent A represents Principal P for read in scope X at epoch 5 through a delegation valid on [0,10); no write grant exists.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

A delegation for Agent B cannot justify A's acts-for edge.

**Exact excluded conclusions**

- `relation.acts-for:forbidden:0` — **identity-equivalence**: The independent governed identity model equates these endpoints, beyond representation or container membership. Participants: source and target exact revisions, with independent governed identity classes; a merge additionally binds before/after states.
- `relation.acts-for:forbidden:1` — **ownership-transfer**: A separately authorized ownership transition changes the artifact's owner. Participants: source/target or exact produced/consumed artifact from the primary witness; owner/attribute/provenance comes from the independent catalog, not a relation label.
- `relation.acts-for:forbidden:2` — **unrestricted-authority**: The actor is permitted every action/subject/scope in the independently owned universe, beyond the delegated subset. Participants: source Agent Instance and the full independently owned action/subject/scope universe; not the caller's reduced list.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K00(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 8; ordered endpoint branches: 1.

Policy decisions: D01, D02, D07.
