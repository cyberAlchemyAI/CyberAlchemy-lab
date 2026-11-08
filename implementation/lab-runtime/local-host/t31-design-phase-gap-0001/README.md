# T31 designed-transition causal refusal

The selected T31-0002 run observes four of 28 original output-bearing transition identities. This disjoint diagnostic inspected the two remaining `prepared → designed` candidates without changing their producer, output, or source files. It found **no new countable transition**:

| Transition | Actual phase behavior | Why the required output cannot be attributed to this phase |
| --- | --- | --- |
| `engineering:designed` | Checks connection types and records a proposed output digest | The corrected bytes are obtained in `execute`; the GeneratedOutput carrier is constructed in `materialize` after assessment. The design event has no actual output receipt. |
| `research:designed` | Checks selected inputs and records the design reference/procedure | The ExperimentDesign already exists in the SHA-pinned selection package before `ResearchWorkflow.design()`. The event references that input; it does not produce it. |

`check.py` pins the original producer bytes, selected research package, predecessor RESULT, exact phase event/WorkflowRun bytes and bindings, and exact first-event fields. Its RESULT binds the diagnostic code hash. It refuses a retrospectively inserted output claim even when the event binding is coherently recomputed; the default selected replay also refuses any coherently changed phase bytes. The resulting [RESULT.json](RESULT.json) retains **4 observed / 24 remaining** and claims no native journal or qualification. Seven tests pass under normal and optimized Python, covering both false output claims, a coherently changed selected phase, changed selected inputs/producer, and a symlinked ancestor.

The next implementation cut must create a genuinely phase-bound producer and later consumer for a remaining original template or alter a designed phase so it actually emits its required carrier, then verify that new behavior against its original contract. The retained candidate tree contains WorkflowRun producers only for engineering and research; its other template metadata does not supply observed outputs. This diagnostic itself completes none of the 24 remaining transitions.

```bash
python3 -B implementation/lab-runtime/local-host/t31-design-phase-gap-0001/check.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t31-design-phase-gap-0001 -p 'test_*.py' -v
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t31-design-phase-gap-0001 -p 'test_*.py' -v
```
