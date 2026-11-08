# Architecture foundations

## Availability closure

A generator is selectable only when all four prerequisites are `closed`:

- an admitted DomainSpec meta-type;
- an explicit integration binding;
- a registered generator;
- executable conformance evidence.

## Stability separation

`candidate` and `stable` describe architecture maturity. `available` and
`blocked` describe local generator selection. Passing tests may establish
availability evidence but cannot create stable status.

## No name inference

Pattern names, event names and adapter names never imply implementation
semantics. The language must carry an explicit construct before a generator may
consume it.
