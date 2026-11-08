# W4 orchestration and lifecycle candidate

This family proves two distinct DomainSpec architecture types against exact descriptors:

- `StateMachine` owns a closed state graph. Its transition provider is pure: it returns the next state and effect intents. A W3 `Operation` remains responsible for executing and observing those effects.
- `Workflow` owns an ordered graph of steps bound to Operations or nested Workflows. It also declares scope, terminal outcomes, failure behavior, continuation closure, and compensation.

Every implemented TypeScript, Python, and Rust form is marked `candidate`, never active. Native syntax corroborates the descriptor; it does not author DomainSpec meaning. The hostile proofs reject undeclared transitions, reversed direction, missing guards, inline effects, reordered or missing steps, false terminal outcomes, failure drift, omitted compensation, and open continuation.
