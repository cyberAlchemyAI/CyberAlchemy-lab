# Behavioral qualification (candidate)

`check`, `build`, and `verify` establish different source and artifact facts. None
observes a deployed or hosted runtime. Use `qualify` when a consumer proposes a
specific behavioral claim:

```bash
alchlang qualify application.alch --claim closed-state-model
alchlang qualify application.alch --claim executable-runtime
```

`closed-state-model` is a source-level, closed-world claim. It requires the
canonical `application-v1` profile, at least one declared Operation and State
Machine, an Entity write for every Operation, at least one transition per State
Machine, a subject Entity and trigger Event
for every transition, and an Operation that both writes that subject and
produces each trigger Event. It rejects compatibility transitions without
trigger Events. A positive result is `source-qualified`, with
`runtime_guarantees_observed: false`. It does not prove guards executed, Policy
targets were invoked, persistence committed, Events were delivered, or a
State Machine actually changed state.

The closed-world claim intentionally rejects transitions triggered only by an
external Event. Such an application can still be valid source and may compile;
it simply cannot claim this closed model until an explicit external-event
binding and its qualification evidence are defined. The command does not
silently invent one. It also does not turn a `declarative-function-v1` decision
into an Operation or State Machine.

`executable-runtime` currently fails with `ALCH_RUNTIME_UNOBSERVED` even after
source closure passes. A future qualification may accept exact generated
artifacts plus observed provider behavior, but a source or build receipt alone
cannot satisfy that claim. Adapter profiles such as `service-v1` and
`semantic-contract-v1` do not satisfy either claim by reusing the word
“operation” or by projecting candidate DomainSpec proxy nodes.

## Open Questions

- What exact runtime evidence and provider binding should qualify an executable
  runtime without turning compilation into an authority or deployment grant?
- How should externally triggered State Machine transitions declare source,
  custody, and event-delivery evidence?
- Should a later source-level claim include Policy dispatch and Workflow
  execution coverage, or should those remain distinct claims?

Authority effect: none. Qualification is candidate construction evidence only.
