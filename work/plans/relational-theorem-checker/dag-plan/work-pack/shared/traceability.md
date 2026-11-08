# Traceability

| Task | Layer contract | Immediate prerequisites | Validation |
|---|---|---|---|
| [P01](../tasks/P01.md) | [L0](../../../layers/L0-working-proof.md) | baseline documents | V-P01 |
| [P03](../tasks/P03.md) | [L0](../../../layers/L0-working-proof.md) | P01 | V-P03 |
| [P04](../tasks/P04.md) | [L0](../../../layers/L0-working-proof.md) | P03 | V-P04 |
| [P05](../tasks/P05.md) | [L0](../../../layers/L0-working-proof.md) | P04 | V-P05 |
| [B00](../tasks/B00.md) | [L0](../../../layers/L0-working-proof.md) | P05 | V-B00 |
| [P02](../tasks/P02.md) | [L0](../../../layers/L0-working-proof.md) | B00 | V-P02 |
| [P06](../tasks/P06.md) | [L0](../../../layers/L0-working-proof.md) | P02, P04, P05 | V-P06 |
| [G0](../tasks/G0.md) | [L0](../../../layers/L0-working-proof.md) | P06 | V-G0 |
| [C01](../tasks/C01.md) | [L1](../../../layers/L1-faithful-baseline.md) | G0 | V-C01 |
| [C02](../tasks/C02.md) | [L1](../../../layers/L1-faithful-baseline.md) | C01 | V-C02 |
| [C03](../tasks/C03.md) | [L1](../../../layers/L1-faithful-baseline.md) | C01, C02 | V-C03 |
| [C04](../tasks/C04.md) | [L1](../../../layers/L1-faithful-baseline.md) | C01, C03 | V-C04 |
| [C05](../tasks/C05.md) | [L1](../../../layers/L1-faithful-baseline.md) | C03, C04 | V-C05 |
| [C06](../tasks/C06.md) | [L1](../../../layers/L1-faithful-baseline.md) | C05 | V-C06 |
| [G1](../tasks/G1.md) | [L1](../../../layers/L1-faithful-baseline.md) | C05, C06 | V-G1 |
| [E01](../tasks/E01.md) | [L2](../../../layers/L2-model-evolution.md) | G1 | V-E01 |
| [E02](../tasks/E02.md) | [L2](../../../layers/L2-model-evolution.md) | E01 | V-E02 |
| [E03](../tasks/E03.md) | [L2](../../../layers/L2-model-evolution.md) | E02 | V-E03 |
| [E04](../tasks/E04.md) | [L2](../../../layers/L2-model-evolution.md) | E02 | V-E04 |
| [E05](../tasks/E05.md) | [L2](../../../layers/L2-model-evolution.md) | E03, E04 | V-E05 |
| [G2](../tasks/G2.md) | [L2](../../../layers/L2-model-evolution.md) | E05 | V-G2 |
| [I01](../tasks/I01.md) | [L3](../../../layers/L3-inference-discipline.md) | G2, E02 | V-I01 |
| [I02](../tasks/I02.md) | [L3](../../../layers/L3-inference-discipline.md) | I01 | V-I02 |
| [I03](../tasks/I03.md) | [L3](../../../layers/L3-inference-discipline.md) | I02 | V-I03 |
| [I04](../tasks/I04.md) | [L3](../../../layers/L3-inference-discipline.md) | I02, I03 | V-I04 |
| [I05](../tasks/I05.md) | [L3](../../../layers/L3-inference-discipline.md) | I01, E04 | V-I05 |
| [I06](../tasks/I06.md) | [L3](../../../layers/L3-inference-discipline.md) | I04, I05, E02, E05 | V-I06 |
| [G3](../tasks/G3.md) | [L3](../../../layers/L3-inference-discipline.md) | I03, I06 | V-G3 |
| [R01](../tasks/R01.md) | [L4](../../../layers/L4-workflow-integration.md) | G3 | V-R01 |
| [R02](../tasks/R02.md) | [L4](../../../layers/L4-workflow-integration.md) | G3, P05 | V-R02 |
| [R03](../tasks/R03.md) | [L4](../../../layers/L4-workflow-integration.md) | R01, R02, C06, E02, I06 | V-R03 |
| [R04](../tasks/R04.md) | [L4](../../../layers/L4-workflow-integration.md) | R01, R03 | V-R04 |
| [R05](../tasks/R05.md) | [L4](../../../layers/L4-workflow-integration.md) | R03, C06 | V-R05 |
| [R06](../tasks/R06.md) | [L4](../../../layers/L4-workflow-integration.md) | R04, R05 | V-R06 |
| [G4](../tasks/G4.md) | [L4](../../../layers/L4-workflow-integration.md) | R06 | V-G4 |
