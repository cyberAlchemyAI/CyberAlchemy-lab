# AlchLang behavioral-claim fix DAG (candidate)

Scope: AlchLang source, CLI, compiler consumers, and package boundary only. This
is not a Define-runtime rewrite, an authority promotion, or an Invoke artifact.

```text
A claim vocabulary and ceiling
  -> B profile/claim fit
    -> C cross-type source closure
      -> D projection and runtime evidence
        -> E qualification and regression checks
```

| Node | Review decision | Current result |
| --- | --- | --- |
| A | Separate source closure from observed execution; do not call a build a runtime. | Implemented as `closed-state-model` versus fail-closed `executable-runtime`. |
| B | Only canonical `application-v1` can make the closed state-model claim. Adapter profiles retain their own bounded contracts. | Implemented in `qualify`; not a global parser rejection. |
| C | Require first-class Operation, Entity, Event, and State Machine declarations to join on each transition's subject write and trigger production. An external Event is valid source but does not satisfy a closed-world claim. | Implemented as opt-in source qualification. Policy and Workflow execution coverage remain unclaimed. |
| D | Inventory each adapter's proxy projection and attach exact runtime observation before permitting an executable claim. | Not implemented; runtime claim rejects with `ALCH_RUNTIME_UNOBSERVED`. |
| E | Test positive and hostile claims, CLI, types, package allowlist, and full-suite compatibility. | Focused tests, typecheck, build, and package check pass. Full suite has existing missing ARE adapter dependency in `module-configuration.test.ts`; full-suite pass is not claimed. |

The DAG review found no required cycle: source claim checks do not depend on
runtime evidence, while runtime claims do depend on source qualification. The
first executable slice is deliberately an opt-in gate, so it does **not** yet
make this behavior the default for every AlchLang command or consumer.

## Open Questions

- Which generated artifact and provider-observation contract will satisfy D?
- Which consumers must require `qualify` before advertising a closed state model?
- Should Policy and Workflow receive separate claims or be prerequisites of a
  broader application behavior claim?
