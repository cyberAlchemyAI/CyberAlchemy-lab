# Define runtime design: two-round Distill result

Status: proposed critique and repair. Authority effect: none.

## Conclusion

**The preparation unit is coherent. Complete runtime integration remains FLAG.** The original design preserves the right semantic boundaries, but commits too early to internal module structure while leaving review ingress and durable reconstruction insufficiently specified.

This is a critique of the [existing design](../0006-runtime-integration-design/README.md), not an amendment to its frozen bytes or to the reviewed definitions. Two recursive rounds used independent Proposer and Balancer agents, followed by reconciliation. No third round was run.

## Start here

1. Read the [eight findings](CRITIQUE.md): what is overbuilt, what is missing, and the source evidence.
2. Read the [smaller proposed design](DISTILLED-DESIGN.md): the unit, incident example, handoff and acceptance boundaries.
3. Consult the [round trace](ROUNDS.md) for objections, decisions and remaining disagreement; [run metadata](run.json) records techniques and exact source bindings.

## Selected optimization point

```text
explicit request + exact, provenance-classified captured bundle
                              ↓
                       prepare and check
                              ↓
           frozen Definition Pack + preparation report
```

Organize implementation around three responsibilities: **capture and normalize; construct and check; export and hand off**. These are behavior boundaries, not three new services or mandatory files. Keep applications, assessments, meaning changes, exact provenance and currentness distinct inside those boundaries.

The pure preparation function can be built against a frozen fixture. The first acceptance milestone called **runtime integration** must also demonstrate an actual permitted host capture, stale/expired refusal and Session cleanup. Snapshot progress remains useful and separately labelled.

## Changes recommended

- Replace the prescribed module tree and generalized port framework with one concrete adapter and a small preparation core. Preserve Python ownership of exact authority encoding/hashes and the isolated successor entry.
- Distinguish host-selected source members, local candidate supplements and external evidence in the captured bundle.
- Separate preparation-time readiness from a later, independently bound current-use observation.
- Specify review ingress as an ordered, independently provisioned handoff. Exact target cores must exist **before** `change.prepare`; moving candidate bodies alone is insufficient.
- Specify a retained manifest root **and every required member**, with one actual supported resolution route. A digest or locator alone cannot reconstruct a Pack.

## What remains open

| Obligation | Affects |
| --- | --- |
| Actual selected host/provider, caller permission and Session qualification | Live preparation acceptance |
| Supported provisioning/review policy, exact pre-staging core recipe and current owner/profile scope | Materialization and review qualification |
| Supported retained-member resolver and cold reconstruction | Durable Work result and subsequent Session |
| Authoritative parameter declarations and attributable handling for each selected example | Meaning/application fidelity |
| Existing semantic, representation, consumer and adoption requirements | Their original applicable effects |

These are named dependencies, not newly completed work. The [existing 79-item work map](../0006-runtime-integration-design/work-crosswalk.json) retains its identities and obligations; this reduction does not close or delete them.

## Next route

**Revise the implementation design using this repair, starting with the staged review handoff and retained-member resolution.** Keep the pure core independently implementable. Qualify each later boundary before claiming end-to-end integration. No new foundational Definition or Artifact Type is justified merely to perform this reduction.

## Evidence limits

Source inspection and design counterexamples only. No runtime experiment, test suite, private workspace access, implementation change, admission or adoption occurred. All 13 sealed original-design members are unchanged. Of its 51 external bindings, 50 still match; the execution-progress record has drifted. This critique does not claim the old snapshot is the latest Lab operational status. See [validation](validation.json).
