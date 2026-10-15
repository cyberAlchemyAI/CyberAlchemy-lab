# Execution protocol

> Generated from [PLAN-SOURCE.json](../PLAN-SOURCE.json).
> Standalone candidate. 33/35 tasks accepted with hash-bound evidence; see task receipts for review scope. No formal Invoke admission is claimed.

1. Complete F0 (P01 → P03 → P04 → P05), including the pinned Lean toolchain, independent semantics, inhabited example, general soundness and evidence review.
2. Refresh B00 against the reviewed formal model and align candidate schema/API projections in P02; replan/reprove if bound inputs drift.
3. Start every task only with accepted, current prerequisite evidence.
4. Work in the candidate scope and publish versioned exported contracts.
5. Complete working units, validation and evidence review; explicitly narrow unsupported profiles.
6. Close the wave check after every member is accepted and re-evaluate dependencies after changes.
7. Close each layer gate while retaining its named claim ceiling.

## Wave checks

Each dependency-depth cohort has one wave check. It verifies membership completion, evidence currentness, hard obligations and scope conflicts. These are review controls, not additional DAG nodes; they do not create dependencies between independent branches.

| Wave | Tasks | Single closure check |
|---|---|---|
| [W00](work-pack/waves/W00.md) | P01 | WV-W00 |
| [W01](work-pack/waves/W01.md) | P03 | WV-W01 |
| [W02](work-pack/waves/W02.md) | P04 | WV-W02 |
| [W03](work-pack/waves/W03.md) | P05 | WV-W03 |
| [W04](work-pack/waves/W04.md) | B00 | WV-W04 |
| [W05](work-pack/waves/W05.md) | P02 | WV-W05 |
| [W06](work-pack/waves/W06.md) | P06 | WV-W06 |
| [W07](work-pack/waves/W07.md) | G0 | WV-W07 |
| [W08](work-pack/waves/W08.md) | C01 | WV-W08 |
| [W09](work-pack/waves/W09.md) | C02 | WV-W09 |
| [W10](work-pack/waves/W10.md) | C03 | WV-W10 |
| [W11](work-pack/waves/W11.md) | C04 | WV-W11 |
| [W12](work-pack/waves/W12.md) | C05 | WV-W12 |
| [W13](work-pack/waves/W13.md) | C06 | WV-W13 |
| [W14](work-pack/waves/W14.md) | G1 | WV-W14 |
| [W15](work-pack/waves/W15.md) | E01 | WV-W15 |
| [W16](work-pack/waves/W16.md) | E02 | WV-W16 |
| [W17](work-pack/waves/W17.md) | E03, E04 | WV-W17 |
| [W18](work-pack/waves/W18.md) | E05 | WV-W18 |
| [W19](work-pack/waves/W19.md) | G2 | WV-W19 |
| [W20](work-pack/waves/W20.md) | I01 | WV-W20 |
| [W21](work-pack/waves/W21.md) | I02, I05 | WV-W21 |
| [W22](work-pack/waves/W22.md) | I03 | WV-W22 |
| [W23](work-pack/waves/W23.md) | I04 | WV-W23 |
| [W24](work-pack/waves/W24.md) | I06 | WV-W24 |
| [W25](work-pack/waves/W25.md) | G3 | WV-W25 |
| [W26](work-pack/waves/W26.md) | R01, R02 | WV-W26 |
| [W27](work-pack/waves/W27.md) | R03 | WV-W27 |
| [W28](work-pack/waves/W28.md) | R04, R05 | WV-W28 |
| [W29](work-pack/waves/W29.md) | R06 | WV-W29 |
| [W30](work-pack/waves/W30.md) | G4 | WV-W30 |

## Replan triggers

- Required source bytes or a reviewed semantic contract change.
- A supported profile is inconsistent or a required proof cannot be discharged.
- Scope expands into immutable authority, live runtime or actual admission.
- An interface change affects accepted downstream evidence.

Narrow scope explicitly when justified; do not drop obligations to obtain readiness. Dates, staffing and automatic delegation remain unassigned.
