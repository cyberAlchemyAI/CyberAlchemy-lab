# W3 effects and connections

This family implements the selected `W3-A-DESCRIPTOR-BOUND-TYPED-EFFECTS-CONNECTIONS` candidate for four DomainSpec meta-types:

- Mapping: exact source, target, direction, closed field correspondence, fallibility, effects, and reverse contract;
- Interface: exact boundary identity, version, compatibility policy, and a multi-member Operation/Query exposure set;
- Event: a typed past fact after exactly one durable checkpoint, with occurrence identity separated from publication attempts;
- Operation: declared reads, writes, external effects, outcomes, order, Rule decision use, Event emission, and continuation closure.

`contracts/w3-contracts.ts` defines the closed descriptor and observation union. `evaluator/evaluate-w3.ts` compares authored meaning with native evidence and returns `pass`, `reject`, `unsupported`, or `indeterminate`; missing support never passes. The Financial Settlement fixture binds exact current concept, decision, profile, provider, source, and observation digests.

The TypeScript provider, Python frozen-record/Protocol implementation, and Rust struct/trait implementation realize the same example. Their tests include hostile endpoint, exposure, checkpoint, exactly-once, guard, effect-order, write-restore, and continuation cases.

The software factory registers `typescript-w3-effects-connections-v1`. Its `w3-effects-connections.request.json` request locks the descriptor and observation bytes, executes them, verifies the terminal run, and replays the semantic result in another process.

This is candidate-local implementation and proof evidence. Implemented realizations, including Interface, carry candidate status. That does not promote the ontology, release code, establish production behavior, or make any realization active.
